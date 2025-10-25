"""
Full-Stack Architect & Coordinator Agent
Carlos Mendoza - 35 years experience in software architecture
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class FullStackArchitectAgent(LangChainAgentBase):
    """
    Full-stack architect and coordinator with expertise in:
    - System architecture and design patterns
    - Technology stack selection
    - Multi-agent coordination
    - Performance and scalability
    - Technical decision making
    """
    
    def __init__(self, config: dict):
        config['name'] = 'Carlos Mendoza'
        config['role'] = 'Full-Stack Architect & Coordinator'
        config['specialization'] = 'System architecture, technical leadership, multi-agent coordination'
        config['experience'] = '35 years'
        
        super().__init__('agent-01-fullstack-architect', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Carlos Mendoza, a Full-Stack Architect with 35 years of experience.

## Your Role - ACTION-ORIENTED
As the **architect and coordinator**, your PRIMARY goal is to GET THINGS DONE:
- **Analyze QUICKLY** - Don't over-analyze, focus on actionable decisions
- **Design PRAGMATICALLY** - Simple, working solutions over perfect architecture
- **Coordinate EFFICIENTLY** - Activate specialists and let them work
- **Deliver RESULTS** - Working code is the measure of progress

## Your Expertise
- **Architecture**: Microservices, monoliths, serverless, event-driven
- **Patterns**: SOLID, DDD, CQRS, Clean Architecture
- **Scalability**: Horizontal/vertical scaling, caching strategies
- **Databases**: SQL, NoSQL, graph databases, data modeling
- **Integration**: APIs, message queues, webhooks, GraphQL
- **Cloud**: AWS, Azure, GCP architecture

## Your ACTION-FIRST Approach
1. **Quick Analysis** (5 min max) - What needs to be built?
2. **Identify Specialists** - Who needs to code what?
3. **Simple Architecture** - Just enough design to start coding
4. **Delegate & Execute** - Specialists write code, you coordinate
5. **Iterate Fast** - Working code > perfect plans

## Coordination Strategy - DEVELOP FIRST, ANALYZE SECOND
When breaking down tasks:
- **Frontend work?** → @frontend-specialist codes immediately
- **Backend/APIs?** → @backend-specialist implements right away
- **Security concerns?** → @security-specialist reviews in parallel
- **Performance critical?** → @performance-specialist optimizes later
- **DevOps/deployment?** → @devops-specialist sets up CI/CD
- **Testing required?** → @qa-specialist writes tests after code exists

## CRITICAL RULES FOR ACTION-ORIENTED WORK
1. **PREFER CODING OVER PLANNING** - Specialists should write code, not just plans
2. **ITERATE, DON'T PERFECT** - Working v1 > perfect design that's never built
3. **PARALLEL WORK** - Multiple specialists can code simultaneously
4. **MINIMIZE MEETINGS** - Each agent works autonomously with clear goals
5. **DELIVER INCREMENTALLY** - Small working features > big unreleased projects

## Output Format - BRIEF & ACTIONABLE
Provide concise, action-focused output:
- **Task**: One-line summary of what to build
- **Agents**: Which specialists need to CODE (not just review)
- **Actions**: Specific coding tasks for each agent
- **Files**: Which files each agent will create/modify
- **Done**: What defines completion (working code)

NO LONG ESSAYS. NO OVER-ANALYSIS. FOCUS ON GETTING CODE WRITTEN.

Be strategic, pragmatic, and results-driven. The goal is WORKING SOFTWARE.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create architecture-specific tools"""
        return [
            Tool(
                name="analyze_codebase_structure",
                func=self._analyze_structure,
                description="Analyze codebase architecture. Input: project path"
            ),
            Tool(
                name="check_dependencies",
                func=self._check_dependencies,
                description="Analyze project dependencies and tech stack. Input: project path"
            ),
            Tool(
                name="estimate_complexity",
                func=self._estimate_complexity,
                description="Estimate task complexity and effort. Input: task description"
            ),
            Tool(
                name="suggest_architecture",
                func=self._suggest_architecture,
                description="Suggest architecture pattern. Input: requirements description"
            )
        ]
    
    def _analyze_structure(self, project_path: str) -> str:
        """Analyze codebase structure"""
        try:
            import os
            structure = []
            
            for root, dirs, files in os.walk(project_path):
                # Skip common ignore dirs
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.git', 'dist', 'build']]
                level = root.replace(project_path, '').count(os.sep)
                indent = ' ' * 2 * level
                structure.append(f"{indent}{os.path.basename(root)}/")
                
                if len(structure) > 50:  # Limit output
                    structure.append("... (truncated)")
                    break
            
            return f"Project structure:\n" + "\n".join(structure[:50])
        except Exception as e:
            return f"Could not analyze structure: {e}"
    
    def _check_dependencies(self, project_path: str) -> str:
        """Check project dependencies"""
        try:
            import json
            results = []
            
            # Check package.json
            pkg_json = os.path.join(project_path, 'package.json')
            if os.path.exists(pkg_json):
                with open(pkg_json) as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    results.append(f"Node.js project with {len(deps)} dependencies")
                    results.append(f"Key packages: {', '.join(list(deps.keys())[:5])}")
            
            # Check requirements.txt
            req_txt = os.path.join(project_path, 'requirements.txt')
            if os.path.exists(req_txt):
                with open(req_txt) as f:
                    lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                    results.append(f"Python project with {len(lines)} dependencies")
            
            # Check composer.json
            composer = os.path.join(project_path, 'composer.json')
            if os.path.exists(composer):
                results.append("PHP project (Composer)")
            
            return "\n".join(results) if results else "No standard dependency files found"
        except Exception as e:
            return f"Error checking dependencies: {e}"
    
    def _estimate_complexity(self, task_description: str) -> str:
        """Estimate task complexity"""
        indicators = {
            'high': ['migration', 'refactor', 'architecture', 'multiple services', 'distributed'],
            'medium': ['api', 'database', 'authentication', 'integration', 'testing'],
            'low': ['bug fix', 'styling', 'documentation', 'configuration']
        }
        
        task_lower = task_description.lower()
        complexity = 'low'
        
        if any(word in task_lower for word in indicators['high']):
            complexity = 'high'
        elif any(word in task_lower for word in indicators['medium']):
            complexity = 'medium'
        
        estimates = {
            'low': '2-4 hours',
            'medium': '1-2 days',
            'high': '3-5+ days'
        }
        
        return f"""
Complexity Analysis:
- Level: {complexity.upper()}
- Estimated effort: {estimates[complexity]}
- Recommended agents: {'3-5' if complexity == 'high' else '2-3' if complexity == 'medium' else '1-2'}
- Risk level: {'High - requires careful planning' if complexity == 'high' else 'Moderate' if complexity == 'medium' else 'Low'}
"""
    
    def _suggest_architecture(self, requirements: str) -> str:
        """Suggest architecture pattern"""
        req_lower = requirements.lower()
        
        if 'microservice' in req_lower or 'distributed' in req_lower:
            return """
Recommended: Microservices Architecture
- Service mesh for communication
- API Gateway pattern
- Event-driven communication
- Independent deployments
- Kubernetes orchestration
"""
        elif 'api' in req_lower:
            return """
Recommended: Layered Architecture
- API Layer (Controllers)
- Service Layer (Business logic)
- Data Layer (Repositories)
- Clean separation of concerns
- Easy to test and maintain
"""
        elif 'frontend' in req_lower or 'ui' in req_lower:
            return """
Recommended: Component-Based Architecture
- Atomic design principles
- State management (Redux/Zustand)
- Component composition
- Feature-based folder structure
- Design system integration
"""
        else:
            return """
Recommended: Modular Monolith
- Clear module boundaries
- Shared kernel approach
- Easy to understand and maintain
- Can evolve to microservices later
- Good for most projects
"""
