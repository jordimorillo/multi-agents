"""
Linear.app Integration Client
GraphQL API wrapper for creating and managing issues
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import aiohttp
import logging

logger = logging.getLogger(__name__)


@dataclass
class LinearIssue:
    """Linear issue representation"""
    id: str
    identifier: str  # e.g., "PROJ-123"
    title: str
    url: str
    state: Optional[str] = None
    description: Optional[str] = None


@dataclass
class LinearComment:
    """Linear comment representation"""
    id: str
    body: str
    created_at: str


class LinearClient:
    """
    Client for Linear.app GraphQL API
    
    Usage:
        client = LinearClient(api_key="lin_api_...")
        issue = await client.create_issue(
            team_id="TEAM-123",
            title="Implement OAuth",
            description="Add user authentication"
        )
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.linear.app/graphql"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    async def _execute_query(self, query: str, variables: Dict[str, Any] = None) -> Dict:
        """Execute GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers=self.headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Linear API error: {response.status} - {error_text}")
                
                data = await response.json()
                
                if "errors" in data:
                    raise Exception(f"GraphQL errors: {data['errors']}")
                
                return data.get("data", {})
    
    async def create_issue(
        self,
        team_id: str,
        title: str,
        description: str,
        priority: int = 3,
        assignee_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> LinearIssue:
        """
        Create a new issue in Linear
        
        Args:
            team_id: Team ID (e.g., "TEAM-123")
            title: Issue title
            description: Issue description (supports Markdown)
            priority: Priority 0-4 (0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low)
            assignee_id: User ID to assign
            parent_id: Parent issue ID (for sub-issues)
            labels: List of label IDs
        
        Returns:
            LinearIssue object
        """
        query = """
        mutation IssueCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue {
              id
              identifier
              title
              url
              state {
                name
              }
            }
          }
        }
        """
        
        variables = {
            "input": {
                "teamId": team_id,
                "title": title,
                "description": description,
                "priority": priority
            }
        }
        
        if assignee_id:
            variables["input"]["assigneeId"] = assignee_id
        if parent_id:
            variables["input"]["parentId"] = parent_id
        if labels:
            variables["input"]["labelIds"] = labels
        
        try:
            result = await self._execute_query(query, variables)
            issue_data = result["issueCreate"]["issue"]
            
            logger.info(f"✅ Created Linear issue: {issue_data['identifier']}")
            
            return LinearIssue(
                id=issue_data["id"],
                identifier=issue_data["identifier"],
                title=issue_data["title"],
                url=issue_data["url"],
                state=issue_data.get("state", {}).get("name")
            )
        except Exception as e:
            logger.error(f"❌ Failed to create Linear issue: {e}")
            raise
    
    async def update_issue(
        self,
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[int] = None
    ) -> LinearIssue:
        """
        Update an existing issue
        
        Args:
            issue_id: Issue ID to update
            title: New title (optional)
            description: New description (optional)
            state_id: State ID to transition to (optional)
            assignee_id: User ID to assign (optional)
            priority: New priority (optional)
        
        Returns:
            Updated LinearIssue object
        """
        query = """
        mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
          issueUpdate(id: $id, input: $input) {
            success
            issue {
              id
              identifier
              title
              url
              state {
                name
              }
            }
          }
        }
        """
        
        input_data = {}
        if title:
            input_data["title"] = title
        if description:
            input_data["description"] = description
        if state_id:
            input_data["stateId"] = state_id
        if assignee_id:
            input_data["assigneeId"] = assignee_id
        if priority is not None:
            input_data["priority"] = priority
        
        variables = {
            "id": issue_id,
            "input": input_data
        }
        
        try:
            result = await self._execute_query(query, variables)
            issue_data = result["issueUpdate"]["issue"]
            
            logger.info(f"✅ Updated Linear issue: {issue_data['identifier']}")
            
            return LinearIssue(
                id=issue_data["id"],
                identifier=issue_data["identifier"],
                title=issue_data["title"],
                url=issue_data["url"],
                state=issue_data.get("state", {}).get("name")
            )
        except Exception as e:
            logger.error(f"❌ Failed to update Linear issue: {e}")
            raise
    
    async def create_comment(
        self,
        issue_id: str,
        body: str
    ) -> LinearComment:
        """
        Add a comment to an issue
        
        Args:
            issue_id: Issue ID
            body: Comment body (supports Markdown)
        
        Returns:
            LinearComment object
        """
        query = """
        mutation CommentCreate($input: CommentCreateInput!) {
          commentCreate(input: $input) {
            success
            comment {
              id
              body
              createdAt
            }
          }
        }
        """
        
        variables = {
            "input": {
                "issueId": issue_id,
                "body": body
            }
        }
        
        try:
            result = await self._execute_query(query, variables)
            comment_data = result["commentCreate"]["comment"]
            
            logger.info(f"✅ Created comment on issue")
            
            return LinearComment(
                id=comment_data["id"],
                body=comment_data["body"],
                created_at=comment_data["createdAt"]
            )
        except Exception as e:
            logger.error(f"❌ Failed to create comment: {e}")
            raise
    
    async def get_workflow_states(self, team_id: str) -> List[Dict[str, str]]:
        """
        Get workflow states for a team
        
        Args:
            team_id: Team ID
        
        Returns:
            List of states with id and name
        """
        query = """
        query Team($id: String!) {
          team(id: $id) {
            states {
              nodes {
                id
                name
                type
              }
            }
          }
        }
        """
        
        variables = {"id": team_id}
        
        try:
            result = await self._execute_query(query, variables)
            states = result["team"]["states"]["nodes"]
            
            return [
                {
                    "id": state["id"],
                    "name": state["name"],
                    "type": state["type"]
                }
                for state in states
            ]
        except Exception as e:
            logger.error(f"❌ Failed to get workflow states: {e}")
            raise
    
    async def transition_issue_to_state(
        self,
        issue_id: str,
        state_name: str,
        team_id: str
    ) -> LinearIssue:
        """
        Transition issue to a specific state by name
        
        Args:
            issue_id: Issue ID
            state_name: Target state name (e.g., "In Progress", "Done")
            team_id: Team ID to get states from
        
        Returns:
            Updated LinearIssue object
        """
        # Get all states for the team
        states = await self.get_workflow_states(team_id)
        
        # Find state by name
        target_state = next(
            (s for s in states if s["name"].lower() == state_name.lower()),
            None
        )
        
        if not target_state:
            raise ValueError(f"State '{state_name}' not found. Available: {[s['name'] for s in states]}")
        
        # Update issue with new state
        return await self.update_issue(issue_id, state_id=target_state["id"])
    
    async def create_sub_issue(
        self,
        parent_id: str,
        team_id: str,
        title: str,
        description: str,
        assignee_id: Optional[str] = None
    ) -> LinearIssue:
        """
        Create a sub-issue (child of another issue)
        
        Args:
            parent_id: Parent issue ID
            team_id: Team ID
            title: Sub-issue title
            description: Sub-issue description
            assignee_id: Optional assignee
        
        Returns:
            LinearIssue object
        """
        return await self.create_issue(
            team_id=team_id,
            title=title,
            description=description,
            parent_id=parent_id,
            assignee_id=assignee_id
        )
    
    async def get_issue(self, issue_id: str) -> LinearIssue:
        """
        Get issue details
        
        Args:
            issue_id: Issue ID
        
        Returns:
            LinearIssue object
        """
        query = """
        query Issue($id: String!) {
          issue(id: $id) {
            id
            identifier
            title
            description
            url
            state {
              name
            }
          }
        }
        """
        
        variables = {"id": issue_id}
        
        try:
            result = await self._execute_query(query, variables)
            issue_data = result["issue"]
            
            return LinearIssue(
                id=issue_data["id"],
                identifier=issue_data["identifier"],
                title=issue_data["title"],
                url=issue_data["url"],
                state=issue_data.get("state", {}).get("name"),
                description=issue_data.get("description")
            )
        except Exception as e:
            logger.error(f"❌ Failed to get issue: {e}")
            raise


# Example usage
async def example_usage():
    """Example of how to use LinearClient"""
    client = LinearClient(api_key=os.getenv("LINEAR_API_KEY"))
    
    # Create main issue
    issue = await client.create_issue(
        team_id="TEAM-123",
        title="Implement user authentication",
        description="Add OAuth 2.0 authentication system",
        priority=1  # Urgent
    )
    
    print(f"Created issue: {issue.identifier} - {issue.url}")
    
    # Create sub-issues for different agents
    sub_issue_backend = await client.create_sub_issue(
        parent_id=issue.id,
        team_id="TEAM-123",
        title="Backend: OAuth endpoints",
        description="Implement /auth/login and /auth/callback endpoints"
    )
    
    sub_issue_frontend = await client.create_sub_issue(
        parent_id=issue.id,
        team_id="TEAM-123",
        title="Frontend: Login UI",
        description="Create login form and authentication flow"
    )
    
    # Update sub-issue status
    await client.transition_issue_to_state(
        issue_id=sub_issue_backend.id,
        state_name="In Progress",
        team_id="TEAM-123"
    )
    
    # Add comment
    await client.create_comment(
        issue_id=sub_issue_backend.id,
        body="🤖 Agent @backend-specialist started implementation"
    )
    
    # Mark as done
    await client.transition_issue_to_state(
        issue_id=sub_issue_backend.id,
        state_name="Done",
        team_id="TEAM-123"
    )
    
    await client.create_comment(
        issue_id=sub_issue_backend.id,
        body="✅ OAuth endpoints implemented\n\nPR: https://github.com/owner/repo/pull/123"
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
