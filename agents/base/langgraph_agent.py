"""
LangChain Agent Base with Tools and RAG
Base class for all specialized agents using LangChain
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.tools import Tool, StructuredTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.callbacks import get_openai_callback

# Import integrations
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from integrations.linear.client import LinearClient
from integrations.github.client import GitHubClient, AgentGitHubWorkflow, FileChange
from graphs.state import AgentState, AgentResult

logger = logging.getLogger(__name__)


# Pydantic schemas for structured tools
class WriteFileInput(BaseModel):
    """Input schema for write_file tool"""
    path: str = Field(description="Path to the file to write")
    content: str = Field(description="Content to write to the file")


class LangChainAgentBase(ABC):
    """
    Base agent using LangChain for LLM orchestration
    
    Features:
    - LangChain AgentExecutor with tools
    - RAG knowledge base (ChromaDB)
    - Linear/GitHub integration
    - Automatic token tracking
    - Structured output
    
    To create a specialized agent:
    ```python
    class FrontendAgent(LangChainAgentBase):
        def __init__(self, config):
            super().__init__('agent-02-frontend', config)
        
        def _get_system_prompt(self) -> str:
            return "You are Elena, frontend specialist..."
        
        def _create_custom_tools(self) -> List[Tool]:
            return [Tool(...), ...]
    ```
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        
        # Agent metadata
        self.name = config.get('name', agent_id)
        self.role = config.get('role', 'Specialist')
        self.specialization = config.get('specialization', '')
        self.experience = config.get('experience', '30 years')
        
        # Set API key as environment variable (LangChain workaround)
        if 'openai_api_key' in config:
            os.environ['OPENAI_API_KEY'] = config['openai_api_key']
        
        # LLM
        self.llm = ChatOpenAI(
            model=config.get('model', 'gpt-4-turbo-preview'),
            temperature=config.get('temperature', 0.2)
        )
        
        # RAG vector store
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self._init_rag()
        
        # Integrations
        self.linear_client = None
        self.github_client = None
        self.github_workflow = None
        self._init_integrations()
        
        # Create agent
        self.tools = self._create_all_tools()
        self.prompt = self._create_prompt()
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )
        
        logger.info(f"🤖 {self.name} initialized with {len(self.tools)} tools")
    
    def _init_rag(self):
        """Initialize RAG vector store"""
        try:
            rag_dir = f".agents/rag-knowledge/individual/{self.agent_id}"
            
            # Load RAG documents
            if os.path.exists(f"{rag_dir}-rag.json"):
                with open(f"{rag_dir}-rag.json", 'r') as f:
                    rag_data = json.load(f)
                
                # Convert to LangChain documents
                documents = []
                for pattern in rag_data.get('patterns', []):
                    doc = Document(
                        page_content=f"{pattern['title']}: {pattern['description']}",
                        metadata=pattern
                    )
                    documents.append(doc)
                
                # Create vector store
                persist_dir = f".rag_store/{self.agent_id}"
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=persist_dir
                )
                
                logger.info(f"✅ RAG initialized with {len(documents)} patterns")
        except Exception as e:
            logger.warning(f"⚠️  RAG initialization failed: {e}")
    
    def _init_integrations(self):
        """Initialize Linear and GitHub clients"""
        try:
            if self.config.get('linear_api_key'):
                self.linear_client = LinearClient(self.config['linear_api_key'])
            
            if self.config.get('github_token') and self.config.get('github_repo'):
                self.github_client = GitHubClient(
                    token=self.config['github_token'],
                    repo=self.config['github_repo']
                )
                self.github_workflow = AgentGitHubWorkflow(
                    self.github_client,
                    self.agent_id
                )
        except Exception as e:
            logger.error(f"❌ Integration init failed: {e}")
    
    def _create_all_tools(self) -> List[Tool]:
        """Create all tools for the agent"""
        tools = []
        
        # Common tools
        tools.extend(self._create_file_tools())
        tools.extend(self._create_rag_tools())
        
        # Custom tools (implemented by subclass)
        tools.extend(self._create_custom_tools())
        
        return tools
    
    def _create_file_tools(self) -> List[Tool]:
        """Create file I/O tools"""
        return [
            Tool(
                name="read_file",
                func=self._read_file,
                description="Read contents of a file. Input: file path"
            ),
            StructuredTool.from_function(
                func=self._write_file_structured,
                name="write_file",
                description="Write content to a file",
                args_schema=WriteFileInput
            ),
            Tool(
                name="list_files",
                func=self._list_files,
                description="List files in a directory. Input: directory path"
            )
        ]
    
    def _create_rag_tools(self) -> List[Tool]:
        """Create RAG search tools"""
        return [
            Tool(
                name="search_knowledge",
                func=self._search_rag,
                description="Search your knowledge base for patterns and best practices. Input: search query"
            )
        ]
    
    @abstractmethod
    def _create_custom_tools(self) -> List[Tool]:
        """Create agent-specific tools - implemented by subclasses"""
        return []
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create agent prompt"""
        system_prompt = self._get_system_prompt()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get system prompt - implemented by subclasses"""
        pass
    
    # ═══════════════════════════════════════════════════════════
    # TOOL IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════
    
    def _read_file(self, path: str) -> str:
        """Read file tool"""
        try:
            full_path = os.path.join(self.config.get('project_path', ''), path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File content ({len(content)} chars):\n\n{content}"
        except Exception as e:
            return f"Error reading file: {e}"
    
    def _write_file(self, input_json: str) -> str:
        """Write file tool (legacy - kept for compatibility)"""
        try:
            data = json.loads(input_json)
            path = data['path']
            content = data['content']
            
            full_path = os.path.join(self.config.get('project_path', ''), path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ File written: {path} ({len(content)} chars)"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def _write_file_structured(self, path: str, content: str) -> str:
        """Write file tool (structured with Pydantic)"""
        try:
            full_path = os.path.join(self.config.get('project_path', ''), path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ File written: {path} ({len(content)} chars)"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def _list_files(self, directory: str) -> str:
        """List files tool"""
        try:
            full_path = os.path.join(self.config.get('project_path', ''), directory)
            files = os.listdir(full_path)
            return f"Files in {directory}:\n" + "\n".join(f"  - {f}" for f in files)
        except Exception as e:
            return f"Error listing files: {e}"
    
    def _search_rag(self, query: str) -> str:
        """Search RAG knowledge base"""
        try:
            if not self.vector_store:
                return "No knowledge base available"
            
            results = self.vector_store.similarity_search(query, k=3)
            
            if not results:
                return "No relevant patterns found"
            
            output = "Relevant patterns from your knowledge base:\n\n"
            for i, doc in enumerate(results, 1):
                output += f"{i}. {doc.page_content}\n"
                if doc.metadata.get('approach'):
                    output += f"   Approach: {doc.metadata['approach']}\n"
                output += "\n"
            
            return output
        except Exception as e:
            return f"Error searching knowledge: {e}"
    
    # ═══════════════════════════════════════════════════════════
    # MAIN EXECUTION
    # ═══════════════════════════════════════════════════════════
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute agent task - this is called by LangGraph as a node
        
        Args:
            state: Current graph state
        
        Returns:
            Updated state
        """
        logger.info(f"🚀 {self.name} starting execution")
        
        try:
            # Build input from state
            input_text = self._build_input(state)
            
            # Execute with token tracking
            with get_openai_callback() as cb:
                result = await self.executor.ainvoke({
                    "input": input_text
                })
            
            # Parse output
            agent_result = self._parse_output(result['output'], cb)
            
            # Update Linear if needed
            if state.get('linear_sub_issues', {}).get(self.agent_id):
                await self._update_linear(
                    state['linear_sub_issues'][self.agent_id],
                    agent_result
                )
            
            # Push to GitHub if has code changes
            if agent_result.get('files_created') or agent_result.get('files_modified'):
                pr_info = await self._push_to_github(state, agent_result)
                agent_result['pr_url'] = pr_info.get('url', '')
                agent_result['branch_name'] = pr_info.get('branch', '')
            
            # Update state
            state['agent_results'][self.agent_id] = agent_result
            state['completed_agents'].append(self.agent_id)
            state['messages'].append(f"✅ {self.name} completed")
            state['total_tokens_used'] += cb.total_tokens
            state['total_cost_usd'] += cb.total_cost
            
            logger.info(f"✅ {self.name} completed successfully")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ {self.name} failed: {e}", exc_info=True)
            
            state['failed_agents'].append(self.agent_id)
            state['messages'].append(f"❌ {self.name} failed: {str(e)}")
            
            return state
    
    def _build_input(self, state: AgentState) -> str:
        """Build input text from state"""
        input_parts = [
            f"# Task\n{state['task_description']}\n",
            f"# Project\nPath: {state['project_path']}\n",
        ]
        
        # Add previous agent results
        if state.get('agent_results'):
            input_parts.append("# Previous Agent Results:")
            for agent_id, result in state['agent_results'].items():
                input_parts.append(f"\n## {agent_id}")
                input_parts.append(f"{result.get('summary', 'No summary')}")
        
        input_parts.append("\n# Your Task")
        input_parts.append("Implement your part of the solution following best practices.")
        input_parts.append("Use your tools to read/write files and search your knowledge base.")
        
        return "\n".join(input_parts)
    
    def _parse_output(self, output: str, callback) -> AgentResult:
        """Parse agent output into structured result"""
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.name,
            success=True,
            summary=output[:500],  # Truncate
            files_modified=[],
            files_created=[],
            files_deleted=[],
            branch_name='',
            pr_url='',
            commits=[],
            issue_id='',
            issue_updated=False,
            tokens_used=callback.total_tokens,
            cost_usd=callback.total_cost,
            execution_time=0.0,
            error_message='',
            needs_retry=False
        )
    
    async def _update_linear(self, issue_id: str, result: AgentResult):
        """Update Linear issue"""
        if not self.linear_client:
            return
        
        try:
            await self.linear_client.create_comment(
                issue_id=issue_id,
                body=f"""✅ **{self.name}** completed

{result['summary']}

**Tokens used**: {result['tokens_used']:,}
**Cost**: ${result['cost_usd']:.4f}
"""
            )
        except Exception as e:
            logger.error(f"Failed to update Linear: {e}")
    
    async def _push_to_github(self, state: AgentState, result: AgentResult) -> Dict:
        """Push changes to GitHub"""
        if not self.github_workflow:
            return {}
        
        try:
            # Create branch
            branch = self.github_workflow.create_agent_branch(
                task_id=state['task_id'],
                description=state['task_title']
            )
            
            # TODO: Commit files (need to extract from result)
            
            # Create PR
            pr = self.github_workflow.create_agent_pr(
                branch=branch,
                task_title=state['task_title'],
                task_summary=result['summary'],
                linear_issue_url=state.get('linear_main_issue_url')
            )
            
            return {'url': pr.html_url, 'branch': branch}
            
        except Exception as e:
            logger.error(f"Failed to push to GitHub: {e}")
            return {}


if __name__ == "__main__":
    print("LangChainAgentBase is an abstract class. Use a concrete implementation.")
