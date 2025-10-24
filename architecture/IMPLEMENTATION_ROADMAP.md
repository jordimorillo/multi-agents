# Roadmap de Implementación - Sistema Multi-Agente Autónomo

## 🎯 Objetivo
Transformar el sistema conceptual multi-agente en un **sistema ejecutable autónomo** donde cada agente:
- Se ejecuta como proceso independiente
- Actualiza Linear.app automáticamente
- Crea commits y PRs en GitHub
- Se coordina con otros agentes vía message broker

## 📅 Fases de Desarrollo

### FASE 1: Infraestructura Core (Semana 1)
**Objetivo**: Establecer la base de comunicación y coordinación

#### Task 1.1: Setup de Message Broker
```bash
# Tecnología: Redis con Redis Streams
# Tiempo estimado: 1 día
```

**Entregables**:
- [ ] Docker Compose con Redis configurado
- [ ] Script de inicialización de colas y streams
- [ ] Pruebas básicas de pub/sub y streams
- [ ] Documentación de estructura de mensajes

**Archivos a crear**:
```
infrastructure/
├── docker-compose.yml
├── redis/
│   ├── redis.conf
│   └── init-streams.sh
└── tests/
    └── test_redis_connection.py
```

#### Task 1.2: Base de Datos de Estado
```bash
# Tecnología: PostgreSQL
# Tiempo estimado: 1 día
```

**Entregables**:
- [ ] Schema de base de datos (tasks, agents, logs)
- [ ] Migraciones con Alembic
- [ ] Modelos SQLAlchemy o Prisma
- [ ] Seeds iniciales

**Archivos a crear**:
```
database/
├── models.py
├── migrations/
│   ├── 001_create_tasks_table.sql
│   ├── 002_create_agents_table.sql
│   └── 003_create_logs_table.sql
└── seeds.py
```

#### Task 1.3: Orchestrator Base
```bash
# Tecnología: Python FastAPI
# Tiempo estimado: 2 días
```

**Entregables**:
- [ ] API REST con FastAPI
- [ ] Endpoints básicos (create_task, get_status)
- [ ] Integración con Redis y DB
- [ ] Health checks y monitoring

**Archivos a crear**:
```
orchestrator/
├── main.py
├── api/
│   ├── tasks.py
│   ├── agents.py
│   └── health.py
├── services/
│   ├── task_service.py
│   └── agent_coordinator.py
└── tests/
    └── test_api.py
```

---

### FASE 2: Integraciones Externas (Semana 2)

#### Task 2.1: Cliente Linear.app
```bash
# Tecnología: Linear SDK + GraphQL
# Tiempo estimado: 2 días
```

**Entregables**:
- [ ] Wrapper de Linear SDK
- [ ] Métodos: create_issue, update_issue, create_comment
- [ ] Manejo de errores y rate limiting
- [ ] Tests con mocks

**Archivos a crear**:
```
integrations/
├── linear/
│   ├── client.py
│   ├── models.py
│   ├── exceptions.py
│   └── tests/
│       └── test_linear_client.py
└── config.py
```

**Ejemplo de uso**:
```python
linear = LinearClient(api_key=os.getenv('LINEAR_API_KEY'))

# Crear issue principal
issue = await linear.create_issue(
    team_id='TEAM-123',
    title='Implementar autenticación',
    description='Sistema OAuth completo'
)

# Crear sub-issues
sub_issue = await linear.create_sub_issue(
    parent_id=issue.id,
    title='Backend OAuth endpoints',
    description='Implementar /auth/login y /auth/callback'
)

# Actualizar estado
await linear.update_issue(
    issue_id=sub_issue.id,
    status='In Progress',
    comment='🤖 Agent @backend-specialist comenzó la implementación'
)
```

#### Task 2.2: Cliente GitHub
```bash
# Tecnología: PyGithub
# Tiempo estimado: 2 días
```

**Entregables**:
- [ ] Wrapper de GitHub API
- [ ] Métodos: create_branch, commit_file, create_pr
- [ ] Manejo de conflictos
- [ ] Tests con repositorio de prueba

**Archivos a crear**:
```
integrations/
├── github/
│   ├── client.py
│   ├── branch_manager.py
│   ├── pr_manager.py
│   └── tests/
│       └── test_github_client.py
```

**Ejemplo de uso**:
```python
github = GitHubClient(
    token=os.getenv('GITHUB_TOKEN'),
    repo='owner/repo'
)

# Crear branch
branch = await github.create_branch(
    name='agent/backend/auth-oauth',
    from_branch='main'
)

# Hacer commits
await github.commit_file(
    branch='agent/backend/auth-oauth',
    path='src/auth/oauth.py',
    content='# OAuth implementation...',
    message='feat: add OAuth endpoints'
)

# Crear PR
pr = await github.create_pull_request(
    head='agent/backend/auth-oauth',
    base='main',
    title='feat: OAuth authentication system',
    body='Implemented by @backend-specialist agent\n\nCloses LINEAR-123'
)
```

#### Task 2.3: Cliente LLM
```bash
# Tecnología: LangChain + OpenAI/Anthropic
# Tiempo estimado: 1 día
```

**Entregables**:
- [ ] Wrapper unificado para múltiples LLMs
- [ ] Sistema de prompts templatizados
- [ ] Caching de respuestas
- [ ] Métricas de uso y costo

**Archivos a crear**:
```
integrations/
├── llm/
│   ├── client.py
│   ├── prompts/
│   │   ├── agent_prompts.py
│   │   └── templates/
│   ├── cache.py
│   └── tests/
```

---

### FASE 3: Agentes Autónomos (Semana 3-4)

#### Task 3.1: Agent Framework Base
```bash
# Framework común para todos los agentes
# Tiempo estimado: 3 días
```

**Entregables**:
- [ ] Clase base `BaseAgent` con lifecycle
- [ ] Sistema de colas y consumo de tareas
- [ ] Logging estructurado
- [ ] Manejo de errores y reintentos

**Archivos a crear**:
```
agents/
├── base/
│   ├── agent_base.py
│   ├── task_processor.py
│   ├── rag_loader.py
│   └── lifecycle.py
├── config/
│   └── agent_configs.json
└── utils/
    ├── logger.py
    └── metrics.py
```

**Ejemplo de Agent Base**:
```python
# agents/base/agent_base.py
from abc import ABC, abstractmethod
import asyncio
from redis import Redis
from integrations.linear import LinearClient
from integrations.github import GitHubClient
from integrations.llm import LLMClient

class BaseAgent(ABC):
    def __init__(self, agent_id: str, config: dict):
        self.agent_id = agent_id
        self.config = config
        self.redis = Redis.from_url(config['redis_url'])
        self.linear = LinearClient(config['linear_api_key'])
        self.github = GitHubClient(config['github_token'], config['repo'])
        self.llm = LLMClient(config['llm_provider'])
        self.running = False
        
    async def start(self):
        """Iniciar el agente"""
        self.running = True
        print(f"🤖 {self.agent_id} started")
        await self.run_loop()
    
    async def run_loop(self):
        """Loop principal del agente"""
        queue_name = f"tasks:{self.agent_id}"
        
        while self.running:
            try:
                # Consumir tarea de Redis Stream
                messages = await self.redis.xreadgroup(
                    groupname=f'{self.agent_id}-workers',
                    consumername=self.agent_id,
                    streams={queue_name: '>'},
                    count=1,
                    block=1000
                )
                
                if not messages:
                    continue
                
                for stream, task_list in messages:
                    for task_id, task_data in task_list:
                        await self.process_task(task_id, task_data)
                        
            except Exception as e:
                print(f"❌ Error in {self.agent_id}: {e}")
                await asyncio.sleep(5)
    
    async def process_task(self, task_id: str, task_data: dict):
        """Procesar una tarea"""
        try:
            # 1. Actualizar Linear: In Progress
            await self.linear.update_issue(
                issue_id=task_data['linear_issue_id'],
                status='In Progress',
                comment=f'🤖 {self.agent_id} started working'
            )
            
            # 2. Cargar RAG knowledge
            rag_context = await self.load_rag_knowledge(task_data)
            
            # 3. Ejecutar tarea con LLM
            result = await self.execute_task(task_data, rag_context)
            
            # 4. Aplicar cambios a GitHub si hay código
            if result.has_code_changes:
                pr = await self.push_to_github(task_data, result)
                result.github_pr = pr.html_url
            
            # 5. Actualizar Linear: Done
            await self.linear.update_issue(
                issue_id=task_data['linear_issue_id'],
                status='Done',
                comment=f'✅ Completed by {self.agent_id}\n\n{result.summary}'
            )
            
            # 6. Notificar completado
            await self.publish_completion(task_id, result)
            
            # 7. ACK del mensaje
            await self.redis.xack(
                f"tasks:{self.agent_id}",
                f'{self.agent_id}-workers',
                task_id
            )
            
        except Exception as e:
            await self.handle_error(task_id, task_data, e)
    
    @abstractmethod
    async def execute_task(self, task_data: dict, rag_context: dict):
        """Método abstracto: cada agente implementa su lógica"""
        pass
    
    async def load_rag_knowledge(self, task_data: dict):
        """Cargar conocimiento RAG del agente"""
        rag_file = f".agents/rag-knowledge/individual/{self.agent_id}-rag.json"
        # Leer y filtrar patrones relevantes
        return rag_context
    
    async def push_to_github(self, task_data: dict, result):
        """Crear branch, commits y PR"""
        branch_name = f"agent/{self.agent_id}/{task_data['task_id']}"
        
        # Crear branch
        await self.github.create_branch(branch_name)
        
        # Commits
        for file_change in result.file_changes:
            await self.github.commit_file(
                branch=branch_name,
                path=file_change.path,
                content=file_change.content,
                message=file_change.commit_message
            )
        
        # Crear PR
        pr = await self.github.create_pull_request(
            head=branch_name,
            base='main',
            title=result.pr_title,
            body=result.pr_body + f"\n\nLinear: {task_data['linear_issue_url']}"
        )
        
        return pr
    
    async def publish_completion(self, task_id: str, result):
        """Publicar evento de completado"""
        await self.redis.publish('events:task-completed', {
            'agent': self.agent_id,
            'task_id': task_id,
            'status': 'completed',
            'summary': result.summary
        })
    
    async def stop(self):
        """Detener el agente gracefully"""
        self.running = False
        print(f"🛑 {self.agent_id} stopped")
```

#### Task 3.2: Implementar Agentes Específicos
```bash
# Crear los 12 agentes especializados
# Tiempo estimado: 5 días (paralelo)
```

**Agentes a implementar**:
```
agents/
├── agent_01_fullstack_architect.py
├── agent_02_frontend_specialist.py
├── agent_03_backend_specialist.py
├── agent_04_devops_specialist.py
├── agent_05_security_specialist.py
├── agent_06_performance_specialist.py
├── agent_07_qa_specialist.py
├── agent_08_seo_specialist.py
├── agent_09_ux_specialist.py
├── agent_10_data_specialist.py
├── agent_11_ai_specialist.py
└── agent_12_observer_optimizer.py
```

**Ejemplo: Frontend Specialist**:
```python
# agents/agent_02_frontend_specialist.py
from agents.base.agent_base import BaseAgent
from dataclasses import dataclass

@dataclass
class TaskResult:
    summary: str
    file_changes: list
    pr_title: str
    pr_body: str
    has_code_changes: bool = True

class FrontendSpecialist(BaseAgent):
    def __init__(self, config):
        super().__init__('agent-02-frontend', config)
        self.specialization = "Frontend development, React, Vue, performance"
    
    async def execute_task(self, task_data: dict, rag_context: dict):
        """Implementar tarea frontend con LLM"""
        
        # Construir prompt especializado
        prompt = f"""
You are Elena Rodriguez, a Frontend Specialist with 32 years of experience.

TASK: {task_data['description']}

PROJECT CONTEXT:
- Framework: {task_data.get('framework', 'React')}
- Existing code: {task_data.get('context', '')}

RAG KNOWLEDGE (proven patterns):
{rag_context}

DELIVERABLES REQUIRED:
1. Component implementation with TypeScript
2. Unit tests (Jest/Vitest)
3. Accessibility compliance (WCAG AA)
4. Performance optimization (Core Web Vitals)

OUTPUT FORMAT (JSON):
{{
  "summary": "Brief description of implementation",
  "file_changes": [
    {{
      "path": "src/components/LoginForm.tsx",
      "content": "// Component code...",
      "commit_message": "feat: add login form component"
    }}
  ],
  "pr_title": "feat: login form implementation",
  "pr_body": "Detailed description with testing notes"
}}
"""
        
        # Ejecutar LLM
        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.2,
            max_tokens=4000
        )
        
        # Parse respuesta
        result_data = self.parse_llm_response(response)
        
        return TaskResult(**result_data)
    
    def parse_llm_response(self, response: str) -> dict:
        """Parsear respuesta JSON del LLM"""
        import json
        # Extraer JSON de la respuesta
        return json.loads(response)

# Entry point
if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    config = {
        'redis_url': os.getenv('REDIS_URL'),
        'linear_api_key': os.getenv('LINEAR_API_KEY'),
        'github_token': os.getenv('GITHUB_TOKEN'),
        'repo': os.getenv('GITHUB_REPO'),
        'llm_provider': 'openai'
    }
    
    agent = FrontendSpecialist(config)
    asyncio.run(agent.start())
```

#### Task 3.3: Sistema de Deployment de Agentes
```bash
# Docker containers para cada agente
# Tiempo estimado: 2 días
```

**Entregables**:
- [ ] Dockerfile para agentes
- [ ] Docker Compose para todos los agentes
- [ ] Scripts de inicio/parada
- [ ] Health checks

**Archivos a crear**:
```
deployment/
├── Dockerfile.agent
├── docker-compose.agents.yml
├── scripts/
│   ├── start-all-agents.sh
│   ├── stop-all-agents.sh
│   └── restart-agent.sh
└── health/
    └── check-agents.py
```

---

### FASE 4: Coordinación Avanzada (Semana 5)

#### Task 4.1: Dependency Management
```bash
# Sistema de dependencias entre tareas
# Tiempo estimado: 2 días
```

**Entregables**:
- [ ] DAG de dependencias de tareas
- [ ] Sistema de espera y notificación
- [ ] Resolución de deadlocks

#### Task 4.2: Observer & Optimizer Autónomo
```bash
# Agente que analiza y optimiza automáticamente
# Tiempo estimado: 3 días
```

**Entregables**:
- [ ] Análisis post-intervención automático
- [ ] Actualización de RAG knowledge
- [ ] Optimización de configuraciones

---

### FASE 5: CLI y UX (Semana 6)

#### Task 5.1: CLI Tool
```bash
# CLI para interactuar con el sistema
# Tiempo estimado: 2 días
```

**Ejemplo de uso**:
```bash
# Crear tarea
multi-agent task create "Implementar autenticación OAuth" \
  --project /home/user/mi-proyecto \
  --linear-team TEAM-123

# Ver estado
multi-agent task status TASK-456

# Ver logs en tiempo real
multi-agent task logs TASK-456 --follow

# Estado de agentes
multi-agent agents status

# Detener tarea
multi-agent task cancel TASK-456
```

#### Task 5.2: Dashboard Web
```bash
# Dashboard para monitoreo visual
# Tiempo estimado: 3 días
```

**Tecnología**: React + WebSockets
**Features**:
- Estado en tiempo real de tareas
- Estado de agentes (idle/working)
- Logs en vivo
- Métricas y gráficos

---

## 🎯 Milestones

### Milestone 1: MVP Funcional (Fin Semana 4)
- ✅ 1 agente funcionando end-to-end
- ✅ Integración Linear + GitHub completa
- ✅ Orquestador básico
- ✅ Ejemplo de tarea completada automáticamente

### Milestone 2: Sistema Completo (Fin Semana 6)
- ✅ 12 agentes operativos
- ✅ Coordinación con dependencias
- ✅ CLI funcional
- ✅ Dashboard de monitoreo
- ✅ Documentación completa

### Milestone 3: Producción (Semana 7-8)
- ✅ Tests E2E
- ✅ CI/CD setup
- ✅ Deployment en cloud
- ✅ Monitoring y alertas
- ✅ Backup y recovery

---

## 📊 Métricas de Éxito

- **Performance**: Tarea promedio < 10 minutos
- **Calidad**: 90%+ PRs aprobados sin cambios
- **Confiabilidad**: 95%+ tareas completadas exitosamente
- **Cost**: < $5 USD en APIs por tarea promedio

---

## 🚀 Comenzar Implementación

```bash
# 1. Clonar y preparar
cd /home/jordi/IdeaProjects/multi-agents
git checkout -b feature/autonomous-agents

# 2. Crear estructura
mkdir -p {infrastructure,orchestrator,agents,integrations,deployment}

# 3. Comenzar con Fase 1
cd infrastructure
# Seguir tareas de Task 1.1...
```

Ver archivos específicos de implementación en `/implementation/` directory.
