"""
Shared State Definition for LangGraph Multi-Agent System
"""

from typing import TypedDict, Annotated, List, Dict, Any
from operator import add
from datetime import datetime


class AgentState(TypedDict):
    """
    Estado compartido entre todos los agentes en el grafo LangGraph
    
    Este estado se pasa entre agentes y cada agente puede:
    - Leer cualquier campo
    - Actualizar campos específicos
    - Acumular resultados en listas/dicts con Annotated[..., add]
    """
    
    # ═══════════════════════════════════════════════════════════
    # TASK INFORMATION
    # ═══════════════════════════════════════════════════════════
    task_id: str
    task_description: str
    task_title: str
    project_path: str
    complexity: str  # 'simple', 'moderate', 'complex'
    
    # ═══════════════════════════════════════════════════════════
    # LINEAR INTEGRATION
    # ═══════════════════════════════════════════════════════════
    linear_main_issue_id: str
    linear_main_issue_url: str
    linear_team_id: str
    linear_sub_issues: Dict[str, str]  # agent_id -> issue_id
    
    # ═══════════════════════════════════════════════════════════
    # GITHUB INTEGRATION
    # ═══════════════════════════════════════════════════════════
    github_repo: str
    github_base_branch: str
    github_agent_branches: Dict[str, str]  # agent_id -> branch_name
    github_prs: Annotated[List[Dict[str, str]], add]  # List of PRs created
    
    # ═══════════════════════════════════════════════════════════
    # AGENT COORDINATION
    # ═══════════════════════════════════════════════════════════
    agent_results: Dict[str, Any]  # agent_id -> result (not accumulated, just updated)
    completed_agents: Annotated[List[str], add]  # List of completed agent IDs
    failed_agents: Annotated[List[str], add]  # List of failed agent IDs
    blocked_agents: List[str]  # Agents waiting for dependencies
    
    # ═══════════════════════════════════════════════════════════
    # EXECUTION METADATA
    # ═══════════════════════════════════════════════════════════
    started_at: str  # ISO timestamp
    updated_at: str  # ISO timestamp
    messages: Annotated[List[str], add]  # Log messages
    
    # ═══════════════════════════════════════════════════════════
    # METRICS
    # ═══════════════════════════════════════════════════════════
    total_tokens_used: Annotated[int, add]
    total_cost_usd: Annotated[float, add]
    execution_time_seconds: float
    
    # ═══════════════════════════════════════════════════════════
    # CONDITIONAL ROUTING
    # ═══════════════════════════════════════════════════════════
    security_approved: bool  # Si security aprueba, continuar
    needs_human_review: bool  # Si requiere revisión humana
    requires_devops: bool  # Si necesita deployment
    requires_testing: bool  # Si necesita QA
    next_agent: str  # Next agent to route to (for dynamic routing)


class AgentResult(TypedDict):
    """Resultado de la ejecución de un agente"""
    agent_id: str
    agent_name: str
    success: bool
    summary: str
    
    # Code changes
    files_modified: List[str]
    files_created: List[str]
    files_deleted: List[str]
    
    # GitHub
    branch_name: str
    pr_url: str
    commits: List[str]
    
    # Linear
    issue_id: str
    issue_updated: bool
    
    # Metrics
    tokens_used: int
    cost_usd: float
    execution_time: float
    
    # Errors
    error_message: str
    needs_retry: bool


def create_initial_state(
    task_description: str,
    project_path: str,
    linear_team_id: str,
    github_repo: str,
    task_id: str = None
) -> AgentState:
    """
    Crear estado inicial para una nueva tarea
    
    Args:
        task_description: Descripción de la tarea
        project_path: Path del proyecto
        linear_team_id: ID del team en Linear
        github_repo: Repositorio GitHub (owner/repo)
        task_id: ID opcional de la tarea
    
    Returns:
        AgentState inicializado
    """
    import uuid
    
    if not task_id:
        task_id = str(uuid.uuid4())
    
    now = datetime.now().isoformat()
    
    return AgentState(
        # Task info
        task_id=task_id,
        task_description=task_description,
        task_title=task_description[:100],  # Truncate for title
        project_path=project_path,
        complexity='moderate',
        
        # Linear
        linear_main_issue_id='',
        linear_main_issue_url='',
        linear_team_id=linear_team_id,
        linear_sub_issues={},
        
        # GitHub
        github_repo=github_repo,
        github_base_branch='main',
        github_agent_branches={},
        github_prs=[],
        
        # Coordination
        agent_results={},
        completed_agents=[],
        failed_agents=[],
        blocked_agents=[],
        
        # Metadata
        started_at=now,
        updated_at=now,
        messages=[f"Task created: {task_description[:50]}..."],
        
        # Metrics
        total_tokens_used=0,
        total_cost_usd=0.0,
        execution_time_seconds=0.0,
        
        # Routing flags
        security_approved=False,
        needs_human_review=False,
        requires_devops=False,
        requires_testing=True,
        next_agent=''
    )


def update_state_with_result(
    state: AgentState,
    result: AgentResult
) -> AgentState:
    """
    Actualizar estado con el resultado de un agente
    
    Args:
        state: Estado actual
        result: Resultado del agente
    
    Returns:
        Estado actualizado
    """
    # Update results
    state['agent_results'][result['agent_id']] = result
    
    # Update completed/failed
    if result['success']:
        if result['agent_id'] not in state['completed_agents']:
            state['completed_agents'].append(result['agent_id'])
    else:
        if result['agent_id'] not in state['failed_agents']:
            state['failed_agents'].append(result['agent_id'])
    
    # Update GitHub PRs
    if result.get('pr_url'):
        state['github_prs'].append({
            'agent': result['agent_id'],
            'url': result['pr_url'],
            'branch': result['branch_name']
        })
    
    # Update metrics
    state['total_tokens_used'] += result.get('tokens_used', 0)
    state['total_cost_usd'] += result.get('cost_usd', 0.0)
    
    # Update timestamp
    state['updated_at'] = datetime.now().isoformat()
    
    # Add message
    if result['success']:
        state['messages'].append(f"✅ {result['agent_name']} completed")
    else:
        state['messages'].append(
            f"❌ {result['agent_name']} failed: {result.get('error_message', 'Unknown')}"
        )
    
    return state


def get_pending_agents(state: AgentState, all_agents: List[str]) -> List[str]:
    """
    Obtener lista de agentes pendientes de ejecución
    
    Args:
        state: Estado actual
        all_agents: Lista de todos los agent IDs
    
    Returns:
        Lista de agent IDs pendientes
    """
    completed = set(state['completed_agents'])
    failed = set(state['failed_agents'])
    blocked = set(state['blocked_agents'])
    
    pending = [
        agent for agent in all_agents
        if agent not in completed and agent not in failed and agent not in blocked
    ]
    
    return pending


def is_task_complete(state: AgentState, required_agents: List[str]) -> bool:
    """
    Verificar si la tarea está completa
    
    Args:
        state: Estado actual
        required_agents: Lista de agentes requeridos
    
    Returns:
        True si todos los agentes requeridos completaron
    """
    completed = set(state['completed_agents'])
    required = set(required_agents)
    
    return required.issubset(completed)


def calculate_execution_time(state: AgentState) -> float:
    """
    Calcular tiempo total de ejecución
    
    Args:
        state: Estado actual
    
    Returns:
        Tiempo en segundos
    """
    from datetime import datetime
    
    started = datetime.fromisoformat(state['started_at'])
    updated = datetime.fromisoformat(state['updated_at'])
    
    return (updated - started).total_seconds()
