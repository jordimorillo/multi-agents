"""
Multi-Agent Workflow with LangGraph
Orchestrates multiple specialized agents to complete complex tasks
"""

import os
import logging
from typing import Dict, Any, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from graphs.state import AgentState, create_initial_state

# Import all 12 agents
from agents.agent_01_fullstack_architect import FullStackArchitectAgent
from agents.agent_02_frontend_specialist import FrontendSpecialistAgent
from agents.agent_03_backend_specialist import BackendSpecialistAgent
from agents.agent_04_devops_specialist import DevOpsSpecialistAgent
from agents.agent_05_security_specialist import SecuritySpecialistAgent
from agents.agent_06_performance_specialist import PerformanceSpecialistAgent
from agents.agent_07_qa_specialist import QASpecialistAgent
from agents.agent_08_seo_specialist import SEOSpecialistAgent
from agents.agent_09_ux_specialist import UXSpecialistAgent
from agents.agent_10_data_specialist import DataSpecialistAgent
from agents.agent_11_ai_specialist import AISpecialistAgent
from agents.agent_12_observer_optimizer import ObserverOptimizerAgent

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """
    LangGraph workflow that coordinates multiple agents
    
    Workflow:
    1. Architect analyzes task and creates plan
    2. Security reviews requirements
    3. Backend + Frontend work in parallel (conditional)
    4. QA runs tests
    5. Observer analyzes and updates RAG
    
    Features:
    - Conditional routing based on state
    - Parallel execution support
    - Checkpointing for resumability
    - State persistence
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.graph = None
        self.checkpointer = None
        self._init_agents()
        self._build_graph()
    
    def _init_agents(self):
        """Initialize all 12 agents"""
        logger.info("🔧 Initializing all 12 agents...")
        
        # Initialize all specialist agents
        self.architect_agent = FullStackArchitectAgent(self.config)
        self.frontend_agent = FrontendSpecialistAgent(self.config)
        self.backend_agent = BackendSpecialistAgent(self.config)
        self.devops_agent = DevOpsSpecialistAgent(self.config)
        self.security_agent = SecuritySpecialistAgent(self.config)
        self.performance_agent = PerformanceSpecialistAgent(self.config)
        self.qa_agent = QASpecialistAgent(self.config)
        self.seo_agent = SEOSpecialistAgent(self.config)
        self.ux_agent = UXSpecialistAgent(self.config)
        self.data_agent = DataSpecialistAgent(self.config)
        self.ai_agent = AISpecialistAgent(self.config)
        self.observer_agent = ObserverOptimizerAgent(self.config)
        
        logger.info("✅ All 12 agents initialized successfully")
    
    def _build_graph(self):
        """
        Build DYNAMIC workflow - Architect decides who runs each iteration
        
        Flow:
        1. Start → Architect (analyzes task)
        2. Architect → Route (decides which agents to activate)
        3. Execute agents in parallel
        4. Check completion → Back to Architect OR End
        """
        logger.info("🔧 Building dynamic workflow graph...")
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add all agent nodes
        workflow.add_node("start", self._start_node)
        workflow.add_node("architect", self.architect_agent.execute)
        workflow.add_node("router", self._router_node)  # Dynamic routing node
        
        # Add all specialist agents
        workflow.add_node("frontend", self.frontend_agent.execute)
        workflow.add_node("backend", self.backend_agent.execute)
        workflow.add_node("devops", self.devops_agent.execute)
        workflow.add_node("security", self.security_agent.execute)
        workflow.add_node("performance", self.performance_agent.execute)
        workflow.add_node("qa", self.qa_agent.execute)
        workflow.add_node("seo", self.seo_agent.execute)
        workflow.add_node("ux", self.ux_agent.execute)
        workflow.add_node("data", self.data_agent.execute)
        workflow.add_node("ai", self.ai_agent.execute)
        workflow.add_node("observer", self.observer_agent.execute)
        
        # Initial flow
        workflow.set_entry_point("start")
        workflow.add_edge("start", "architect")
        workflow.add_edge("architect", "router")
        
        # Router decides which agents to execute
        workflow.add_conditional_edges(
            "router",
            self._route_to_agents,
            {
                "frontend": "frontend",
                "backend": "backend",
                "devops": "devops",
                "security": "security",
                "performance": "performance",
                "qa": "qa",
                "seo": "seo",
                "ux": "ux",
                "data": "data",
                "ai": "ai",
                "observer": "observer",
                "end": END
            }
        )
        
        # All agents return to router to check next step
        for agent in ["frontend", "backend", "devops", "security", "performance", 
                      "qa", "seo", "ux", "data", "ai"]:
            workflow.add_edge(agent, "router")
        
        # Observer ends the workflow (final analysis)
        workflow.add_edge("observer", END)
        
        # Compile
        self.graph = workflow.compile()
        
        logger.info("✅ Dynamic workflow graph built")
    
    # ═══════════════════════════════════════════════════════════
    # NODE FUNCTIONS
    # ═══════════════════════════════════════════════════════════
    
    async def _start_node(self, state: AgentState) -> AgentState:
        """
        Initial node - setup Linear issues and prepare state
        
        This node:
        - Creates main Linear issue
        - Creates sub-issues for each agent
        - Initializes workflow metadata
        """
        print("\n" + "=" * 80)
        print("🎬 INICIANDO ANÁLISIS")
        print("=" * 80)
        print(f"📝 Tarea: {state['task_description']}")
        print()
        
        state['messages'].append("📋 Sistema multi-agente inicializado")
        state['messages'].append(f"🎯 Tarea: {state['task_description'][:100]}...")
        state['iteration'] = 0
        state['next_agents'] = []  # Agents to execute in next iteration
        
        return state
    
    async def _router_node(self, state: AgentState) -> AgentState:
        """
        Router node - reads architect's decision and updates routing
        
        The Architect agent sets state['next_agents'] with list of agent IDs
        to execute in this iteration
        """
        state['iteration'] = state.get('iteration', 0) + 1
        
        print("\n" + "=" * 80)
        print(f"🔄 ITERACIÓN {state['iteration']}")
        print("=" * 80)
        
        # Check if task is complete
        if state.get('task_complete'):
            print("✅ Arquitecto ha marcado la tarea como COMPLETADA")
            print("📊 Procediendo al análisis final...")
            state['next_agents'] = ['observer']  # Final step
            return state
        
        # Get next agents from architect's decision
        next_agents = state.get('next_agents', [])
        
        if not next_agents:
            # No more agents to execute, go to observer
            print("📊 No hay más agentes programados")
            print("🔍 Moviendo al Observer para análisis final...")
            state['next_agents'] = ['observer']
        else:
            # Map agent IDs to friendly names
            agent_names = {
                'frontend': '💻 Frontend',
                'backend': '🔧 Backend',
                'devops': '🚀 DevOps',
                'security': '🔒 Seguridad',
                'performance': '⚡ Performance',
                'qa': '✅ QA',
                'seo': '📈 SEO',
                'ux': '🎨 UX',
                'data': '📊 Datos',
                'ai': '🤖 IA'
            }
            
            agent_list = [agent_names.get(a, a) for a in next_agents]
            print(f"🎯 Agentes programados para esta iteración:")
            for agent in agent_list:
                print(f"   {agent}")
            print()
        
        return state
    
    # ═══════════════════════════════════════════════════════════
    # CONDITIONAL ROUTING FUNCTIONS
    # ═══════════════════════════════════════════════════════════
    
    def _route_to_agents(self, state: AgentState) -> str:
        """
        Dynamic routing based on Architect's decisions
        
        The Architect sets state['next_agents'] with the list of agent IDs.
        This function pops the next agent from the queue.
        
        Returns:
            Agent ID to execute next, or 'end' if done
        """
        next_agents = state.get('next_agents', [])
        
        if not next_agents:
            return "end"
        
        # Pop the first agent from the queue
        next_agent = next_agents.pop(0)
        state['next_agents'] = next_agents
        
        # Map agent IDs to node names
        agent_map = {
            'agent-02-frontend-specialist': 'frontend',
            'agent-03-backend-specialist': 'backend',
            'agent-04-devops-specialist': 'devops',
            'agent-05-security-specialist': 'security',
            'agent-06-performance-specialist': 'performance',
            'agent-07-qa-specialist': 'qa',
            'agent-08-seo-specialist': 'seo',
            'agent-09-ux-specialist': 'ux',
            'agent-10-data-specialist': 'data',
            'agent-11-ai-specialist': 'ai',
            'agent-12-observer-optimizer': 'observer',
            # Short names as well
            'frontend': 'frontend',
            'backend': 'backend',
            'devops': 'devops',
            'security': 'security',
            'performance': 'performance',
            'qa': 'qa',
            'seo': 'seo',
            'ux': 'ux',
            'data': 'data',
            'ai': 'ai',
            'observer': 'observer'
        }
        
        return agent_map.get(next_agent, 'end')
        
        return state
    
    # ═══════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════
    
    async def execute(
        self,
        task_description: str,
        project_path: str,
        linear_team_id: str,
        github_repo: str,
        task_id: str = None
    ) -> AgentState:
        """
        Execute the multi-agent workflow
        
        Args:
            task_description: What needs to be done
            project_path: Path to the project
            linear_team_id: Linear team ID
            github_repo: GitHub repo (owner/repo)
            task_id: Optional task ID for resuming
        
        Returns:
            Final state with all results
        """
        logger.info(f"🚀 Executing workflow: {task_description[:50]}...")
        
        # Create initial state
        initial_state = create_initial_state(
            task_description=task_description,
            project_path=project_path,
            linear_team_id=linear_team_id,
            github_repo=github_repo,
            task_id=task_id
        )
        
        # Config for checkpointing
        # SIN LÍMITE de recursión - el workflow debe poder iterar libremente
        config = {
            "configurable": {
                "thread_id": initial_state["task_id"]
            },
            "recursion_limit": 1000  # Límite muy alto para permitir iteraciones extensas
        }
        
        # Execute graph
        try:
            final_state = await self.graph.ainvoke(initial_state, config)
            
            logger.info("✅ Workflow completed successfully")
            self._print_summary(final_state)
            
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            raise
    
    async def resume(self, task_id: str) -> AgentState:
        """
        Resume a workflow from checkpoint
        
        Args:
            task_id: Task ID to resume
        
        Returns:
            Final state
        """
        logger.info(f"🔄 Resuming workflow: {task_id}")
        
        config = {
            "configurable": {"thread_id": task_id},
            "recursion_limit": 1000  # Límite muy alto para permitir iteraciones extensas
        }
        
        # Resume from checkpoint
        final_state = await self.graph.ainvoke(None, config)
        
        return final_state
    
    def _print_summary(self, state: AgentState):
        """Print execution summary"""
        print("\n" + "="*70)
        print("MULTI-AGENT WORKFLOW SUMMARY")
        print("="*70)
        
        print(f"\n📋 Task: {state['task_description'][:60]}...")
        print(f"⏱️  Duration: {state['execution_time_seconds']:.1f}s")
        print(f"💰 Cost: ${state['total_cost_usd']:.4f}")
        print(f"🔢 Tokens: {state['total_tokens_used']:,}")
        
        print(f"\n✅ Completed Agents ({len(state['completed_agents'])}):")
        for agent in state['completed_agents']:
            print(f"  - {agent}")
        
        if state.get('failed_agents'):
            print(f"\n❌ Failed Agents ({len(state['failed_agents'])}):")
            for agent in state['failed_agents']:
                print(f"  - {agent}")
        
        if state.get('github_prs'):
            print(f"\n🔀 Pull Requests ({len(state['github_prs'])}):")
            for pr in state['github_prs']:
                print(f"  - {pr.get('url', 'N/A')}")
        
        print("\n📝 Messages:")
        for msg in state['messages'][-10:]:  # Last 10
            print(f"  {msg}")
        
        print("\n" + "="*70)


# ═══════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════

async def main():
    """Example usage of the multi-agent workflow"""
    
    # Configuration
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'linear_api_key': os.getenv('LINEAR_API_KEY'),
        'github_token': os.getenv('GITHUB_TOKEN'),
        'github_repo': 'owner/repo',
        'model': 'gpt-4-turbo-preview',
        'temperature': 0.2
    }
    
    # Create workflow
    workflow = MultiAgentWorkflow(config)
    
    # Execute task
    final_state = await workflow.execute(
        task_description="Create a responsive login form with OAuth 2.0 support",
        project_path="/home/jordi/test-project",
        linear_team_id="TEAM-123",
        github_repo="owner/repo"
    )
    
    print("\n✅ Workflow completed!")
    print(f"Final state has {len(final_state['completed_agents'])} completed agents")


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
