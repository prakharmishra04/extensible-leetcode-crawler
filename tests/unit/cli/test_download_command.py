"""
Unit tests for the DownloadCommand.

This module tests the DownloadCommand implementation, including:
- Successful download scenarios
- Error handling for various exceptions
- Input validation
- Argument parser configuration
"""

import pytest
from unittest.mock import Mock, MagicMock
from logging import Logger

from crawler.cli.commands.download import DownloadCommand
from crawler.cli.commands.base import CommandResult
from crawler.domain.entities import Problem, Submission
from crawler.domain.value_objects import Difficulty, Example
from crawler.domain.exceptions import (
    AuthenticationException,
    NetworkException,
    ProblemNotFoundException,
    RepositoryException,
    UnsupportedPlatformException,
)


@pytest.fixture
def mock_client():
    """Create a mock platform client."""
    return Mock()


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return Mock()


@pytest.fixture
def mock_formatter():
    """Create a mock formatter."""
    formatter = Mock()
    formatter.get_file_extension.return_value = "py"
    return formatter


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock(spec=Logger)


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
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
                explanation="Because nums[0] + nums[1] == 9, we return [0, 1]."
            )
        ],
        hints=["Use a hash map to store complements"],
        acceptance_rate=49.1,
    )


class TestDownloadCommandSuccess:
    """Test successful download scenarios."""
    
    def test_execute_success_with_cache(
        self, mock_client, mock_repository, mock_formatter, mock_logger, sample_problem
    ):
        """Test successful download from cache."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_problem
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is True
        assert "Successfully downloaded" in result.message
        assert "Two Sum" in result.message
        assert result.data == sample_problem
        assert result.error is None
        
        # Verify cache was checked
        mock_repository.find_by_id.assert_called_once_with("two-sum", "leetcode")
        # Verify client was not called (cache hit)
        mock_client.fetch_problem.assert_not_called()
    
    def test_execute_success_with_force(
        self, mock_client, mock_repository, mock_formatter, mock_logger, sample_problem
    ):
        """Test successful download with force flag (bypass cache)."""
        # Arrange
        mock_client.fetch_problem.return_value = sample_problem
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=True,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is True
        assert "Successfully downloaded" in result.message
        assert "from platform" in result.message
        assert result.data == sample_problem
        assert result.error is None
        
        # Verify cache was not checked (force flag)
        mock_repository.find_by_id.assert_not_called()
        # Verify client was called
        mock_client.fetch_problem.assert_called_once_with("two-sum")
        # Verify problem was saved
        mock_repository.save.assert_called_once_with(sample_problem)
    
    def test_execute_success_cache_miss(
        self, mock_client, mock_repository, mock_formatter, mock_logger, sample_problem
    ):
        """Test successful download when cache misses."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is True
        assert "Successfully downloaded" in result.message
        assert result.data == sample_problem
        assert result.error is None
        
        # Verify cache was checked
        mock_repository.find_by_id.assert_called_once_with("two-sum", "leetcode")
        # Verify client was called (cache miss)
        mock_client.fetch_problem.assert_called_once_with("two-sum")
        # Verify problem was saved
        mock_repository.save.assert_called_once_with(sample_problem)


class TestDownloadCommandErrors:
    """Test error handling scenarios."""
    
    def test_execute_problem_not_found(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test handling of ProblemNotFoundException."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = ProblemNotFoundException(
            "nonexistent", "leetcode"
        )
        
        command = DownloadCommand(
            problem_id="nonexistent",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "not found" in result.message
        assert "nonexistent" in result.message
        assert isinstance(result.error, ProblemNotFoundException)
        assert result.data is None
    
    def test_execute_authentication_error(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test handling of AuthenticationException."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = AuthenticationException(
            "leetcode", "Invalid session token"
        )
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "Authentication failed" in result.message
        assert "credentials" in result.message
        assert isinstance(result.error, AuthenticationException)
        assert result.data is None
    
    def test_execute_network_error(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test handling of NetworkException."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = NetworkException(
            "Connection timeout",
            url="https://leetcode.com/api",
            status_code=504,
        )
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "Network error" in result.message
        assert "504" in result.message
        assert "https://leetcode.com/api" in result.message
        assert isinstance(result.error, NetworkException)
        assert result.data is None
    
    def test_execute_unsupported_platform(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test handling of UnsupportedPlatformException."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = UnsupportedPlatformException("unknown")
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="unknown",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "not supported" in result.message
        assert "unknown" in result.message
        assert isinstance(result.error, UnsupportedPlatformException)
        assert result.data is None
    
    def test_execute_repository_error(
        self, mock_client, mock_repository, mock_formatter, mock_logger, sample_problem
    ):
        """Test handling of RepositoryException.
        
        Note: FetchProblemUseCase doesn't raise when save() fails - it logs a warning
        and returns the problem anyway. This is by design to ensure the user gets
        the problem even if saving fails. So this test verifies success with a warning.
        """
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.return_value = sample_problem
        mock_repository.save.side_effect = RepositoryException("Disk full")
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        # FetchProblemUseCase doesn't fail when save fails - it just logs a warning
        assert result.success is True
        assert "Successfully downloaded" in result.message
        assert result.data == sample_problem
        # Verify warning was logged about save failure
        mock_logger.warning.assert_called()
    
    def test_execute_unexpected_error(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test handling of unexpected exceptions."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = RuntimeError("Unexpected error")
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "Unexpected error" in result.message
        assert "bug" in result.message
        assert isinstance(result.error, RuntimeError)
        assert result.data is None


class TestDownloadCommandValidation:
    """Test input validation."""
    
    def test_validate_empty_problem_id(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test validation of empty problem ID."""
        # Arrange
        command = DownloadCommand(
            problem_id="",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "cannot be empty" in result.message.lower()
        assert isinstance(result.error, ValueError)
    
    def test_validate_whitespace_problem_id(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test validation of whitespace-only problem ID."""
        # Arrange
        command = DownloadCommand(
            problem_id="   ",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "cannot be empty" in result.message.lower()
        assert isinstance(result.error, ValueError)
    
    def test_validate_empty_platform(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test validation of empty platform."""
        # Arrange
        command = DownloadCommand(
            problem_id="two-sum",
            platform="",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "cannot be empty" in result.message.lower()
        assert isinstance(result.error, ValueError)
    
    def test_validate_empty_output_format(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test validation of empty output format."""
        # Arrange
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        assert "cannot be empty" in result.message.lower()
        assert isinstance(result.error, ValueError)


class TestDownloadCommandArgumentParser:
    """Test argument parser configuration."""
    
    def test_create_argument_parser(self):
        """Test that argument parser is created correctly."""
        # Act
        parser = DownloadCommand.create_argument_parser()
        
        # Assert
        assert parser is not None
        assert parser.description is not None
    
    def test_parse_required_arguments(self):
        """Test parsing of required arguments."""
        # Arrange
        parser = DownloadCommand.create_argument_parser()
        
        # Act
        args = parser.parse_args(["two-sum", "--platform", "leetcode"])
        
        # Assert
        assert args.problem_id == "two-sum"
        assert args.platform == "leetcode"
        assert args.force is False
        assert args.format == "python"
    
    def test_parse_all_arguments(self):
        """Test parsing of all arguments."""
        # Arrange
        parser = DownloadCommand.create_argument_parser()
        
        # Act
        args = parser.parse_args([
            "two-sum",
            "--platform", "leetcode",
            "--force",
            "--format", "markdown",
        ])
        
        # Assert
        assert args.problem_id == "two-sum"
        assert args.platform == "leetcode"
        assert args.force is True
        assert args.format == "markdown"
    
    def test_parse_short_options(self):
        """Test parsing of short option flags."""
        # Arrange
        parser = DownloadCommand.create_argument_parser()
        
        # Act
        args = parser.parse_args([
            "two-sum",
            "-p", "leetcode",
            "-f",
        ])
        
        # Assert
        assert args.problem_id == "two-sum"
        assert args.platform == "leetcode"
        assert args.force is True
    
    def test_parse_invalid_platform(self):
        """Test that invalid platform raises error."""
        # Arrange
        parser = DownloadCommand.create_argument_parser()
        
        # Act & Assert
        with pytest.raises(SystemExit):
            parser.parse_args(["two-sum", "--platform", "invalid"])
    
    def test_parse_invalid_format(self):
        """Test that invalid format raises error."""
        # Arrange
        parser = DownloadCommand.create_argument_parser()
        
        # Act & Assert
        with pytest.raises(SystemExit):
            parser.parse_args([
                "two-sum",
                "--platform", "leetcode",
                "--format", "invalid",
            ])
    
    def test_parse_missing_platform(self):
        """Test that missing platform raises error."""
        # Arrange
        parser = DownloadCommand.create_argument_parser()
        
        # Act & Assert
        with pytest.raises(SystemExit):
            parser.parse_args(["two-sum"])


class TestDownloadCommandLogging:
    """Test logging behavior."""
    
    def test_logs_success(
        self, mock_client, mock_repository, mock_formatter, mock_logger, sample_problem
    ):
        """Test that success is logged."""
        # Arrange
        mock_repository.find_by_id.return_value = sample_problem
        
        command = DownloadCommand(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is True
        # Verify info logging was called
        assert mock_logger.info.call_count >= 2  # Start and success messages
    
    def test_logs_error(
        self, mock_client, mock_repository, mock_formatter, mock_logger
    ):
        """Test that errors are logged."""
        # Arrange
        mock_repository.find_by_id.return_value = None
        mock_client.fetch_problem.side_effect = ProblemNotFoundException(
            "nonexistent", "leetcode"
        )
        
        command = DownloadCommand(
            problem_id="nonexistent",
            platform="leetcode",
            force=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            logger=mock_logger,
        )
        
        # Act
        result = command.execute()
        
        # Assert
        assert result.success is False
        # Verify error logging was called
        mock_logger.error.assert_called()
