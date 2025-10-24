# 🚀 Sistema Multi-Agente Autónomo con LangChain + LangGraph

Sistema distribuido de agentes IA especializados que trabajan en colaboración para completar tareas de desarrollo de software. Cada agente es autónomo, actualiza Linear.app automáticamente, y crea PRs en GitHub.

## ✨ Características Principales

- **🤖 12 Agentes Especializados** - Arquitecto, Frontend, Backend, DevOps, Security, QA, etc.
- **🔗 LangChain + LangGraph** - Orchestración avanzada con estado compartido
- **📊 RAG Knowledge Base** - Cada agente aprende de experiencias pasadas
- **🔄 Ejecución Paralela** - Múltiples agentes trabajando simultáneamente
- **💾 Checkpointing** - Reanudar workflows desde cualquier punto
- **🔍 LangSmith Observability** - Tracking completo de tokens, costos y latencia
- **✅ Linear Integration** - Actualización automática de issues
- **🔀 GitHub Integration** - Branches, commits y PRs automáticos

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────┐
│         LANGGRAPH ORCHESTRATOR                   │
│  - StateGraph with conditional routing           │
│  - Parallel execution support                    │
│  - Automatic checkpointing                       │
└────────────────┬─────────────────────────────────┘
                 │
                 ↓
        ┌────────────────┐
        │  SHARED STATE  │
        │  - Task info   │
        │  - Results     │
        │  - Metrics     │
        └────────────────┘
                 │
    ┌────────────┼────────────┐
    ↓            ↓            ↓
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Agent 1 │  │ Agent 2 │  │ Agent N │
│LangChain│  │LangChain│  │LangChain│
│  +Tools │  │  +Tools │  │  +Tools │
│  +RAG   │  │  +RAG   │  │  +RAG   │
└─────────┘  └─────────┘  └─────────┘
     │            │            │
     └────────────┴────────────┘
                  │
         ┌────────┴────────┐
         ↓                 ↓
    ┌─────────┐      ┌──────────┐
    │ Linear  │      │  GitHub  │
    │  API    │      │   API    │
    └─────────┘      └──────────┘
```

## 🚀 Quick Start

### 1. Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/multi-agents.git
cd multi-agents

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

Crear archivo `.env`:

```bash
# LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Linear.app
LINEAR_API_KEY=lin_api_...
LINEAR_TEAM_ID=TEAM-123

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo-name

# LangSmith (opcional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_...
LANGCHAIN_PROJECT=multi-agents
```

### 3. Uso Básico

```python
from graphs.workflow import MultiAgentWorkflow

# Configurar
config = {
    'openai_api_key': os.getenv('OPENAI_API_KEY'),
    'linear_api_key': os.getenv('LINEAR_API_KEY'),
    'github_token': os.getenv('GITHUB_TOKEN'),
    'github_repo': 'owner/repo',
    'model': 'gpt-4-turbo-preview'
}

# Crear workflow
workflow = MultiAgentWorkflow(config)

# Ejecutar tarea
final_state = await workflow.execute(
    task_description="Implementar autenticación OAuth 2.0",
    project_path="/path/to/project",
    linear_team_id="TEAM-123",
    github_repo="owner/repo"
)

print(f"✅ Completado en {final_state['execution_time_seconds']:.1f}s")
print(f"💰 Costo: ${final_state['total_cost_usd']:.4f}")
print(f"🔀 PRs creados: {len(final_state['github_prs'])}")
```

## 📖 Ejemplos de Uso

### Ejemplo 1: Nueva Feature

```python
workflow = MultiAgentWorkflow(config)

result = await workflow.execute(
    task_description="""
    Añadir sistema de comentarios en tiempo real:
    - Backend: WebSocket endpoints
    - Frontend: UI de comentarios React
    - Tests: E2E con Playwright
    """,
    project_path="/home/user/mi-app",
    linear_team_id="TEAM-123",
    github_repo="myorg/myapp"
)

# Output:
# ✅ Architect completed analysis
# ✅ Security approved
# ✅ Backend completed (PR #156)
# ✅ Frontend completed (PR #157)
# ✅ QA tests passed
# ✅ Observer updated RAG
# Total: 8.5 minutes, $2.34, 3 PRs
```

### Ejemplo 2: Bug Fix

```python
result = await workflow.execute(
    task_description="Fix memory leak in user session management",
    project_path="/home/user/mi-app",
    linear_team_id="TEAM-123",
    github_repo="myorg/myapp"
)

# Agents activados automáticamente:
# - Backend (fixes session handling)
# - Performance (validates fix)
# - QA (regression tests)
```

### Ejemplo 3: Reanudar Workflow

```python
# Si un workflow falla o se interrumpe
result = await workflow.resume(task_id="abc-123-def")

# Continúa desde el último checkpoint
```

## 🎯 Agentes Disponibles

| Agent | Especialización | Triggers |
|-------|----------------|----------|
| **Architect** | Coordinación, arquitectura | Siempre primero |
| **Security** | Auditorías, vulnerabilidades | Antes de implementación |
| **Backend** | APIs, bases de datos | Backend changes |
| **Frontend** | React/Vue, UI/UX | Frontend changes |
| **DevOps** | CI/CD, deployment | Deployment needed |
| **Performance** | Optimización, escalabilidad | Performance issues |
| **QA** | Testing, calidad | Siempre al final |
| **SEO** | SEO técnico | Content/SEO work |
| **UX** | Experiencia de usuario | UX improvements |
| **Data** | Arquitectura de datos | Data pipelines |
| **AI** | ML/AI integration | AI features |
| **Observer** | Análisis, aprendizaje | Siempre al final |

## 🔧 Configuración Avanzada

### Custom Agent

```python
from agents.base.langgraph_agent import LangChainAgentBase
from langchain.tools import Tool

class CustomAgent(LangChainAgentBase):
    def __init__(self, config):
        config['name'] = 'Mi Agente'
        config['specialization'] = 'Mi especialización'
        super().__init__('agent-custom', config)
    
    def _get_system_prompt(self) -> str:
        return "Eres un especialista en..."
    
    def _create_custom_tools(self) -> List[Tool]:
        return [
            Tool(
                name="mi_tool",
                func=self._mi_funcion,
                description="Descripción de la tool"
            )
        ]
    
    def _mi_funcion(self, input: str) -> str:
        return "resultado..."
```

### Custom Workflow

```python
from langgraph.graph import StateGraph, END
from graphs.state import AgentState

workflow = StateGraph(AgentState)

# Añadir nodos
workflow.add_node("agent1", agent1.execute)
workflow.add_node("agent2", agent2.execute)

# Definir flujo
workflow.set_entry_point("agent1")
workflow.add_edge("agent1", "agent2")
workflow.add_edge("agent2", END)

# Compilar
graph = workflow.compile()

# Ejecutar
result = await graph.ainvoke(initial_state)
```

## 📊 Monitoring con LangSmith

```bash
# Activar tracing
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls_...
export LANGCHAIN_PROJECT=multi-agents

# Ejecutar workflow
python -m graphs.workflow

# Ver en https://smith.langchain.com
# - Latencia por agente
# - Tokens y costos
# - Tool calls
# - Errores y stack traces
```

## 🧪 Testing

```bash
# Tests unitarios
pytest tests/test_agents.py

# Test de workflow completo
pytest tests/test_workflow.py -v

# Coverage
pytest --cov=agents --cov=graphs tests/
```

## 📚 Documentación Detallada

- [Arquitectura LangGraph](./architecture/LANGGRAPH_ARCHITECTURE.md)
- [Roadmap de Implementación](./architecture/IMPLEMENTATION_ROADMAP.md)
- [Guía de Agentes](./AGENTS.md)
- [Ejemplos Avanzados](./examples/)

## 🤝 Contribuir

```bash
# Fork y clonar
git clone https://github.com/tu-usuario/multi-agents.git

# Crear branch
git checkout -b feature/mi-agente

# Implementar y testear
pytest tests/

# Commit y push
git commit -m "feat: add custom agent"
git push origin feature/mi-agente

# Crear PR
```

## 📈 Roadmap

- [x] Arquitectura base con LangChain + LangGraph
- [x] Integración Linear.app
- [x] Integración GitHub
- [x] Sistema RAG con vector store
- [x] Agent base con tools
- [x] Workflow con routing condicional
- [ ] Implementar 12 agentes completos
- [ ] Dashboard web React
- [ ] CLI tool
- [ ] Docker deployment
- [ ] Kubernetes charts
- [ ] Métricas avanzadas
- [ ] A/B testing de prompts

## 💡 Ventajas vs Sistemas Tradicionales

| Feature | Multi-Agent System | Traditional |
|---------|-------------------|-------------|
| **Especialización** | ✅ Expertos dedicados | ❌ Genérico |
| **Paralelización** | ✅ Nativa | ❌ Manual |
| **Aprendizaje** | ✅ RAG automático | ❌ No aprende |
| **Observabilidad** | ✅ LangSmith | ⚠️  Logs básicos |
| **Recuperación** | ✅ Checkpoints | ❌ Reiniciar todo |
| **Testing** | ✅ Por agente | ⚠️  End-to-end solo |
| **Escalabilidad** | ✅ Horizontal | ⚠️  Limitada |

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/multi-agents/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tu-usuario/multi-agents/discussions)
- **Docs**: [Documentation](https://docs.multiagents.dev)

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE)

---

**Construido con** 🦜🔗 LangChain + 🕸️ LangGraph + ❤️
