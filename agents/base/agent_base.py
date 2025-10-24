"""
Base Agent Framework
Abstract class that all specialized agents inherit from
"""

import os
import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import integrations
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from integrations.linear.client import LinearClient
from integrations.github.client import GitHubClient, AgentGitHubWorkflow, FileChange

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of task execution"""
    success: bool
    summary: str
    file_changes: List[FileChange]
    pr_title: Optional[str] = None
    pr_body: Optional[str] = None
    has_code_changes: bool = True
    error: Optional[str] = None
    llm_tokens_used: int = 0
    execution_time_seconds: float = 0.0


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system
    
    Each agent:
    - Runs as an independent process
    - Consumes tasks from its Redis queue
    - Updates Linear issues automatically
    - Creates GitHub branches/commits/PRs
    - Reports completion/errors
    
    To create a new agent:
    ```python
    class MyAgent(BaseAgent):
        def __init__(self, config):
            super().__init__('my-agent-id', config)
            self.specialization = "My specialization"
        
        async def execute_task(self, task_data, rag_context):
            # Implement task logic
            return TaskResult(...)
    ```
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.running = False
        self.current_task = None
        
        # Initialize clients
        self.redis_client: Optional[redis.Redis] = None
        self.linear_client: Optional[LinearClient] = None
        self.github_client: Optional[GitHubClient] = None
        self.github_workflow: Optional[AgentGitHubWorkflow] = None
        
        # Database
        self.db_engine = None
        self.db_session_factory = None
        
        # LLM client (to be implemented by subclasses)
        self.llm_client = None
        
        # Agent metadata
        self.name = config.get('name', agent_id)
        self.role = config.get('role', 'Specialist')
        self.specialization = config.get('specialization', '')
        
        logger.info(f"🤖 Initializing agent: {self.name} ({self.agent_id})")
    
    async def initialize(self):
        """Initialize all connections and clients"""
        try:
            # Redis connection
            self.redis_client = redis.from_url(
                self.config['redis_url'],
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info(f"✅ Redis connected")
            
            # Linear client
            if self.config.get('linear_api_key'):
                self.linear_client = LinearClient(self.config['linear_api_key'])
                logger.info(f"✅ Linear client initialized")
            
            # GitHub client
            if self.config.get('github_token') and self.config.get('github_repo'):
                self.github_client = GitHubClient(
                    token=self.config['github_token'],
                    repo=self.config['github_repo']
                )
                self.github_workflow = AgentGitHubWorkflow(
                    self.github_client,
                    self.agent_id
                )
                logger.info(f"✅ GitHub client initialized")
            
            # Database
            if self.config.get('database_url'):
                self.db_engine = create_async_engine(
                    self.config['database_url'],
                    echo=False
                )
                self.db_session_factory = sessionmaker(
                    self.db_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                logger.info(f"✅ Database connected")
            
            # LLM initialization (subclass responsibility)
            await self.initialize_llm()
            
            # Update agent status in DB
            await self.update_agent_status('idle')
            
            logger.info(f"✅ {self.name} fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    @abstractmethod
    async def initialize_llm(self):
        """Initialize LLM client - implemented by subclasses"""
        pass
    
    async def start(self):
        """Start the agent main loop"""
        await self.initialize()
        
        self.running = True
        logger.info(f"🚀 {self.name} started - waiting for tasks...")
        
        try:
            await self.run_loop()
        except KeyboardInterrupt:
            logger.info(f"⚠️  {self.name} received shutdown signal")
        finally:
            await self.shutdown()
    
    async def run_loop(self):
        """Main event loop - consume and process tasks"""
        queue_name = f"tasks:{self.agent_id}"
        group_name = f"{self.agent_id}-workers"
        consumer_name = f"{self.agent_id}-{os.getpid()}"
        
        # Ensure consumer group exists
        try:
            await self.redis_client.xgroup_create(
                queue_name, group_name, id='0', mkstream=True
            )
        except Exception:
            pass  # Group already exists
        
        while self.running:
            try:
                # Read messages from stream
                messages = await self.redis_client.xreadgroup(
                    groupname=group_name,
                    consumername=consumer_name,
                    streams={queue_name: '>'},
                    count=1,
                    block=1000  # 1 second timeout
                )
                
                if not messages:
                    # Heartbeat
                    await self.send_heartbeat()
                    continue
                
                # Process message
                for stream, message_list in messages:
                    for message_id, message_data in message_list:
                        await self.process_task(message_id, message_data)
                        
            except asyncio.CancelledError:
                logger.info(f"⚠️  {self.name} task cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(5)  # Back off on error
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]):
        """
        Process a single task
        
        Workflow:
        1. Update Linear: "In Progress"
        2. Load RAG knowledge
        3. Execute task with LLM
        4. Push to GitHub (if code changes)
        5. Update Linear: "Done"
        6. Notify completion
        7. ACK message
        """
        start_time = datetime.now()
        self.current_task = task_id
        
        try:
            logger.info(f"📋 Processing task: {task_data.get('title', task_id)}")
            
            # 1. Update Linear: In Progress
            linear_issue_id = task_data.get('linear_issue_id')
            if linear_issue_id and self.linear_client:
                await self.linear_client.transition_issue_to_state(
                    issue_id=linear_issue_id,
                    state_name='In Progress',
                    team_id=task_data.get('linear_team_id', '')
                )
                await self.linear_client.create_comment(
                    issue_id=linear_issue_id,
                    body=f"🤖 **{self.name}** started working on this task"
                )
            
            # Update agent status
            await self.update_agent_status('working', task_id)
            
            # 2. Load RAG knowledge
            rag_context = await self.load_rag_knowledge(task_data)
            
            # 3. Execute task (implemented by subclass)
            result = await self.execute_task(task_data, rag_context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time_seconds = execution_time
            
            if not result.success:
                raise Exception(result.error or "Task execution failed")
            
            # 4. Push to GitHub if there are code changes
            github_pr_url = None
            if result.has_code_changes and result.file_changes and self.github_workflow:
                try:
                    # Create branch
                    branch_name = self.github_workflow.create_agent_branch(
                        task_id=task_data.get('id', task_id),
                        description=task_data.get('title', 'Task')
                    )
                    
                    # Commit files
                    self.github_workflow.commit_agent_work(
                        branch=branch_name,
                        files=result.file_changes,
                        task_description=task_data.get('title', 'Task')
                    )
                    
                    # Create PR
                    pr = self.github_workflow.create_agent_pr(
                        branch=branch_name,
                        task_title=result.pr_title or task_data.get('title', 'Task'),
                        task_summary=result.summary,
                        linear_issue_url=task_data.get('linear_issue_url')
                    )
                    
                    github_pr_url = pr.html_url
                    logger.info(f"✅ Created PR: {github_pr_url}")
                    
                except Exception as e:
                    logger.error(f"⚠️  GitHub push failed: {e}")
                    # Continue anyway - don't fail the whole task
            
            # 5. Update Linear: Done
            if linear_issue_id and self.linear_client:
                comment_body = f"""✅ **Task completed by {self.name}**

{result.summary}

**Execution time**: {execution_time:.1f}s
"""
                if github_pr_url:
                    comment_body += f"\n**Pull Request**: {github_pr_url}"
                
                if result.llm_tokens_used:
                    comment_body += f"\n**Tokens used**: {result.llm_tokens_used:,}"
                
                await self.linear_client.create_comment(
                    issue_id=linear_issue_id,
                    body=comment_body
                )
                
                await self.linear_client.transition_issue_to_state(
                    issue_id=linear_issue_id,
                    state_name='Done',
                    team_id=task_data.get('linear_team_id', '')
                )
            
            # 6. Publish completion event
            await self.publish_event('task-completed', {
                'agent_id': self.agent_id,
                'task_id': task_id,
                'success': True,
                'summary': result.summary,
                'execution_time': execution_time,
                'github_pr': github_pr_url
            })
            
            # 7. ACK the message
            await self.redis_client.xack(
                f"tasks:{self.agent_id}",
                f"{self.agent_id}-workers",
                task_id
            )
            
            # Update stats
            await self.update_agent_stats(success=True, execution_time=execution_time)
            await self.update_agent_status('idle')
            
            logger.info(f"✅ Task completed successfully in {execution_time:.1f}s")
            
        except Exception as e:
            logger.error(f"❌ Task failed: {e}", exc_info=True)
            await self.handle_task_error(task_id, task_data, e)
            await self.update_agent_status('idle')
        
        finally:
            self.current_task = None
    
    @abstractmethod
    async def execute_task(
        self,
        task_data: Dict[str, Any],
        rag_context: Dict[str, Any]
    ) -> TaskResult:
        """
        Execute the task - MUST be implemented by subclasses
        
        Args:
            task_data: Task information from orchestrator
            rag_context: Relevant RAG knowledge for this task
        
        Returns:
            TaskResult with success, summary, file_changes, etc.
        """
        pass
    
    async def load_rag_knowledge(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load relevant RAG knowledge for this task"""
        try:
            rag_file = f".agents/rag-knowledge/individual/{self.agent_id}-rag.json"
            
            if os.path.exists(rag_file):
                with open(rag_file, 'r') as f:
                    rag_data = json.load(f)
                
                # Filter relevant patterns based on task
                # (Simple implementation - can be enhanced with semantic search)
                return rag_data
            
            return {}
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to load RAG knowledge: {e}")
            return {}
    
    async def handle_task_error(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        error: Exception
    ):
        """Handle task execution error"""
        # Update Linear
        linear_issue_id = task_data.get('linear_issue_id')
        if linear_issue_id and self.linear_client:
            try:
                await self.linear_client.create_comment(
                    issue_id=linear_issue_id,
                    body=f"""❌ **Task failed**

Agent: {self.name}
Error: {str(error)}

The task will be retried or escalated.
"""
                )
            except Exception as e:
                logger.error(f"Failed to update Linear on error: {e}")
        
        # Publish failure event
        await self.publish_event('task-failed', {
            'agent_id': self.agent_id,
            'task_id': task_id,
            'error': str(error)
        })
        
        # Update stats
        await self.update_agent_stats(success=False)
    
    async def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to Redis pub/sub"""
        try:
            channel = f"events:{event_type}"
            message = json.dumps({
                **data,
                'timestamp': datetime.now().isoformat(),
                'agent_id': self.agent_id
            })
            await self.redis_client.publish(channel, message)
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    async def send_heartbeat(self):
        """Send heartbeat to indicate agent is alive"""
        try:
            await self.redis_client.hset(
                f"agent:{self.agent_id}:heartbeat",
                mapping={
                    'timestamp': datetime.now().isoformat(),
                    'status': 'alive',
                    'current_task': self.current_task or 'none'
                }
            )
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
    
    async def update_agent_status(
        self,
        status: str,
        current_task_id: Optional[str] = None
    ):
        """Update agent status in database"""
        # Simplified - would use actual DB in production
        try:
            await self.redis_client.hset(
                f"agent:{self.agent_id}:status",
                mapping={
                    'status': status,
                    'current_task': current_task_id or '',
                    'updated_at': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    async def update_agent_stats(
        self,
        success: bool,
        execution_time: float = 0.0
    ):
        """Update agent statistics"""
        try:
            key = f"agent:{self.agent_id}:stats"
            if success:
                await self.redis_client.hincrby(key, 'tasks_completed', 1)
            else:
                await self.redis_client.hincrby(key, 'tasks_failed', 1)
            
            if execution_time > 0:
                await self.redis_client.hincrbyfloat(
                    key, 'total_execution_time', execution_time
                )
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info(f"🛑 Shutting down {self.name}...")
        
        self.running = False
        
        await self.update_agent_status('offline')
        
        # Close connections
        if self.redis_client:
            await self.redis_client.close()
        
        if self.db_engine:
            await self.db_engine.dispose()
        
        logger.info(f"✅ {self.name} shut down gracefully")


if __name__ == "__main__":
    logger.info("BaseAgent is an abstract class. Create a subclass to use it.")
