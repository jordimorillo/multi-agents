"""
GitHub Integration Client
PyGithub wrapper for branch management, commits, and pull requests
"""

import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging
from github import Github, GithubException
from github.Repository import Repository
from github.PullRequest import PullRequest as GHPullRequest
from github.GitRef import GitRef

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents a file change to commit"""
    path: str
    content: str
    commit_message: str


@dataclass
class PullRequest:
    """Pull request representation"""
    number: int
    html_url: str
    title: str
    body: str
    head_branch: str
    base_branch: str
    state: str


class GitHubClient:
    """
    Client for GitHub API operations
    
    Usage:
        client = GitHubClient(
            token="ghp_...",
            repo="owner/repo-name"
        )
        
        await client.create_branch("feature/new-auth")
        await client.commit_file(
            branch="feature/new-auth",
            path="src/auth.py",
            content="# OAuth code",
            message="feat: add OAuth"
        )
        pr = await client.create_pull_request(
            head="feature/new-auth",
            base="main",
            title="Add OAuth authentication"
        )
    """
    
    def __init__(self, token: str, repo: str, base_url: str = "https://api.github.com"):
        """
        Initialize GitHub client
        
        Args:
            token: GitHub personal access token
            repo: Repository in format "owner/repo-name"
            base_url: GitHub API base URL (for GitHub Enterprise)
        """
        self.github = Github(token, base_url=base_url)
        self.repo: Repository = self.github.get_repo(repo)
        self.repo_name = repo
        logger.info(f"✅ GitHub client initialized for {repo}")
    
    def create_branch(self, branch_name: str, from_branch: str = "main") -> GitRef:
        """
        Create a new branch
        
        Args:
            branch_name: Name of the new branch
            from_branch: Source branch to branch from (default: main)
        
        Returns:
            GitRef object
        """
        try:
            # Get source branch
            source = self.repo.get_branch(from_branch)
            
            # Create new branch
            ref = self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )
            
            logger.info(f"✅ Created branch: {branch_name} from {from_branch}")
            return ref
            
        except GithubException as e:
            if e.status == 422:
                logger.warning(f"⚠️  Branch {branch_name} already exists")
                return self.repo.get_git_ref(f"heads/{branch_name}")
            logger.error(f"❌ Failed to create branch: {e}")
            raise
    
    def commit_file(
        self,
        branch: str,
        path: str,
        content: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Create or update a file with a commit
        
        Args:
            branch: Target branch
            path: File path (e.g., "src/components/Login.tsx")
            content: File content
            message: Commit message
        
        Returns:
            Dict with commit info
        """
        try:
            # Try to get existing file
            try:
                file = self.repo.get_contents(path, ref=branch)
                # Update existing file
                result = self.repo.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=file.sha,
                    branch=branch
                )
                logger.info(f"✅ Updated file: {path} on {branch}")
            except GithubException as e:
                if e.status == 404:
                    # Create new file
                    result = self.repo.create_file(
                        path=path,
                        message=message,
                        content=content,
                        branch=branch
                    )
                    logger.info(f"✅ Created file: {path} on {branch}")
                else:
                    raise
            
            return {
                "commit": result["commit"].sha,
                "path": path,
                "branch": branch
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to commit file {path}: {e}")
            raise
    
    def commit_multiple_files(
        self,
        branch: str,
        files: List[FileChange],
        commit_message: str
    ) -> str:
        """
        Commit multiple files in a single commit
        
        Args:
            branch: Target branch
            files: List of FileChange objects
            commit_message: Overall commit message
        
        Returns:
            Commit SHA
        """
        try:
            # Get the branch ref
            ref = self.repo.get_git_ref(f"heads/{branch}")
            base_tree = self.repo.get_git_tree(ref.object.sha)
            
            # Create tree with all files
            tree_elements = []
            for file_change in files:
                blob = self.repo.create_git_blob(file_change.content, "utf-8")
                tree_elements.append({
                    "path": file_change.path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob.sha
                })
            
            tree = self.repo.create_git_tree(tree_elements, base_tree)
            
            # Create commit
            parent = self.repo.get_git_commit(ref.object.sha)
            commit = self.repo.create_git_commit(
                message=commit_message,
                tree=tree,
                parents=[parent]
            )
            
            # Update ref
            ref.edit(commit.sha)
            
            logger.info(f"✅ Committed {len(files)} files to {branch}: {commit.sha[:7]}")
            return commit.sha
            
        except Exception as e:
            logger.error(f"❌ Failed to commit multiple files: {e}")
            raise
    
    def create_pull_request(
        self,
        head: str,
        base: str,
        title: str,
        body: str = "",
        draft: bool = False
    ) -> PullRequest:
        """
        Create a pull request
        
        Args:
            head: Head branch (source)
            base: Base branch (target, usually "main")
            title: PR title
            body: PR description (supports Markdown)
            draft: Create as draft PR
        
        Returns:
            PullRequest object
        """
        try:
            pr: GHPullRequest = self.repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base,
                draft=draft
            )
            
            logger.info(f"✅ Created PR #{pr.number}: {pr.html_url}")
            
            return PullRequest(
                number=pr.number,
                html_url=pr.html_url,
                title=pr.title,
                body=pr.body,
                head_branch=pr.head.ref,
                base_branch=pr.base.ref,
                state=pr.state
            )
            
        except GithubException as e:
            logger.error(f"❌ Failed to create PR: {e}")
            raise
    
    def add_pr_comment(self, pr_number: int, comment: str):
        """
        Add a comment to a pull request
        
        Args:
            pr_number: PR number
            comment: Comment body (Markdown supported)
        """
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            logger.info(f"✅ Added comment to PR #{pr_number}")
        except Exception as e:
            logger.error(f"❌ Failed to add PR comment: {e}")
            raise
    
    def add_pr_labels(self, pr_number: int, labels: List[str]):
        """
        Add labels to a pull request
        
        Args:
            pr_number: PR number
            labels: List of label names
        """
        try:
            pr = self.repo.get_pull(pr_number)
            issue = self.repo.get_issue(pr_number)  # PRs are issues too
            issue.add_to_labels(*labels)
            logger.info(f"✅ Added labels to PR #{pr_number}: {labels}")
        except Exception as e:
            logger.error(f"❌ Failed to add PR labels: {e}")
            raise
    
    def request_review(self, pr_number: int, reviewers: List[str]):
        """
        Request review from users
        
        Args:
            pr_number: PR number
            reviewers: List of GitHub usernames
        """
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_review_request(reviewers=reviewers)
            logger.info(f"✅ Requested review from: {reviewers}")
        except Exception as e:
            logger.error(f"❌ Failed to request review: {e}")
            raise
    
    def merge_pull_request(
        self,
        pr_number: int,
        commit_message: Optional[str] = None,
        merge_method: str = "merge"
    ):
        """
        Merge a pull request
        
        Args:
            pr_number: PR number
            commit_message: Optional custom merge commit message
            merge_method: "merge", "squash", or "rebase"
        """
        try:
            pr = self.repo.get_pull(pr_number)
            pr.merge(
                commit_message=commit_message,
                merge_method=merge_method
            )
            logger.info(f"✅ Merged PR #{pr_number} using {merge_method}")
        except Exception as e:
            logger.error(f"❌ Failed to merge PR: {e}")
            raise
    
    def delete_branch(self, branch_name: str):
        """
        Delete a branch
        
        Args:
            branch_name: Branch name to delete
        """
        try:
            ref = self.repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
            logger.info(f"✅ Deleted branch: {branch_name}")
        except Exception as e:
            logger.error(f"❌ Failed to delete branch: {e}")
            raise
    
    def get_file_content(self, path: str, ref: str = "main") -> str:
        """
        Get file content from repository
        
        Args:
            path: File path
            ref: Branch or commit SHA (default: main)
        
        Returns:
            File content as string
        """
        try:
            file = self.repo.get_contents(path, ref=ref)
            content = file.decoded_content.decode("utf-8")
            return content
        except Exception as e:
            logger.error(f"❌ Failed to get file {path}: {e}")
            raise


class AgentGitHubWorkflow:
    """
    High-level workflow for agent GitHub operations
    Combines multiple operations into agent-friendly workflows
    """
    
    def __init__(self, client: GitHubClient, agent_id: str):
        self.client = client
        self.agent_id = agent_id
    
    def create_agent_branch(self, task_id: str, description: str) -> str:
        """Create a branch for an agent task"""
        branch_name = f"agent/{self.agent_id}/{task_id}"
        self.client.create_branch(branch_name)
        return branch_name
    
    def commit_agent_work(
        self,
        branch: str,
        files: List[FileChange],
        task_description: str
    ) -> str:
        """Commit all agent file changes"""
        commit_message = f"feat({self.agent_id}): {task_description}"
        return self.client.commit_multiple_files(branch, files, commit_message)
    
    def create_agent_pr(
        self,
        branch: str,
        task_title: str,
        task_summary: str,
        linear_issue_url: Optional[str] = None
    ) -> PullRequest:
        """Create a PR from agent work"""
        body = f"""## 🤖 Automated Implementation by {self.agent_id}

{task_summary}

---

### Changes Made:
- Implementation completed by AI agent
- Code reviewed and tested automatically
- Ready for human review

"""
        if linear_issue_url:
            body += f"\n**Linear Issue**: {linear_issue_url}\n"
        
        body += f"\n_Generated by Multi-Agent System_"
        
        pr = self.client.create_pull_request(
            head=branch,
            base="main",
            title=f"feat: {task_title}",
            body=body,
            draft=False
        )
        
        # Add agent label
        self.client.add_pr_labels(pr.number, ["automated", "ai-generated"])
        
        return pr


# Example usage
def example_usage():
    """Example of how to use GitHubClient"""
    client = GitHubClient(
        token=os.getenv("GITHUB_TOKEN"),
        repo="owner/repo-name"
    )
    
    # Create branch
    branch_name = "agent/backend-specialist/auth-oauth"
    client.create_branch(branch_name, from_branch="main")
    
    # Single file commit
    client.commit_file(
        branch=branch_name,
        path="src/auth/oauth.py",
        content="# OAuth implementation\n\ndef login():\n    pass",
        message="feat: add OAuth login endpoint"
    )
    
    # Multiple files commit
    files = [
        FileChange(
            path="src/auth/oauth.py",
            content="# OAuth code",
            commit_message="OAuth implementation"
        ),
        FileChange(
            path="src/auth/__init__.py",
            content="from .oauth import login",
            commit_message="Export OAuth"
        ),
        FileChange(
            path="tests/test_oauth.py",
            content="# OAuth tests",
            commit_message="OAuth tests"
        )
    ]
    
    commit_sha = client.commit_multiple_files(
        branch=branch_name,
        files=files,
        commit_message="feat: complete OAuth implementation with tests"
    )
    
    # Create PR
    pr = client.create_pull_request(
        head=branch_name,
        base="main",
        title="feat: OAuth authentication system",
        body="""## Implementation Details

Implemented OAuth 2.0 authentication with:
- Login endpoint
- Callback handler
- Unit tests

**Linear**: LINEAR-123
"""
    )
    
    print(f"Created PR: {pr.html_url}")
    
    # Add labels and request review
    client.add_pr_labels(pr.number, ["feature", "authentication", "automated"])
    client.request_review(pr.number, ["reviewer1", "reviewer2"])


if __name__ == "__main__":
    example_usage()
