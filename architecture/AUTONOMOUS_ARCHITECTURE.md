# Arquitectura de Sistema Multi-Agente Autónomo

## 🎯 Visión General

Sistema distribuido donde cada agente IA es un **proceso independiente** que:
- Se ejecuta de forma autónoma en su propio runtime
- Recibe tareas, las ejecuta y reporta resultados
- Se comunica con otros agentes vía message broker
- Actualiza Linear.app automáticamente
- Crea branches/commits/PRs en GitHub automáticamente

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Central Hub)                    │
│  - Recibe peticiones de usuario                                 │
│  - Analiza y descompone en tareas                               │
│  - Asigna tareas a agentes específicos                          │
│  - Monitorea progreso y coordina dependencias                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MESSAGE BROKER (Redis/RabbitMQ)              │
│  - Cola de tareas por agente                                    │
│  - Sistema de pub/sub para eventos                              │
│  - Estado compartido y coordinación                             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬─────────────┐
        ↓              ↓              ↓             ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   AGENT 01   │ │   AGENT 02   │ │   AGENT 03   │ │   AGENT 12   │
│  Fullstack   │ │   Frontend   │ │   Backend    │ │   Observer   │
│  Architect   │ │  Specialist  │ │  Specialist  │ │  Optimizer   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                              │
                  ┌───────────┴───────────┐
                  ↓                       ↓
          ┌──────────────┐        ┌──────────────┐
          │  LINEAR API  │        │  GITHUB API  │
          │  - Create    │        │  - Branch    │
          │  - Update    │        │  - Commit    │
          │  - Comment   │        │  - PR        │
          └──────────────┘        └──────────────┘
```

## 🔧 Componentes del Sistema

### 1. Orchestrator (Coordinador Central)
**Tecnología**: Python FastAPI / Node.js Express
**Responsabilidades**:
- Recibir requests de usuario (CLI, API, Webhook)
- Analizar y descomponer en subtareas
- Crear issues en Linear para cada subtarea
- Asignar tareas a agentes específicos vía message queue
- Monitorear progreso y gestionar dependencias
- Agregar resultados finales

**Endpoints**:
```python
POST /tasks/create          # Crear nueva tarea multi-agente
GET  /tasks/{id}/status     # Consultar estado de tarea
POST /tasks/{id}/cancel     # Cancelar tarea en progreso
GET  /agents/status         # Estado de todos los agentes
```

### 2. Message Broker (Redis con Redis Streams)
**Por qué Redis**:
- Ligero y rápido
- Redis Streams para colas persistentes
- Pub/Sub para eventos en tiempo real
- Estado compartido (Redis Hash)
- Fácil de deployar

**Estructura de Colas**:
```
tasks:agent-01              # Cola de tareas para Arquitecto
tasks:agent-02              # Cola de tareas para Frontend
tasks:agent-03              # Cola de tareas para Backend
...
events:agent-coordination   # Canal pub/sub para eventos
state:task:{id}             # Hash con estado de tarea
```

### 3. Agentes Autónomos (Workers Independientes)
**Tecnología**: Python (LangChain + OpenAI) o Node.js
**Cada agente es un proceso que**:

```python
# Ejemplo: agent_frontend.py
class FrontendAgent:
    def __init__(self, agent_id, redis_client, linear_client, github_client):
        self.agent_id = agent_id
        self.redis = redis_client
        self.linear = linear_client
        self.github = github_client
        self.llm = OpenAI(model="gpt-4")
        
    async def run(self):
        """Loop principal del agente"""
        while True:
            # 1. Obtener tarea de la cola
            task = await self.redis.xread_group(
                groupname='frontend-workers',
                consumername=self.agent_id,
                streams={'tasks:agent-02': '>'}
            )
            
            if not task:
                await asyncio.sleep(1)
                continue
            
            # 2. Procesar tarea con LLM
            result = await self.process_task(task)
            
            # 3. Actualizar Linear
            await self.update_linear(task.linear_issue_id, result)
            
            # 4. Crear commit/PR en GitHub
            if result.has_code_changes:
                await self.push_to_github(result)
            
            # 5. Notificar completado
            await self.redis.publish('events:agent-coordination', {
                'agent': self.agent_id,
                'task_id': task.id,
                'status': 'completed'
            })
    
    async def process_task(self, task):
        """Ejecutar tarea con LLM"""
        # Consultar RAG del agente
        rag_context = self.load_rag_knowledge()
        
        # Prompt al LLM
        prompt = f"""
        Eres un especialista frontend con 32 años de experiencia.
        
        Tarea: {task.description}
        Contexto del proyecto: {task.project_context}
        RAG Knowledge: {rag_context}
        
        Implementa la solución y genera:
        1. Código necesario
        2. Tests
        3. Documentación
        """
        
        response = await self.llm.agenerate(prompt)
        return self.parse_response(response)
    
    async def update_linear(self, issue_id, result):
        """Actualizar issue de Linear"""
        await self.linear.update_issue(
            issue_id=issue_id,
            status='Done',
            comment=f"✅ Completado por {self.agent_id}\n\n{result.summary}"
        )
    
    async def push_to_github(self, result):
        """Crear branch, commit y PR"""
        branch_name = f"agent/{self.agent_id}/{result.task_id}"
        
        # Crear branch
        await self.github.create_branch(branch_name)
        
        # Crear commits
        for file_change in result.file_changes:
            await self.github.commit_file(
                branch=branch_name,
                path=file_change.path,
                content=file_change.content,
                message=f"feat: {file_change.description}"
            )
        
        # Crear PR
        pr = await self.github.create_pull_request(
            head=branch_name,
            base='main',
            title=result.pr_title,
            body=result.pr_description
        )
        
        return pr
```

### 4. Integraciones Externas

#### Linear.app Integration
```python
# linear_client.py
class LinearClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = 'https://api.linear.app/graphql'
    
    async def create_issue(self, team_id, title, description, assignee=None):
        """Crear issue en Linear"""
        mutation = """
        mutation IssueCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            issue {
              id
              identifier
              url
            }
          }
        }
        """
        # Implementación GraphQL...
    
    async def update_issue(self, issue_id, status=None, comment=None):
        """Actualizar estado e comentario"""
        # Implementación...
    
    async def create_sub_issue(self, parent_id, title, description):
        """Crear sub-issue"""
        # Implementación...
```

#### GitHub Integration
```python
# github_client.py
class GitHubClient:
    def __init__(self, token, repo_owner, repo_name):
        self.github = Github(token)
        self.repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
    
    async def create_branch(self, branch_name, from_branch='main'):
        """Crear nueva branch"""
        source = self.repo.get_branch(from_branch)
        self.repo.create_git_ref(
            ref=f'refs/heads/{branch_name}',
            sha=source.commit.sha
        )
    
    async def commit_file(self, branch, path, content, message):
        """Crear o actualizar archivo"""
        try:
            file = self.repo.get_contents(path, ref=branch)
            self.repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=file.sha,
                branch=branch
            )
        except:
            self.repo.create_file(
                path=path,
                message=message,
                content=content,
                branch=branch
            )
    
    async def create_pull_request(self, head, base, title, body):
        """Crear PR"""
        pr = self.repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base
        )
        return pr
```

## 🚀 Flujo de Ejecución Completo

### Ejemplo: "Añadir autenticación de usuarios"

```
1. USUARIO → ORCHESTRATOR
   POST /tasks/create
   {
     "description": "Añadir autenticación de usuarios con OAuth",
     "project_path": "/home/user/mi-proyecto",
     "linear_team_id": "TEAM-123",
     "github_repo": "owner/repo"
   }

2. ORCHESTRATOR → LINEAR
   - Crear issue principal: "User Authentication System"
   - Crear sub-issues:
     * SUB-001: Security requirements analysis (@security-specialist)
     * SUB-002: Backend OAuth implementation (@backend-specialist)
     * SUB-003: Frontend login UI (@frontend-specialist)
     * SUB-004: Testing strategy (@qa-specialist)

3. ORCHESTRATOR → MESSAGE BROKER
   - Enviar tarea a tasks:agent-05 (security)
   - Esperar completado de SUB-001
   - Enviar tareas paralelas a agent-02 y agent-03
   - Finalmente enviar a agent-07 (QA)

4. AGENT-05 (Security) EJECUTA:
   a) Consume tarea de Redis: tasks:agent-05
   b) Analiza con LLM + RAG: 
      - Consulta security-patterns RAG
      - Genera análisis de seguridad
   c) Actualiza Linear:
      - SUB-001 → In Progress
      - Añade comentario con análisis
      - SUB-001 → Done
   d) Publica evento: 'security-analysis-completed'

5. AGENT-03 (Backend) EJECUTA:
   a) Recibe tarea (dependencia de security completada)
   b) Implementa con LLM:
      - Genera código OAuth backend
      - Crea tests unitarios
   c) GitHub Actions:
      - Crea branch: agent/backend-specialist/oauth-implementation
      - Commit: auth endpoints
      - Commit: tests
      - Crea PR: "feat: OAuth backend implementation"
   d) Linear Update:
      - SUB-002 → Done
      - Link a PR en comentario

6. AGENT-02 (Frontend) EJECUTA (en paralelo):
   a) Implementa UI de login
   b) GitHub Actions:
      - Crea branch: agent/frontend-specialist/login-ui
      - Commits de componentes React
      - Crea PR: "feat: Login UI components"
   c) Linear Update:
      - SUB-003 → Done

7. AGENT-07 (QA) EJECUTA (al final):
   a) Genera estrategia de testing
   b) Crea tests E2E
   c) GitHub: Commit tests en branch separada
   d) Linear: SUB-004 → Done

8. ORCHESTRATOR → USUARIO:
   {
     "status": "completed",
     "linear_issue": "PROJ-456",
     "github_prs": [
       "#123 - OAuth backend",
       "#124 - Login UI",
       "#125 - E2E tests"
     ],
     "duration": "8 minutes",
     "agents_involved": ["security", "backend", "frontend", "qa"]
   }
```

## 📦 Stack Tecnológico Recomendado

### Core Infrastructure
- **Orchestrator**: Python FastAPI o Node.js Express
- **Message Broker**: Redis con Redis Streams
- **Database**: PostgreSQL (estado, logs, métricas)
- **Agents**: Python (LangChain + OpenAI/Anthropic)

### Integraciones
- **Linear SDK**: `@linear/sdk` (Node) o `linear-api` (Python)
- **GitHub API**: `PyGithub` (Python) o `@octokit/rest` (Node)
- **LLM**: OpenAI API, Anthropic Claude, o LLM local

### Deployment
- **Container**: Docker + Docker Compose
- **Orchestration**: Kubernetes (opcional para scale)
- **CI/CD**: GitHub Actions
- **Monitoring**: Grafana + Prometheus

## 🔐 Seguridad y Configuración

### Variables de Entorno Requeridas
```bash
# LLM Provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Linear.app
LINEAR_API_KEY=lin_api_...
LINEAR_TEAM_ID=TEAM-...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_REPO_OWNER=tu-org
GITHUB_REPO_NAME=tu-repo

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/multiagent
```

## 📊 Monitoreo y Observabilidad

### Métricas a Rastrear
- Tiempo de ejecución por agente
- Tasa de éxito de tareas
- Costo de API LLM por tarea
- Throughput de tareas/hora
- Estado de colas Redis

### Dashboard Ejemplo
```
┌─────────────────────────────────────────┐
│  Multi-Agent System - Live Dashboard    │
├─────────────────────────────────────────┤
│  Active Tasks: 3                        │
│  Completed Today: 47                    │
│  Average Time: 6.2 min                  │
│                                         │
│  Agent Status:                          │
│  ✅ agent-01 (Architect)    - Idle      │
│  🔄 agent-02 (Frontend)     - Working   │
│  🔄 agent-03 (Backend)      - Working   │
│  ✅ agent-04 (DevOps)       - Idle      │
│  ...                                    │
│                                         │
│  Queue Depth:                           │
│  📊 tasks:agent-02: 2 pending           │
│  📊 tasks:agent-03: 1 pending           │
│                                         │
│  Recent Completions:                    │
│  ✅ PROJ-123 - Auth system (8m)        │
│  ✅ PROJ-124 - Performance opt (12m)   │
└─────────────────────────────────────────┘
```

## 🎯 Próximos Pasos para Implementación

Ver `IMPLEMENTATION_ROADMAP.md` para plan detallado de desarrollo.
