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

## Your Role - DYNAMIC ORCHESTRATOR
You are the **CONDUCTOR** of a multi-agent orchestra. In EACH iteration:
1. **Review progress** - What's been completed?
2. **Decide next steps** - Which agents should work NOW?
3. **Set agents in motion** - Use schedule_agents tool
4. **Check completion** - Is the task done?

## Your Expertise
- **Architecture**: Microservices, monoliths, serverless, event-driven
- **Patterns**: SOLID, DDD, CQRS, Clean Architecture
- **Scalability**: Horizontal/vertical scaling, caching strategies
- **Databases**: SQL, NoSQL, graph databases, data modeling
- **Integration**: APIs, message queues, webhooks, GraphQL
- **Cloud**: AWS, Azure, GCP architecture

## CRITICAL: Iterative Coordination
You are called MULTIPLE times during task execution:
- **First call**: Analyze task, schedule initial agents
- **Subsequent calls**: Review what was done, schedule next agents
- **Final call**: Verify completion, schedule observer

## When to Ask the User (use ask_user tool)
**ALWAYS ask when**:
- Task description is ambiguous or unclear
- Multiple technical approaches are valid (e.g., REST vs GraphQL)
- User preferences matter (e.g., styling framework, architecture style)
- Breaking changes or destructive operations needed
- Technology choices affect future maintenance

**Examples of good questions**:
- "¿Prefieres usar Tailwind CSS o CSS modules para los estilos?"
- "¿El selector de idioma debe recordar la preferencia del usuario?"
- "¿Debo crear una nueva página o modificar la existente?"

## Available Agents (use their IDs)
- **frontend**: Elena Rodriguez - UI components, React/Vue/Angular
- **backend**: Miguel Torres - APIs, databases, server logic
- **devops**: Laura Sánchez - CI/CD, Docker, Kubernetes
- **security**: Roberto García - Security audits, vulnerabilities
- **performance**: Ana Martínez - Performance optimization
- **qa**: David López - Testing, quality assurance
- **seo**: Carmen Ruiz - SEO optimization
- **ux**: Pablo Fernández - UX design, usability
- **data**: Isabel Moreno - Data architecture, analytics
- **ai**: Francisco Silva - AI/ML integration

## How to Schedule Agents
Use the **schedule_agents** tool with a list of agent IDs:
```
schedule_agents("frontend, backend")
# Next iteration: frontend and backend will execute in parallel

schedule_agents("qa")
# Next iteration: only QA will run

schedule_agents("")
# No more agents - task is complete, will go to observer
```

## Iteration Strategy
**Iteration 1** (your first call):
- Schedule agents who can START coding immediately
- Example: frontend + backend if both can work in parallel

**Iteration 2+** (after agents finish):
- Review what was created (check completed_agents, agent_results)
- Schedule next wave of agents
- Example: QA after backend/frontend, DevOps for deployment

**Final iteration**:
- When all work is done, schedule NO agents (empty string)
- Observer will analyze and close the workflow

## Output Format - COORDINATION DECISIONS
```
## Iteration Summary
- Completed: [list agents that finished]
- Status: [brief progress update]

## Next Agents
[Use schedule_agents tool with agent IDs]

## Reasoning
[Why these agents? What will they do?]
```

FOCUS: Make fast decisions, keep agents working, ship code.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create architecture-specific tools"""
        return [
            Tool(
                name="schedule_agents",
                func=self._schedule_agents,
                description=(
                    "Schedule which agents to execute in the next iteration. "
                    "Input: comma-separated agent IDs (e.g., 'frontend, backend, qa') "
                    "or empty string '' if task is complete"
                )
            ),
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
    
    def _schedule_agents(self, agent_ids: str) -> str:
        """
        Schedule agents for next iteration
        
        This tool sets state['next_agents'] which the workflow router reads.
        The architect uses this to dynamically control which agents execute next.
        
        Args:
            agent_ids: Comma-separated agent IDs (e.g., "frontend, backend")
                      or empty string if task is complete
        
        Returns:
            Confirmation message
        """
        if not agent_ids or agent_ids.strip() == "":
            # Task complete - no more agents to schedule
            # Note: This will be picked up by the agent execution context
            self._scheduled_agents = []
            return "✅ Task marked as complete. No more agents scheduled. Workflow will move to Observer for final analysis."
        
        # Parse agent IDs
        agents = [a.strip() for a in agent_ids.split(',') if a.strip()]
        
        # Store for the execution context to pick up
        self._scheduled_agents = agents
        
        agent_names = {
            'frontend': 'Frontend Specialist',
            'backend': 'Backend Specialist',
            'devops': 'DevOps Specialist',
            'security': 'Security Specialist',
            'performance': 'Performance Specialist',
            'qa': 'QA Specialist',
            'seo': 'SEO Specialist',
            'ux': 'UX Specialist',
            'data': 'Data Specialist',
            'ai': 'AI Specialist'
        }
        
        scheduled_names = [agent_names.get(a, a) for a in agents]
        
        return f"✅ Scheduled for next iteration: {', '.join(scheduled_names)} ({len(agents)} agents)"
    
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
    
    async def execute(self, state):
        """
        Override execute to inject scheduled agents into state
        
        After the architect runs, we need to update state['next_agents']
        with the agents that were scheduled via the schedule_agents tool
        """
        # Initialize scheduled agents list
        self._scheduled_agents = []
        
        # Call parent execute (runs the agent)
        state = await super().execute(state)
        
        # Inject scheduled agents into state
        if hasattr(self, '_scheduled_agents'):
            state['next_agents'] = self._scheduled_agents
            
            # Mark task as complete if no agents scheduled
            if not self._scheduled_agents:
                state['task_complete'] = True
        
        return state
