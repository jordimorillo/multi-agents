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
from agents.agent_02_frontend_specialist import FrontendSpecialistAgent

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
        """Initialize all agents"""
        logger.info("🔧 Initializing agents...")
        
        # TODO: Initialize all agents
        # For now, just frontend as example
        self.frontend_agent = FrontendSpecialistAgent(self.config)
        
        # TODO: Add other agents
        # self.architect_agent = ArchitectAgent(self.config)
        # self.backend_agent = BackendAgent(self.config)
        # etc...
        
        logger.info("✅ Agents initialized")
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        logger.info("🔧 Building workflow graph...")
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("start", self._start_node)
        workflow.add_node("architect", self._architect_node)
        workflow.add_node("security", self._security_node)
        workflow.add_node("backend", self._backend_node)
        workflow.add_node("frontend", self.frontend_agent.execute)  # Real agent!
        workflow.add_node("qa", self._qa_node)
        workflow.add_node("observer", self._observer_node)
        
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
    # NODE FUNCTIONS (Placeholders - to be replaced with real agents)
    # ═══════════════════════════════════════════════════════════
    
    async def _start_node(self, state: AgentState) -> AgentState:
        """Initial node - setup Linear issues"""
        logger.info("🚀 Starting workflow...")
        
        # TODO: Create Linear main issue
        # TODO: Create sub-issues for each agent
        
        state['messages'].append("📋 Workflow initialized")
        return state
    
    async def _architect_node(self, state: AgentState) -> AgentState:
        """Architect analyzes and plans"""
        logger.info("🏗️  Architect analyzing task...")
        
        # Placeholder - would be real ArchitectAgent
        state['agent_results']['architect'] = {
            'summary': 'Task analyzed. Requires frontend + backend work.',
            'complexity': 'moderate',
            'estimated_time': '2 hours'
        }
        state['completed_agents'].append('architect')
        state['messages'].append("✅ Architect completed analysis")
        
        # Set routing flags
        state['requires_testing'] = True
        state['requires_devops'] = False
        
        return state
    
    async def _security_node(self, state: AgentState) -> AgentState:
        """Security reviews requirements"""
        logger.info("🛡️  Security reviewing...")
        
        # Placeholder
        state['agent_results']['security'] = {
            'summary': 'Security review passed. No critical issues.',
            'vulnerabilities': [],
            'approved': True
        }
        state['completed_agents'].append('security')
        state['security_approved'] = True
        state['messages'].append("✅ Security approved")
        
        return state
    
    async def _backend_node(self, state: AgentState) -> AgentState:
        """Backend implementation"""
        logger.info("🔧 Backend working...")
        
        # Placeholder - would be real BackendAgent
        state['agent_results']['backend'] = {
            'summary': 'Backend API endpoints implemented',
            'files_created': ['src/api/auth.py', 'src/api/users.py'],
            'tests': 'Unit tests included'
        }
        state['completed_agents'].append('backend')
        state['messages'].append("✅ Backend completed")
        
        return state
    
    async def _qa_node(self, state: AgentState) -> AgentState:
        """QA testing"""
        logger.info("✅ QA testing...")
        
        # Placeholder
        state['agent_results']['qa'] = {
            'summary': 'All tests passed',
            'test_results': {
                'unit': 'pass',
                'integration': 'pass',
                'e2e': 'pass'
            }
        }
        state['completed_agents'].append('qa')
        state['messages'].append("✅ QA tests passed")
        
        return state
    
    async def _observer_node(self, state: AgentState) -> AgentState:
        """Observer analyzes and updates RAG"""
        logger.info("🔍 Observer analyzing intervention...")
        
        # TODO: Extract patterns and update RAG
        
        state['agent_results']['observer'] = {
            'summary': 'Intervention analyzed. RAG updated.',
            'patterns_extracted': 2,
            'quality_score': 8.5
        }
        state['completed_agents'].append('observer')
        state['messages'].append("✅ Observer completed")
        
        # Calculate final metrics
        state['execution_time_seconds'] = (
            datetime.now() - datetime.fromisoformat(state['started_at'])
        ).total_seconds()
        
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
        config = {
            "configurable": {
                "thread_id": initial_state["task_id"]
            }
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
        
        config = {"configurable": {"thread_id": task_id}}
        
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
