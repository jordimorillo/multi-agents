"""
Simple example of using the Multi-Agent Workflow
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from graphs.workflow import MultiAgentWorkflow


async def main():
    """
    Simple example: Create a login form with OAuth
    
    This will:
    1. Architect analyzes the task
    2. Security reviews requirements
    3. Backend implements OAuth endpoints
    4. Frontend creates login UI
    5. QA runs tests
    6. Observer updates RAG knowledge
    
    Each agent:
    - Updates Linear issues
    - Creates GitHub branches
    - Makes commits
    - Creates pull requests
    """
    
    print("🚀 Multi-Agent System - Simple Example")
    print("="*60)
    
    # Configuration
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'linear_api_key': os.getenv('LINEAR_API_KEY'),
        'github_token': os.getenv('GITHUB_TOKEN'),
        'github_repo': os.getenv('GITHUB_REPO', 'owner/repo'),
        'model': os.getenv('DEFAULT_MODEL', 'gpt-4-turbo-preview'),
        'temperature': float(os.getenv('DEFAULT_TEMPERATURE', '0.2')),
        'project_path': os.getcwd()  # Current directory
    }
    
    # Validate config
    if not config['openai_api_key'] or config['openai_api_key'] == 'sk-your-key-here':
        print("❌ Error: Please set OPENAI_API_KEY in .env file")
        print("   Edit .env and add your OpenAI API key")
        return
    
    print(f"\n📋 Configuration:")
    print(f"  Model: {config['model']}")
    print(f"  GitHub: {config['github_repo']}")
    print(f"  Linear Team: {os.getenv('LINEAR_TEAM_ID', 'Not set')}")
    print()
    
    # Create workflow
    print("🔧 Initializing multi-agent workflow...")
    workflow = MultiAgentWorkflow(config)
    print("✅ Workflow initialized")
    print()
    
    # Execute task
    print("🚀 Starting task execution...")
    print("   Task: Create responsive login form with OAuth 2.0")
    print()
    
    try:
        final_state = await workflow.execute(
            task_description="""
            Create a responsive login form with OAuth 2.0 support.
            
            Requirements:
            - Backend: OAuth endpoints (login, callback, refresh)
            - Frontend: Login form UI with React
            - Security: CSRF protection, secure token storage
            - Testing: Unit tests + E2E tests
            - Responsive: Mobile-first design
            - Accessibility: WCAG AA compliance
            """,
            project_path=os.getcwd(),
            linear_team_id=os.getenv('LINEAR_TEAM_ID', 'TEAM-123'),
            github_repo=config['github_repo']
        )
        
        print("\n" + "="*60)
        print("✅ TASK COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Show results
        print(f"\n📊 Execution Summary:")
        print(f"  ⏱️  Duration: {final_state['execution_time_seconds']:.1f}s")
        print(f"  💰 Cost: ${final_state['total_cost_usd']:.4f}")
        print(f"  🔢 Tokens: {final_state['total_tokens_used']:,}")
        
        print(f"\n✅ Completed Agents: {len(final_state['completed_agents'])}")
        for agent in final_state['completed_agents']:
            print(f"  - {agent}")
        
        if final_state.get('github_prs'):
            print(f"\n🔀 Pull Requests Created: {len(final_state['github_prs'])}")
            for pr in final_state['github_prs']:
                print(f"  - {pr.get('agent', 'unknown')}: {pr.get('url', 'N/A')}")
        
        if final_state.get('linear_main_issue_url'):
            print(f"\n📋 Linear Issue: {final_state['linear_main_issue_url']}")
        
        print("\n🎉 All done! Check your GitHub repo for the PRs.")
        
    except Exception as e:
        print(f"\n❌ Task failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
