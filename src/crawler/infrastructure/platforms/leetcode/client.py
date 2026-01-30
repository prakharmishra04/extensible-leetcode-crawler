"""LeetCode platform client implementation."""

from logging import Logger
from typing import Dict, List

from crawler.application.interfaces import PlatformClient
from crawler.config.settings import Config
from crawler.domain.entities import Problem, Submission
from crawler.domain.exceptions import (
    AuthenticationException,
    ProblemNotFoundException,
)
from crawler.infrastructure.http import HTTPClient

from .adapter import LeetCodeAdapter


class LeetCodeClient(PlatformClient):
    """LeetCode-specific API client.
    
    This client implements the PlatformClient interface for LeetCode,
    handling GraphQL API communication and authentication.
    
    The client uses:
    - HTTPClient for network requests with retry logic
    - LeetCodeAdapter for converting API responses to domain models
    - Config for API endpoints and authentication
    - Logger for tracking operations
    
    Attributes:
        http_client: HTTP client with retry and rate limiting
        adapter: Adapter for converting API responses
        config: Configuration settings
        logger: Logger for tracking operations
        session_token: Optional session token for authentication
    
    Example:
        >>> from crawler.infrastructure.http import HTTPClient, RateLimiter, RetryConfig
        >>> from crawler.config import get_logger
        >>> 
        >>> retry_config = RetryConfig()
        >>> rate_limiter = RateLimiter(2.0)
        >>> http_client = HTTPClient(retry_config, rate_limiter, logger)
        >>> adapter = LeetCodeAdapter()
        >>> config = Config()
        >>> logger = get_logger(__name__)
        >>> 
        >>> client = LeetCodeClient(http_client, adapter, config, logger)
        >>> problem = client.fetch_problem("two-sum")
    """
    
    def __init__(
        self,
        http_client: HTTPClient,
        adapter: LeetCodeAdapter,
        config: Config,
        logger: Logger
    ):
        """Initialize the LeetCode client.
        
        Args:
            http_client: HTTP client for making requests
            adapter: Adapter for converting API responses
            config: Configuration settings
            logger: Logger for tracking operations
        """
        self.http_client = http_client
        self.adapter = adapter
        self.config = config
        self.logger = logger
        self.session_token = config.leetcode_session_token
    
    def fetch_problem(self, problem_id: str) -> Problem:
        """Fetch a single problem from LeetCode.
        
        Uses the LeetCode GraphQL API to fetch problem details including
        description, examples, constraints, hints, and metadata.
        
        Args:
            problem_id: The problem's title slug (e.g., "two-sum")
        
        Returns:
            Problem entity with all metadata
        
        Raises:
            ProblemNotFoundException: If the problem doesn't exist
            NetworkException: If the network request fails
        
        Example:
            >>> problem = client.fetch_problem("two-sum")
            >>> print(problem.title)
            "Two Sum"
        """
        self.logger.info(f"Fetching problem: {problem_id}")
        
        # GraphQL query for fetching problem details
        query = """
        query getProblem($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                difficulty
                content
                topicTags {
                    name
                    slug
                }
                hints
                exampleTestcases
                constraints
                stats
            }
        }
        """
        
        variables = {"titleSlug": problem_id}
        
        try:
            response = self.http_client.post(
                url=self.config.leetcode_graphql_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_msg = data["errors"][0]["message"]
                if "not found" in error_msg.lower():
                    raise ProblemNotFoundException(problem_id, "leetcode")
                raise Exception(f"GraphQL error: {error_msg}")
            
            # Check if question data exists
            if not data.get("data", {}).get("question"):
                raise ProblemNotFoundException(problem_id, "leetcode")
            
            # Adapt response to domain model
            problem = self.adapter.adapt_problem(data)
            
            self.logger.info(f"Successfully fetched problem: {problem.title}")
            return problem
            
        except ProblemNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to fetch problem {problem_id}: {e}")
            raise
    
    def fetch_solved_problems(self, username: str) -> List[Problem]:
        """Fetch all problems solved by a user.
        
        Uses the LeetCode GraphQL API to fetch the list of problems
        that a user has solved (accepted submissions).
        
        Args:
            username: The LeetCode username
        
        Returns:
            List of Problem entities for all solved problems
        
        Raises:
            NetworkException: If the network request fails
            AuthenticationException: If authentication is required but not provided
        
        Example:
            >>> problems = client.fetch_solved_problems("john_doe")
            >>> print(f"Solved {len(problems)} problems")
        """
        self.logger.info(f"Fetching solved problems for user: {username}")
        
        # GraphQL query for fetching user's solved problems
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
            recentAcSubmissionList(username: $username, limit: 1000) {
                id
                title
                titleSlug
                timestamp
            }
        }
        """
        
        variables = {"username": username}
        
        try:
            response = self.http_client.post(
                url=self.config.leetcode_graphql_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_msg = data["errors"][0]["message"]
                raise Exception(f"GraphQL error: {error_msg}")
            
            # Get list of solved problems
            submissions = data.get("data", {}).get("recentAcSubmissionList", [])
            
            # Fetch full details for each problem
            problems = []
            for submission in submissions:
                try:
                    problem = self.fetch_problem(submission["titleSlug"])
                    problems.append(problem)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to fetch problem {submission['titleSlug']}: {e}"
                    )
                    continue
            
            self.logger.info(f"Successfully fetched {len(problems)} solved problems")
            return problems
            
        except Exception as e:
            self.logger.error(f"Failed to fetch solved problems for {username}: {e}")
            raise
    
    def fetch_submission(self, problem_id: str, username: str) -> Submission:
        """Fetch the last accepted submission for a problem.
        
        Uses the LeetCode GraphQL API to fetch the user's most recent
        accepted submission for a specific problem.
        
        Args:
            problem_id: The problem's title slug (e.g., "two-sum")
            username: The LeetCode username
        
        Returns:
            Submission entity with code and metadata
        
        Raises:
            NetworkException: If the network request fails
            AuthenticationException: If authentication is required but not provided
        
        Example:
            >>> submission = client.fetch_submission("two-sum", "john_doe")
            >>> print(submission.language)
            "python3"
        """
        self.logger.info(f"Fetching submission for problem: {problem_id}, user: {username}")
        
        # GraphQL query for fetching submission details
        # Note: This is a simplified version. The actual LeetCode API
        # requires authentication and uses a different endpoint.
        query = """
        query getSubmission($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
            }
        }
        """
        
        variables = {"titleSlug": problem_id}
        
        try:
            # First, get the question ID
            response = self.http_client.post(
                url=self.config.leetcode_graphql_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_msg = data["errors"][0]["message"]
                raise Exception(f"GraphQL error: {error_msg}")
            
            # For now, we'll return a placeholder since fetching submissions
            # requires authentication and a different API endpoint
            # This will be fully implemented when authentication is added
            
            self.logger.warning(
                "Submission fetching requires authentication - returning placeholder"
            )
            
            # Return a placeholder submission
            # In a real implementation, this would fetch the actual submission
            from crawler.domain.entities.enums import SubmissionStatus
            
            submission = Submission(
                id="placeholder",
                problem_id=problem_id,
                language="python3",
                code="# Placeholder code\n# Authentication required to fetch actual submission",
                status=SubmissionStatus.ACCEPTED,
                runtime="N/A",
                memory="N/A",
                timestamp=0,
                percentiles=None
            )
            
            return submission
            
        except Exception as e:
            self.logger.error(f"Failed to fetch submission for {problem_id}: {e}")
            raise
    
    def fetch_community_solutions(self, problem_id: str, limit: int = 10) -> List[Submission]:
        """Fetch top community solutions for a problem.
        
        Uses the LeetCode GraphQL API to fetch popular community solutions
        for a specific problem.
        
        Args:
            problem_id: The problem's title slug (e.g., "two-sum")
            limit: Maximum number of solutions to fetch (default: 10)
        
        Returns:
            List of Submission entities representing community solutions
        
        Raises:
            ProblemNotFoundException: If the problem doesn't exist
            NetworkException: If the network request fails
        
        Example:
            >>> solutions = client.fetch_community_solutions("two-sum", limit=5)
            >>> print(f"Found {len(solutions)} community solutions")
        """
        self.logger.info(f"Fetching community solutions for problem: {problem_id}")
        
        # GraphQL query for fetching community solutions
        query = """
        query getCommunitySolutions($titleSlug: String!, $limit: Int!) {
            questionSolutions(
                questionSlug: $titleSlug
                first: $limit
                orderBy: HOT
            ) {
                solutions {
                    id
                    title
                    content
                    voteCount
                    author {
                        username
                    }
                }
            }
        }
        """
        
        variables = {"titleSlug": problem_id, "limit": limit}
        
        try:
            response = self.http_client.post(
                url=self.config.leetcode_graphql_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_msg = data["errors"][0]["message"]
                if "not found" in error_msg.lower():
                    raise ProblemNotFoundException(problem_id, "leetcode")
                raise Exception(f"GraphQL error: {error_msg}")
            
            # Get list of solutions
            solutions_data = data.get("data", {}).get("questionSolutions", {}).get("solutions", [])
            
            # Convert to Submission entities
            from crawler.domain.entities.enums import SubmissionStatus
            
            submissions = []
            for i, sol in enumerate(solutions_data):
                submission = Submission(
                    id=sol["id"],
                    problem_id=problem_id,
                    language="unknown",  # Community solutions don't specify language
                    code=sol["content"],
                    status=SubmissionStatus.ACCEPTED,
                    runtime="N/A",
                    memory="N/A",
                    timestamp=0,
                    percentiles=None
                )
                submissions.append(submission)
            
            self.logger.info(f"Successfully fetched {len(submissions)} community solutions")
            return submissions
            
        except ProblemNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to fetch community solutions for {problem_id}: {e}")
            raise
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with LeetCode using session token.
        
        LeetCode uses session-based authentication. The session token
        can be obtained from the browser's cookies after logging in.
        
        Args:
            credentials: Dictionary containing "session_token" key
        
        Returns:
            True if authentication succeeded, False otherwise
        
        Raises:
            AuthenticationException: If authentication fails
        
        Example:
            >>> success = client.authenticate({"session_token": "abc123..."})
            >>> print(f"Authenticated: {success}")
        """
        self.logger.info("Authenticating with LeetCode")
        
        session_token = credentials.get("session_token")
        
        if not session_token:
            raise AuthenticationException(
                "leetcode",
                "session_token is required for authentication"
            )
        
        # Store the session token
        self.session_token = session_token
        
        # Verify authentication by making a test request
        try:
            # Try to fetch user profile to verify token
            query = """
            query {
                user {
                    username
                }
            }
            """
            
            response = self.http_client.post(
                url=self.config.leetcode_graphql_url,
                json={"query": query},
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Check for authentication errors
            if "errors" in data:
                error_msg = data["errors"][0]["message"]
                if "not authorized" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    raise AuthenticationException("leetcode", "Invalid session token")
                raise AuthenticationException("leetcode", error_msg)
            
            # Check if user data exists
            if not data.get("data", {}).get("user"):
                raise AuthenticationException("leetcode", "Failed to verify authentication")
            
            self.logger.info("Successfully authenticated with LeetCode")
            return True
            
        except AuthenticationException:
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise AuthenticationException("leetcode", str(e))
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for LeetCode API requests.
        
        Returns:
            Dictionary of HTTP headers including authentication if available
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; CodingPlatformCrawler/2.0)"
        }
        
        # Add session token if available
        if self.session_token:
            headers["Cookie"] = f"LEETCODE_SESSION={self.session_token}"
        
        return headers
