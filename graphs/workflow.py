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
        """Build the LangGraph workflow"""
        logger.info("🔧 Building workflow graph...")
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (real agent execute methods)
        workflow.add_node("start", self._start_node)
        workflow.add_node("architect", self.architect_agent.execute)
        workflow.add_node("security", self.security_agent.execute)
        workflow.add_node("backend", self.backend_agent.execute)
        workflow.add_node("frontend", self.frontend_agent.execute)
        workflow.add_node("qa", self.qa_agent.execute)
        workflow.add_node("observer", self.observer_agent.execute)
        
        # Define edges (workflow)
        workflow.set_entry_point("start")
        workflow.add_edge("start", "architect")
        workflow.add_edge("architect", "security")
        
        # Conditional: Security approval
        workflow.add_conditional_edges(
            "security",
            self._should_continue_after_security,
            {
                "approved": "backend",
                "rejected": END,
                "needs_revision": "architect"
            }
        )
        
        # Parallel execution: Backend + Frontend
        workflow.add_edge("backend", "frontend")
        
        # Conditional: Check if both completed
        workflow.add_conditional_edges(
            "frontend",
            self._should_run_qa,
            {
                "run_qa": "qa",
                "skip_qa": "observer"
            }
        )
        
        workflow.add_edge("qa", "observer")
        workflow.add_edge("observer", END)
        
        # Compile WITHOUT checkpointing for now (async compatibility issue)
        # TODO: Use AsyncSqliteSaver when available or implement custom checkpointer
        # self.checkpointer = SqliteSaver.from_conn_string(":memory:")
        # self.graph = workflow.compile(checkpointer=self.checkpointer)
        self.graph = workflow.compile()
        
        logger.info("✅ Workflow graph built")
    
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
        logger.info("🚀 Starting multi-agent workflow...")
        
        # TODO: Create Linear main issue
        # TODO: Create sub-issues for each agent that will be activated
        
        state['messages'].append("📋 Workflow initialized with 12 specialized agents")
        state['messages'].append(f"🎯 Task: {state['task_description'][:100]}...")
        
        return state
    
    # ═══════════════════════════════════════════════════════════
    # CONDITIONAL ROUTING FUNCTIONS
    # ═══════════════════════════════════════════════════════════
    
    def _should_continue_after_security(
        self,
        state: AgentState
    ) -> Literal["approved", "rejected", "needs_revision"]:
        """Decide what to do after security review"""
        
        if state.get('security_approved'):
            return "approved"
        
        security_result = state.get('agent_results', {}).get('security', {})
        vulnerabilities = security_result.get('vulnerabilities', [])
        
        if any(v.get('severity') == 'critical' for v in vulnerabilities):
            return "rejected"
        
        return "needs_revision"
    
    def _should_run_qa(
        self,
        state: AgentState
    ) -> Literal["run_qa", "skip_qa"]:
        """Decide if QA should run"""
        
        if not state.get('requires_testing', True):
            return "skip_qa"
        
        # Check if both backend and frontend completed
        completed = set(state.get('completed_agents', []))
        if 'backend' in completed and 'frontend' in completed:
            return "run_qa"
        
        return "skip_qa"
    
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
