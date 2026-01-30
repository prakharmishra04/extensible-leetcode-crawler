"""Integration tests for LeetCode client with mocked HTTP responses."""

from unittest.mock import Mock, MagicMock
import pytest

from crawler.config import get_logger
from crawler.config.settings import Config
from crawler.domain.entities import Problem, Submission
from crawler.domain.entities.enums import SubmissionStatus
from crawler.domain.exceptions import (
    AuthenticationException,
    ProblemNotFoundException,
)
from crawler.infrastructure.http import HTTPClient, RateLimiter, RetryConfig
from crawler.infrastructure.platforms.leetcode import LeetCodeAdapter, LeetCodeClient
from tests.fixtures.api_responses import (
    get_leetcode_problem_response,
    get_leetcode_submission_response,
    get_leetcode_solved_problems_response,
    get_leetcode_community_solutions_response,
    get_leetcode_error_response,
    get_leetcode_authentication_error_response,
)


class TestLeetCodeClient:
    """Integration tests for LeetCodeClient with mocked HTTP."""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HTTPClient)
    
    @pytest.fixture
    def adapter(self):
        """Create a LeetCodeAdapter instance."""
        return LeetCodeAdapter()
    
    @pytest.fixture
    def config(self):
        """Create a Config instance."""
        return Config()
    
    @pytest.fixture
    def logger(self):
        """Create a logger instance."""
        return get_logger(__name__)
    
    @pytest.fixture
    def client(self, mock_http_client, adapter, config, logger):
        """Create a LeetCodeClient instance with mocked HTTP."""
        return LeetCodeClient(mock_http_client, adapter, config, logger)
    
    def test_fetch_problem_success(self, client, mock_http_client):
        """Test successfully fetching a problem."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = get_leetcode_problem_response()
        mock_http_client.post.return_value = mock_response
        
        # Fetch problem
        problem = client.fetch_problem("two-sum")
        
        # Verify result
        assert isinstance(problem, Problem)
        assert problem.id == "two-sum"
        assert problem.title == "Two Sum"
        assert problem.platform == "leetcode"
        assert problem.difficulty.level == "Easy"
        
        # Verify HTTP client was called correctly
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert call_args[1]["url"] == "https://leetcode.com/graphql"
        assert "query" in call_args[1]["json"]
        assert "variables" in call_args[1]["json"]
        assert call_args[1]["json"]["variables"]["titleSlug"] == "two-sum"
    
    def test_fetch_problem_not_found(self, client, mock_http_client):
        """Test fetching a non-existent problem."""
        # Setup mock response with error
        mock_response = Mock()
        mock_response.json.return_value = get_leetcode_error_response()
        mock_http_client.post.return_value = mock_response
        
        # Attempt to fetch problem
        with pytest.raises(ProblemNotFoundException) as exc_info:
            client.fetch_problem("non-existent-problem")
        
        assert exc_info.value.problem_id == "non-existent-problem"
        assert exc_info.value.platform == "leetcode"
    
    def test_fetch_problem_with_authentication(self, client, mock_http_client):
        """Test fetching a problem with authentication token."""
        # Set session token
        client.session_token = "test_session_token"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = get_leetcode_problem_response()
        mock_http_client.post.return_value = mock_response
        
        # Fetch problem
        problem = client.fetch_problem("two-sum")
        
        # Verify authentication header was included
        call_args = mock_http_client.post.call_args
        headers = call_args[1]["headers"]
        assert "Cookie" in headers
        assert "LEETCODE_SESSION=test_session_token" in headers["Cookie"]
    
    def test_fetch_solved_problems_success(self, client, mock_http_client):
        """Test successfully fetching solved problems."""
        # Setup mock responses
        # First call: get solved problems list
        solved_response = Mock()
        solved_response.json.return_value = get_leetcode_solved_problems_response()
        
        # Subsequent calls: get individual problem details
        problem_response = Mock()
        problem_response.json.return_value = get_leetcode_problem_response()
        
        # Configure mock to return different responses
        mock_http_client.post.side_effect = [
            solved_response,
            problem_response,
            problem_response,
            problem_response,
        ]
        
        # Fetch solved problems
        problems = client.fetch_solved_problems("testuser")
        
        # Verify results
        assert isinstance(problems, list)
        assert len(problems) == 3  # Three problems in the mock response
        assert all(isinstance(p, Problem) for p in problems)
        
        # Verify HTTP client was called multiple times
        assert mock_http_client.post.call_count == 4  # 1 for list + 3 for details
    
    def test_fetch_submission_returns_placeholder(self, client, mock_http_client):
        """Test fetching submission returns placeholder (auth required)."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = get_leetcode_problem_response()
        mock_http_client.post.return_value = mock_response
        
        # Fetch submission
        submission = client.fetch_submission("two-sum", "testuser")
        
        # Verify placeholder submission is returned
        assert isinstance(submission, Submission)
        assert submission.problem_id == "two-sum"
        assert submission.status == SubmissionStatus.ACCEPTED
        assert "Placeholder" in submission.code or "Authentication required" in submission.code
    
    def test_fetch_community_solutions_success(self, client, mock_http_client):
        """Test successfully fetching community solutions."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = get_leetcode_community_solutions_response()
        mock_http_client.post.return_value = mock_response
        
        # Fetch community solutions
        solutions = client.fetch_community_solutions("two-sum", limit=5)
        
        # Verify results
        assert isinstance(solutions, list)
        assert len(solutions) == 2  # Two solutions in the mock response
        assert all(isinstance(s, Submission) for s in solutions)
        assert all(s.problem_id == "two-sum" for s in solutions)
        assert all(s.status == SubmissionStatus.ACCEPTED for s in solutions)
        
        # Verify HTTP client was called correctly
        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"]["variables"]["titleSlug"] == "two-sum"
        assert call_args[1]["json"]["variables"]["limit"] == 5
    
    def test_fetch_community_solutions_not_found(self, client, mock_http_client):
        """Test fetching community solutions for non-existent problem."""
        # Setup mock response with error
        mock_response = Mock()
        mock_response.json.return_value = get_leetcode_error_response()
        mock_http_client.post.return_value = mock_response
        
        # Attempt to fetch solutions
        with pytest.raises(ProblemNotFoundException):
            client.fetch_community_solutions("non-existent-problem")
    
    def test_authenticate_success(self, client, mock_http_client):
        """Test successful authentication."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "user": {
                    "username": "testuser"
                }
            }
        }
        mock_http_client.post.return_value = mock_response
        
        # Authenticate
        result = client.authenticate({"session_token": "valid_token"})
        
        # Verify authentication succeeded
        assert result is True
        assert client.session_token == "valid_token"
        
        # Verify HTTP client was called
        mock_http_client.post.assert_called_once()
    
    def test_authenticate_invalid_token(self, client, mock_http_client):
        """Test authentication with invalid token."""
        # Setup mock response with auth error
        mock_response = Mock()
        mock_response.json.return_value = get_leetcode_authentication_error_response()
        mock_http_client.post.return_value = mock_response
        
        # Attempt to authenticate
        with pytest.raises(AuthenticationException) as exc_info:
            client.authenticate({"session_token": "invalid_token"})
        
        assert exc_info.value.platform == "leetcode"
        assert "Invalid session token" in str(exc_info.value) or "not authorized" in str(exc_info.value).lower()
    
    def test_authenticate_missing_token(self, client, mock_http_client):
        """Test authentication without providing token."""
        # Attempt to authenticate without token
        with pytest.raises(AuthenticationException) as exc_info:
            client.authenticate({})
        
        assert exc_info.value.platform == "leetcode"
        assert "session_token is required" in exc_info.value.reason
    
    def test_get_headers_without_auth(self, client):
        """Test getting headers without authentication."""
        headers = client._get_headers()
        
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers
        assert "Cookie" not in headers
    
    def test_get_headers_with_auth(self, client):
        """Test getting headers with authentication."""
        client.session_token = "test_token"
        
        headers = client._get_headers()
        
        assert "Content-Type" in headers
        assert "User-Agent" in headers
        assert "Cookie" in headers
        assert "LEETCODE_SESSION=test_token" in headers["Cookie"]
    
    def test_fetch_problem_handles_graphql_error(self, client, mock_http_client):
        """Test handling of GraphQL errors."""
        # Setup mock response with generic error
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [
                {
                    "message": "Internal server error",
                    "extensions": {"code": "INTERNAL_ERROR"}
                }
            ]
        }
        mock_http_client.post.return_value = mock_response
        
        # Attempt to fetch problem
        with pytest.raises(Exception) as exc_info:
            client.fetch_problem("two-sum")
        
        assert "GraphQL error" in str(exc_info.value)
    
    def test_fetch_problem_handles_empty_response(self, client, mock_http_client):
        """Test handling of empty response."""
        # Setup mock response with no question data
        mock_response = Mock()
        mock_response.json.return_value = {"data": {}}
        mock_http_client.post.return_value = mock_response
        
        # Attempt to fetch problem
        with pytest.raises(ProblemNotFoundException):
            client.fetch_problem("two-sum")
    
    def test_fetch_solved_problems_handles_partial_failures(self, client, mock_http_client):
        """Test that partial failures in batch fetching are handled gracefully."""
        # Setup mock responses
        solved_response = Mock()
        solved_response.json.return_value = get_leetcode_solved_problems_response()
        
        problem_response = Mock()
        problem_response.json.return_value = get_leetcode_problem_response()
        
        error_response = Mock()
        error_response.json.return_value = get_leetcode_error_response()
        
        # Configure mock: first call succeeds, second fails, third succeeds
        mock_http_client.post.side_effect = [
            solved_response,
            problem_response,
            error_response,  # This one fails
            problem_response,
        ]
        
        # Fetch solved problems
        problems = client.fetch_solved_problems("testuser")
        
        # Verify that we got 2 problems (1 failed)
        assert isinstance(problems, list)
        assert len(problems) == 2
        assert all(isinstance(p, Problem) for p in problems)


class TestLeetCodeClientIntegration:
    """Integration tests with real HTTP client (but still mocked network)."""
    
    @pytest.fixture
    def real_http_client(self):
        """Create a real HTTP client with mocked session."""
        retry_config = RetryConfig(max_retries=1, initial_delay=0.1)
        rate_limiter = RateLimiter(requests_per_second=10.0)
        logger = get_logger(__name__)
        
        client = HTTPClient(retry_config, rate_limiter, logger)
        
        # Mock the session to avoid real network calls
        client.session = Mock()
        
        return client
    
    @pytest.fixture
    def client(self, real_http_client):
        """Create a LeetCodeClient with real HTTP client."""
        adapter = LeetCodeAdapter()
        config = Config()
        logger = get_logger(__name__)
        
        return LeetCodeClient(real_http_client, adapter, config, logger)
    
    def test_fetch_problem_with_retry_logic(self, client, real_http_client):
        """Test that retry logic is applied through real HTTP client."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = get_leetcode_problem_response()
        real_http_client.session.request.return_value = mock_response
        
        # Fetch problem
        problem = client.fetch_problem("two-sum")
        
        # Verify result
        assert isinstance(problem, Problem)
        assert problem.id == "two-sum"
        
        # Verify HTTP request was made
        real_http_client.session.request.assert_called()
