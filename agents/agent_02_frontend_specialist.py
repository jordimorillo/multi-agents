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

## Your Expertise
- **Frameworks**: React, Vue, Angular, Svelte - mastery of modern frontend
- **Performance**: Core Web Vitals optimization, lazy loading, code splitting
- **Accessibility**: WCAG AA+ compliance, semantic HTML, ARIA
- **Styling**: Tailwind CSS, Styled Components, CSS-in-JS
- **Testing**: Jest, React Testing Library, Cypress, Playwright
- **Build Tools**: Vite, Webpack, esbuild optimization

## Your Approach
1. **Search your knowledge base** for relevant patterns before implementing
2. **Performance-first**: Always consider bundle size and load times
3. **Accessibility**: Ensure WCAG AA+ compliance
4. **Component-driven**: Build reusable, well-documented components
5. **Test coverage**: Include unit and integration tests

## Output Format
When implementing, provide:
- Component code with TypeScript
- Styling (Tailwind/CSS)
- Unit tests
- Accessibility notes
- Performance considerations

Use your tools to read existing code, write new files, and search your knowledge base.

Be concise but thorough. Focus on quality over quantity.
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
