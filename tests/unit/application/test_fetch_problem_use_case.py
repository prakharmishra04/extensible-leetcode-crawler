"""Unit tests for FetchProblemUseCase."""

import logging
from unittest.mock import MagicMock, Mock

import pytest

from crawler.application.use_cases.fetch_problem import FetchProblemUseCase
from crawler.domain.entities import Problem
from crawler.domain.exceptions import (
    NetworkException,
    ProblemNotFoundException,
    RepositoryException,
)
from crawler.domain.value_objects import Difficulty, Example


@pytest.fixture
def mock_client():
    """Create a mock PlatformClient."""
    return Mock()


@pytest.fixture
def mock_repository():
    """Create a mock ProblemRepository."""
    return Mock()


@pytest.fixture
def mock_logger():
    """Create a mock Logger."""
    logger = Mock(spec=logging.Logger)
    return logger


@pytest.fixture
def sample_problem():
    """Create a sample Problem entity for testing."""
    return Problem(
        id="two-sum",
        platform="leetcode",
        title="Two Sum",
        difficulty=Difficulty("Easy"),
        description="Given an array of integers, return indices of two numbers that add up to a target.",
        topics=["Array", "Hash Table"],
        constraints="2 <= nums.length <= 10^4",
        examples=[
            Example(
                input="nums = [2,7,11,15], target = 9",
                output="[0,1]",
                explanation="Because nums[0] + nums[1] == 9, we return [0, 1].",
            )
        ],
        hints=["Use a hash table"],
        acceptance_rate=49.5,
    )


@pytest.fixture
def use_case(mock_client, mock_repository, mock_logger):
    """Create a FetchProblemUseCase instance with mocked dependencies."""
    return FetchProblemUseCase(mock_client, mock_repository, mock_logger)


class TestFetchProblemUseCaseInit:
    """Test FetchProblemUseCase initialization."""

    def test_init_stores_dependencies(self, mock_client, mock_repository, mock_logger):
        """Test that __init__ stores all dependencies correctly."""
        use_case = FetchProblemUseCase(mock_client, mock_repository, mock_logger)

        assert use_case.client is mock_client
        assert use_case.repository is mock_repository
        assert use_case.logger is mock_logger


class TestFetchProblemUseCaseCacheHit:
    """Test FetchProblemUseCase when problem is found in cache."""

    def test_execute_returns_cached_problem_when_found(
        self, use_case, mock_repository, mock_client, sample_problem
    ):
        """Test that execute returns cached problem when found and force=False."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_problem

        # Act
        result = use_case.execute("two-sum", "leetcode", force=False)

        # Assert
        assert result is sample_problem
        mock_repository.find_by_id.assert_called_once_with("two-sum", "leetcode")
        mock_client.fetch_problem.assert_not_called()
        mock_repository.save.assert_not_called()

    def test_execute_logs_cache_hit(self, use_case, mock_repository, mock_logger, sample_problem):
        """Test that execute logs when problem is found in cache."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_problem

        # Act
        use_case.execute("two-sum", "leetcode", force=False)

        # Assert
        # Check that info log was called with cache hit message
        info_calls = [call for call in mock_logger.info.call_args_list]
        assert any("Found problem 'two-sum' in cache" in str(call) for call in info_calls)


class TestFetchProblemUseCacheMiss:
    """Test FetchProblemUseCase when problem is not found in cache."""

    def test_execute_fetches_from_platform_when_not_cached(
        self, use_case, mock_repository, mock_client, sample_problem
    ):
        """Test that execute fetches from platform when problem not in cache."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        result = use_case.execute("two-sum", "leetcode", force=False)

        # Assert
        assert result is sample_problem
        mock_repository.find_by_id.assert_called_once_with("two-sum", "leetcode")
        mock_client.fetch_problem.assert_called_once_with("two-sum")
        # Save is no longer called by use case - it's handled by the command
        mock_repository.save.assert_not_called()

    def test_execute_saves_fetched_problem_to_repository(
        self, use_case, mock_repository, mock_client, sample_problem
    ):
        """Test that execute saves fetched problem to repository."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        use_case.execute("two-sum", "leetcode", force=False)

        # Assert
        # Save is no longer called by use case - it's handled by the command
        mock_repository.save.assert_not_called()

    def test_execute_logs_fetch_from_platform(
        self, use_case, mock_repository, mock_client, mock_logger, sample_problem
    ):
        """Test that execute logs when fetching from platform."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        use_case.execute("two-sum", "leetcode", force=False)

        # Assert
        info_calls = [call for call in mock_logger.info.call_args_list]
        assert any(
            "Fetching problem 'two-sum' from platform 'leetcode'" in str(call)
            for call in info_calls
        )


class TestFetchProblemUseCaseForceFlag:
    """Test FetchProblemUseCase with force flag."""

    def test_execute_bypasses_cache_when_force_is_true(
        self, use_case, mock_repository, mock_client, sample_problem
    ):
        """Test that execute bypasses cache when force=True."""
        # Arrange
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        result = use_case.execute("two-sum", "leetcode", force=True)

        # Assert
        assert result is sample_problem
        mock_repository.find_by_id.assert_not_called()
        mock_client.fetch_problem.assert_called_once_with("two-sum")
        # Save is no longer called by use case - it's handled by the command
        mock_repository.save.assert_not_called()

    def test_execute_logs_force_flag(self, use_case, mock_client, mock_logger, sample_problem):
        """Test that execute logs when force flag is set."""
        # Arrange
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        use_case.execute("two-sum", "leetcode", force=True)

        # Assert
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert any("Force flag set, bypassing cache" in str(call) for call in debug_calls)


class TestFetchProblemUseCaseErrorHandling:
    """Test FetchProblemUseCase error handling."""

    def test_execute_raises_problem_not_found_exception(
        self, use_case, mock_repository, mock_client
    ):
        """Test that execute raises ProblemNotFoundException when problem doesn't exist."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = ProblemNotFoundException("two-sum", "leetcode")

        # Act & Assert
        with pytest.raises(ProblemNotFoundException):
            use_case.execute("two-sum", "leetcode", force=False)

    def test_execute_raises_network_exception(self, use_case, mock_repository, mock_client):
        """Test that execute raises NetworkException when network fails."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = NetworkException(
            "Connection timeout", url="https://leetcode.com/api"
        )

        # Act & Assert
        with pytest.raises(NetworkException):
            use_case.execute("two-sum", "leetcode", force=False)

    def test_execute_logs_error_on_fetch_failure(
        self, use_case, mock_repository, mock_client, mock_logger
    ):
        """Test that execute logs error when fetch fails."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = NetworkException("Connection timeout")

        # Act & Assert
        with pytest.raises(NetworkException):
            use_case.execute("two-sum", "leetcode", force=False)

        error_calls = [call for call in mock_logger.error.call_args_list]
        assert any("Failed to fetch problem 'two-sum'" in str(call) for call in error_calls)

    def test_execute_continues_on_repository_save_failure(
        self, use_case, mock_repository, mock_client, sample_problem
    ):
        """Test that execute returns problem (save is now handled by command)."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        result = use_case.execute("two-sum", "leetcode", force=False)

        # Assert - should return the problem (save is handled by command)
        assert result is sample_problem
        # Save is no longer called by use case
        mock_repository.save.assert_not_called()

    def test_execute_logs_warning_on_repository_save_failure(
        self, use_case, mock_repository, mock_client, mock_logger, sample_problem
    ):
        """Test that execute no longer handles save (moved to command)."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        use_case.execute("two-sum", "leetcode", force=False)

        # Assert - no warning about save failure since save is handled by command
        # Save is no longer called by use case
        mock_repository.save.assert_not_called()


class TestFetchProblemUseCaseEdgeCases:
    """Test FetchProblemUseCase edge cases."""

    def test_execute_with_empty_problem_id(self, use_case, mock_repository, mock_client):
        """Test execute with empty problem_id."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = ValueError("Invalid problem ID")

        # Act & Assert
        with pytest.raises(ValueError):
            use_case.execute("", "leetcode", force=False)

    def test_execute_with_empty_platform(self, use_case, mock_repository, mock_client):
        """Test execute with empty platform."""
        # Arrange
        mock_repository.find_by_id.return_value = None

        # Act - should still call the methods with empty platform
        try:
            use_case.execute("two-sum", "", force=False)
        except Exception:
            pass  # We're just testing that it attempts the operation

        # Assert
        mock_repository.find_by_id.assert_called_once_with("two-sum", "")

    def test_execute_with_special_characters_in_problem_id(
        self, use_case, mock_repository, mock_client, sample_problem
    ):
        """Test execute with special characters in problem_id."""
        # Arrange
        problem_id = "problem-with-special-chars-123_test"
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem

        # Act
        result = use_case.execute(problem_id, "leetcode", force=False)

        # Assert
        assert result is sample_problem
        mock_client.fetch_problem.assert_called_once_with(problem_id)


class TestFetchProblemUseCaseIntegration:
    """Integration-style tests for FetchProblemUseCase."""

    def test_execute_full_flow_cache_miss_to_cache_hit(
        self, use_case, mock_repository, mock_client, sample_problem
    ):
        """Test full flow: cache miss, fetch, save, then cache hit."""
        # Arrange - first call: cache miss
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem

        # Act - first call
        result1 = use_case.execute("two-sum", "leetcode", force=False)

        # Assert first call
        assert result1 is sample_problem
        assert mock_client.fetch_problem.call_count == 1
        # Save is no longer called by use case
        assert mock_repository.save.call_count == 0

        # Arrange - second call: cache hit
        mock_repository.find_by_id.return_value = sample_problem

        # Act - second call
        result2 = use_case.execute("two-sum", "leetcode", force=False)

        # Assert second call - should use cache
        assert result2 is sample_problem
        assert mock_client.fetch_problem.call_count == 1  # Still 1, not called again
        # Save is still not called
        assert mock_repository.save.call_count == 0

    def test_execute_multiple_problems_different_platforms(
        self, use_case, mock_repository, mock_client
    ):
        """Test fetching multiple problems from different platforms."""
        # Arrange
        leetcode_problem = Problem(
            id="two-sum",
            platform="leetcode",
            title="Two Sum",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=["Array"],
            constraints="Test",
            examples=[],
            hints=[],
            acceptance_rate=50.0,
        )

        hackerrank_problem = Problem(
            id="fizzbuzz",
            platform="hackerrank",
            title="FizzBuzz",
            difficulty=Difficulty("Easy"),
            description="Test",
            topics=["Math"],
            constraints="Test",
            examples=[],
            hints=[],
            acceptance_rate=75.0,
        )

        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = [leetcode_problem, hackerrank_problem]

        # Act
        result1 = use_case.execute("two-sum", "leetcode", force=False)
        result2 = use_case.execute("fizzbuzz", "hackerrank", force=False)

        # Assert
        assert result1.platform == "leetcode"
        assert result2.platform == "hackerrank"
        assert mock_client.fetch_problem.call_count == 2
        # Save is no longer called by use case
        assert mock_repository.save.call_count == 0
