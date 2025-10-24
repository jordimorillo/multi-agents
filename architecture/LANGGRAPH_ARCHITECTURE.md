# Arquitectura Multi-Agente con LangChain + LangGraph

## 🎯 Por qué LangChain + LangGraph

### LangChain
- **Abstracción de LLMs**: Soporte unificado para OpenAI, Anthropic, etc.
- **Chains y Tools**: Composición modular de funcionalidades
- **Memory**: Gestión de contexto y historial
- **Callbacks**: Tracking de tokens, costos, latencia

### LangGraph
- **State Management**: Estado compartido entre agentes
- **Graph-based Workflows**: Define flujos complejos con dependencias
- **Conditional Edges**: Routing inteligente entre agentes
- **Checkpointing**: Persistencia de estado para recuperación
- **Human-in-the-loop**: Aprobaciones y feedback

## 🏗️ Arquitectura Revisada con LangGraph

```
┌─────────────────────────────────────────────────────────┐
│              LANGGRAPH ORCHESTRATOR                     │
│  - Define el grafo de agentes y dependencias           │
│  - Gestiona estado compartido                          │
│  - Coordina flujo entre agentes                        │
│  - Checkpoints para recuperación                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │   SHARED STATE GRAPH       │
        │  - Task context            │
        │  - Linear issues           │
        │  - GitHub branches         │
        │  - Dependencies resolved   │
        └────────────────────────────┘
                     │
        ┌────────────┴───────────┐
        │                        │
        ↓                        ↓
┌──────────────┐         ┌──────────────┐
│ AGENT NODE   │         │ AGENT NODE   │
│  - LangChain │         │  - LangChain │
│  - Tools     │         │  - Tools     │
│  - RAG       │         │  - RAG       │
└──────────────┘         └──────────────┘
```

## 📦 Stack Tecnológico Actualizado

```python
# Core LangChain/LangGraph
langchain==0.1.0
langchain-openai==0.0.5
langchain-anthropic==0.0.5
langgraph==0.0.20
langsmith==0.0.77  # Para tracing y monitoring

# Vector stores para RAG
chromadb==0.4.22
faiss-cpu==1.7.4

# Integrations (ya las tenemos)
PyGithub==2.1.1
redis==5.0.1
fastapi==0.104.1
```

## 🔧 Componentes Principales

### 1. State Definition (Shared State)

```python
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph
from operator import add

class AgentState(TypedDict):
    """Estado compartido entre todos los agentes"""
    # Task info
    task_id: str
    task_description: str
    project_path: str
    
    # Linear
    linear_main_issue_id: str
    linear_team_id: str
    linear_sub_issues: dict  # agent_id -> issue_id
    
    # GitHub
    github_repo: str
    github_base_branch: str
    github_agent_branches: dict  # agent_id -> branch_name
    github_prs: List[str]  # URLs of created PRs
    
    # Agent outputs
    agent_results: Annotated[dict, add]  # Accumulate results
    
    # Dependencies
    completed_agents: Annotated[List[str], add]
    blocked_agents: List[str]
    
    # Metadata
    started_at: str
    messages: Annotated[List[str], add]  # Log messages
```

### 2. Agent as LangChain Tool Node

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class LangGraphAgent:
    """
    Agent implementado con LangChain que funciona como nodo en LangGraph
    """
    
    def __init__(self, agent_id: str, config: dict):
        self.agent_id = agent_id
        self.config = config
        
        # LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.2
        )
        
        # Tools que el agente puede usar
        self.tools = self._create_tools()
        
        # Prompt especializado
        self.prompt = self._create_prompt()
        
        # Agent executor
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Crear tools específicas del agente"""
        return [
            Tool(
                name="read_file",
                func=self._read_file,
                description="Read a file from the project"
            ),
            Tool(
                name="write_file",
                func=self._write_file,
                description="Write content to a file"
            ),
            Tool(
                name="search_rag",
                func=self._search_rag,
                description="Search RAG knowledge base for patterns"
            ),
            Tool(
                name="run_tests",
                func=self._run_tests,
                description="Run tests to validate implementation"
            )
        ]
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Crear prompt especializado"""
        return ChatPromptTemplate.from_messages([
            ("system", f"""You are {self.config['name']}, {self.config['role']}.

Specialization: {self.config['specialization']}
Experience: {self.config['experience']}

Your task is to implement solutions following best practices and patterns 
from your RAG knowledge base.

Always:
1. Search RAG for relevant patterns
2. Implement with high quality code
3. Include tests
4. Document your changes
"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute agent task - this is the node function in LangGraph
        """
        try:
            # Construir input desde el state
            input_text = f"""
Task: {state['task_description']}
Project: {state['project_path']}

Previous agent results:
{json.dumps(state.get('agent_results', {}), indent=2)}

Implement your part of the solution.
"""
            
            # Ejecutar agent
            result = await self.executor.ainvoke({
                "input": input_text
            })
            
            # Actualizar state
            state['agent_results'][self.agent_id] = result['output']
            state['completed_agents'].append(self.agent_id)
            state['messages'].append(f"✅ {self.agent_id} completed")
            
            # Actualizar Linear
            if state.get('linear_sub_issues', {}).get(self.agent_id):
                await self._update_linear(
                    state['linear_sub_issues'][self.agent_id],
                    result['output']
                )
            
            # Push to GitHub
            if self._has_code_changes(result):
                pr_url = await self._push_to_github(state, result)
                state['github_prs'].append(pr_url)
            
            return state
            
        except Exception as e:
            state['messages'].append(f"❌ {self.agent_id} failed: {e}")
            raise
    
    def _read_file(self, path: str) -> str:
        """Tool: read file"""
        with open(path, 'r') as f:
            return f.read()
    
    def _write_file(self, path: str, content: str) -> str:
        """Tool: write file"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Written to {path}"
    
    def _search_rag(self, query: str) -> str:
        """Tool: search RAG knowledge"""
        # Implementar búsqueda en RAG (vector store)
        return "RAG results..."
    
    def _run_tests(self, test_path: str) -> str:
        """Tool: run tests"""
        # Ejecutar tests
        return "Tests passed"
```

### 3. LangGraph Workflow Definition

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

def create_multi_agent_graph() -> StateGraph:
    """
    Crear el grafo de agentes con LangGraph
    
    Flujo:
    1. Architect analiza y planifica
    2. Security revisa requisitos
    3. Backend + Frontend en paralelo
    4. QA tests
    5. Observer analiza
    """
    
    # Inicializar agentes
    architect = LangGraphAgent('agent-01-architect', config)
    security = LangGraphAgent('agent-05-security', config)
    backend = LangGraphAgent('agent-03-backend', config)
    frontend = LangGraphAgent('agent-02-frontend', config)
    qa = LangGraphAgent('agent-07-qa', config)
    observer = LangGraphAgent('agent-12-observer', config)
    
    # Crear grafo
    workflow = StateGraph(AgentState)
    
    # Añadir nodos
    workflow.add_node("architect", architect.execute)
    workflow.add_node("security", security.execute)
    workflow.add_node("backend", backend.execute)
    workflow.add_node("frontend", frontend.execute)
    workflow.add_node("qa", qa.execute)
    workflow.add_node("observer", observer.execute)
    
    # Definir edges (flujo)
    workflow.set_entry_point("architect")
    
    workflow.add_edge("architect", "security")
    
    # Conditional edge: si security aprueba, continuar
    def should_continue_after_security(state: AgentState) -> str:
        if "security_approved" in state.get('agent_results', {}).get('agent-05-security', ''):
            return "parallel"
        return "architect"  # Volver a arquitecto si hay problemas
    
    workflow.add_conditional_edges(
        "security",
        should_continue_after_security,
        {
            "parallel": "backend",
            "architect": "architect"
        }
    )
    
    # Backend y Frontend en paralelo (LangGraph maneja esto automáticamente)
    workflow.add_edge("backend", "qa")
    workflow.add_edge("frontend", "qa")
    
    # QA al final
    workflow.add_edge("qa", "observer")
    
    # Observer finaliza
    workflow.add_edge("observer", END)
    
    # Compilar con checkpointing
    memory = SqliteSaver.from_conn_string("checkpoints.db")
    graph = workflow.compile(checkpointer=memory)
    
    return graph


# Uso del grafo
async def execute_task(task_description: str, project_path: str):
    """Ejecutar tarea en el multi-agent graph"""
    
    # Crear grafo
    graph = create_multi_agent_graph()
    
    # Estado inicial
    initial_state: AgentState = {
        "task_id": str(uuid.uuid4()),
        "task_description": task_description,
        "project_path": project_path,
        "linear_main_issue_id": "",
        "linear_team_id": "TEAM-123",
        "linear_sub_issues": {},
        "github_repo": "owner/repo",
        "github_base_branch": "main",
        "github_agent_branches": {},
        "github_prs": [],
        "agent_results": {},
        "completed_agents": [],
        "blocked_agents": [],
        "started_at": datetime.now().isoformat(),
        "messages": []
    }
    
    # Ejecutar grafo
    config = {"configurable": {"thread_id": initial_state["task_id"]}}
    
    final_state = await graph.ainvoke(initial_state, config)
    
    return final_state
```

### 4. Advanced: Parallel Execution

```python
from langgraph.pregel import Channel

def create_parallel_workflow() -> StateGraph:
    """
    Workflow con ejecución paralela real de agentes
    """
    workflow = StateGraph(AgentState)
    
    # ... añadir nodos ...
    
    # Ejecutar backend y frontend en paralelo
    workflow.add_edge("security", "parallel_start")
    
    # Fan-out
    workflow.add_edge("parallel_start", "backend")
    workflow.add_edge("parallel_start", "frontend")
    
    # Fan-in: esperar ambos
    def wait_for_both(state: AgentState) -> str:
        completed = state.get('completed_agents', [])
        if 'agent-03-backend' in completed and 'agent-02-frontend' in completed:
            return "qa"
        return "wait"
    
    workflow.add_conditional_edges(
        "backend",
        wait_for_both,
        {"qa": "qa", "wait": "parallel_end"}
    )
    
    workflow.add_conditional_edges(
        "frontend",
        wait_for_both,
        {"qa": "qa", "wait": "parallel_end"}
    )
    
    return workflow.compile()
```

## 🎯 Ventajas de esta Arquitectura

### 1. **Observabilidad Total**
```python
from langsmith import Client

# Cada ejecución se trackea automáticamente
client = Client()
# Ver en LangSmith UI: latencia, tokens, costos, errores
```

### 2. **Checkpointing Automático**
```python
# Si falla un agente, reanudar desde ahí
graph = workflow.compile(checkpointer=SqliteSaver(...))

# Reanudar desde checkpoint
state = await graph.ainvoke(
    None,  # No initial state
    config={"configurable": {"thread_id": "task-123"}}
)
```

### 3. **Human-in-the-loop**
```python
from langgraph.prebuilt import create_react_agent

# Interrumpir para aprobación humana
workflow.add_node("human_approval", human_approval_node)

def human_approval_node(state: AgentState) -> AgentState:
    # Esperar aprobación antes de deploy
    approval = interrupt("Do you approve this PR?")
    if not approval:
        state['messages'].append("❌ Human rejected")
        return state
    return state
```

### 4. **Testing Simplificado**
```python
# Test individual de agentes
agent = LangGraphAgent('test-agent', config)
result = await agent.execute(mock_state)

# Test del grafo completo
graph = create_multi_agent_graph()
final_state = await graph.ainvoke(test_state)
assert 'agent-02-frontend' in final_state['completed_agents']
```

## 🚀 Ventajas vs Redis Streams

| Feature | Redis Streams | LangGraph |
|---------|--------------|-----------|
| **State Management** | Manual | Built-in |
| **Checkpointing** | Custom | Automatic |
| **Observability** | Custom logging | LangSmith UI |
| **Parallel execution** | Manual coordination | Native support |
| **Conditional routing** | Complex logic | Simple decorators |
| **Testing** | Integration tests only | Unit + Integration |
| **Human-in-loop** | Complex | Built-in |
| **Cost tracking** | Manual | Automatic |

## 📊 Estructura de Proyecto Actualizada

```
multi-agents/
├── agents/
│   ├── base/
│   │   ├── langgraph_agent.py      # Base agent con LangChain
│   │   ├── tools.py                 # Shared tools
│   │   └── rag_store.py             # RAG vector store
│   ├── agent_01_architect.py
│   ├── agent_02_frontend.py
│   └── ...
├── graphs/
│   ├── workflows.py                 # Graph definitions
│   ├── state.py                     # State schemas
│   └── conditions.py                # Conditional routing
├── integrations/
│   ├── linear/
│   ├── github/
│   └── langsmith/                   # LangSmith tracking
├── orchestrator/
│   ├── api.py                       # FastAPI endpoints
│   └── executor.py                  # Graph executor
└── tests/
    ├── test_agents.py
    └── test_workflows.py
```

## 🎯 Próximo Paso

¿Quieres que implemente:
1. ✅ **Agente base con LangChain + tools**
2. ✅ **Definición del grafo LangGraph completo**
3. ✅ **Ejemplo end-to-end funcionando**
4. ✅ **RAG con vector store (ChromaDB/FAISS)**
5. ✅ **Dashboard con LangSmith**

Todo esto es **mucho más simple y robusto** que la arquitectura manual con Redis!
