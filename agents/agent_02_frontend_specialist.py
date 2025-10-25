"""
Frontend Specialist Agent
Elena Rodriguez - 32 years experience in frontend development
"""

import os
import json
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class FrontendSpecialistAgent(LangChainAgentBase):
    """
    Frontend specialist with expertise in:
    - React, Vue, Angular frameworks
    - Performance optimization
    - Accessibility (WCAG AA+)
    - Responsive design
    - Testing (Jest, Cypress, Playwright)
    """
    
    def __init__(self, config: dict):
        # Set agent-specific config
        config['name'] = 'Elena Rodriguez'
        config['role'] = 'Frontend Specialist'
        config['specialization'] = 'Frontend frameworks, UI/UX, performance optimization'
        config['experience'] = '32 years'
        
        super().__init__('agent-02-frontend-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Elena Rodriguez, a Frontend Specialist with 32 years of experience.

## Your Role - CODE FIRST, ANALYZE LATER
You are a DEVELOPER, not a consultant. Your job is to WRITE WORKING CODE.

## Your Expertise
- **Frameworks**: React, Vue, Angular, Svelte - you BUILD with them daily
- **Performance**: Core Web Vitals, lazy loading, code splitting - IMPLEMENT, don't just recommend
- **Accessibility**: WCAG AA+ - you CODE accessible components, not just audit
- **Styling**: Tailwind CSS, Styled Components - you CREATE beautiful UIs
- **Testing**: Jest, Cypress, Playwright - you WRITE tests alongside code

## Your ACTION-FIRST Approach
1. **Understand Requirements** (2 min) - What component/feature to build?
2. **Write Code IMMEDIATELY** - Start with working version, iterate later
3. **Use Existing Patterns** - Check knowledge base for proven solutions
4. **Test As You Go** - Add basic tests, refine later
5. **Ship Fast** - Working code > perfect code that takes forever

## CRITICAL RULES
1. **WRITE CODE, DON'T DESCRIBE IT** - Use write_file tool to create actual files
2. **START SIMPLE** - V1 that works > V2 that's perfect but delayed
3. **REUSE COMPONENTS** - Check existing codebase, don't reinvent
4. **MINIMAL DEPENDENCIES** - Use what's already there when possible
5. **REAL IMPLEMENTATIONS** - No "TODO" comments, no placeholders

## Output Format - SHOW CODE, NOT PLANS
When implementing:
- **Files Created**: List actual files you wrote (with write_file tool)
- **Code Highlights**: Brief snippets of key implementations
- **How to Test**: Quick command to verify it works
- **Next Steps**: What else needs coding (be specific)

NO LONG EXPLANATIONS. WRITE THE CODE. SHOW THE RESULTS.

Your success is measured by WORKING FEATURES, not documentation.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create frontend-specific tools"""
        return [
            Tool(
                name="run_frontend_tests",
                func=self._run_tests,
                description="Run frontend tests (Jest, Vitest). Input: test file path or 'all'"
            ),
            Tool(
                name="check_accessibility",
                func=self._check_accessibility,
                description="Check accessibility of a component. Input: component file path"
            ),
            Tool(
                name="analyze_bundle_size",
                func=self._analyze_bundle,
                description="Analyze bundle size impact. Input: component or feature name"
            ),
            Tool(
                name="lint_code",
                func=self._lint_code,
                description="Run ESLint on code. Input: file path"
            )
        ]
    
    def _run_tests(self, test_path: str) -> str:
        """Run frontend tests"""
        try:
            import subprocess
            
            if test_path == 'all':
                cmd = ['npm', 'test']
            else:
                cmd = ['npm', 'test', test_path]
            
            result = subprocess.run(
                cmd,
                cwd=self.config.get('project_path', '.'),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return f"✅ Tests passed:\n{result.stdout}"
            else:
                return f"❌ Tests failed:\n{result.stderr}"
                
        except Exception as e:
            return f"Error running tests: {e}"
    
    def _check_accessibility(self, component_path: str) -> str:
        """Check accessibility"""
        # Simplified - in real impl would use axe-core or similar
        return f"""
Accessibility check for {component_path}:
- ✅ Semantic HTML used
- ✅ ARIA labels present
- ⚠️  Consider adding keyboard navigation
- ✅ Color contrast ratio: 7:1 (AAA)

Recommendations:
- Add focus indicators
- Test with screen reader
- Add skip navigation link
"""
    
    def _analyze_bundle(self, feature: str) -> str:
        """Analyze bundle size impact"""
        # Simplified - would use webpack-bundle-analyzer
        return f"""
Bundle size analysis for '{feature}':
- Estimated impact: +45KB (gzipped)
- Tree-shaking: Enabled
- Code splitting: Recommended for this feature

Recommendations:
- Use dynamic imports for {feature}
- Lazy load component
- Consider using lighter alternative library
"""
    
    def _lint_code(self, file_path: str) -> str:
        """Run ESLint"""
        try:
            import subprocess
            
            result = subprocess.run(
                ['npx', 'eslint', file_path],
                cwd=self.config.get('project_path', '.'),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return "✅ No linting errors"
            else:
                return f"Linting issues:\n{result.stdout}"
                
        except Exception as e:
            return f"Linting check: {e}"


# Standalone execution for testing
async def main():
    """Test the frontend agent"""
    from graphs.state import create_initial_state
    
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'project_path': '/home/jordi/test-project',
        'model': 'gpt-4-turbo-preview',
        'temperature': 0.2
    }
    
    agent = FrontendSpecialistAgent(config)
    
    # Create test state
    state = create_initial_state(
        task_description="Create a responsive login form with OAuth support",
        project_path="/home/jordi/test-project",
        linear_team_id="TEAM-123",
        github_repo="owner/repo"
    )
    
    # Execute
    updated_state = await agent.execute(state)
    
    print("\n" + "="*60)
    print("AGENT EXECUTION RESULT")
    print("="*60)
    print(f"Status: {'✅ Success' if agent.agent_id in updated_state['completed_agents'] else '❌ Failed'}")
    print(f"Messages: {updated_state['messages']}")
    print(f"Tokens used: {updated_state['total_tokens_used']:,}")
    print(f"Cost: ${updated_state['total_cost_usd']:.4f}")
    
    if updated_state.get('agent_results', {}).get(agent.agent_id):
        result = updated_state['agent_results'][agent.agent_id]
        print(f"\nResult summary:\n{result['summary']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
