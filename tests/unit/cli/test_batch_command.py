"""
Unit tests for the BatchDownloadCommand.

This module tests the BatchDownloadCommand implementation, including:
- Successful batch download scenarios
- Error handling for various exceptions
- Input validation
- Argument parser configuration
- Statistics reporting
"""

from logging import Logger
from unittest.mock import Mock

import pytest

from crawler.application.use_cases.batch_download import DownloadStats
from crawler.cli.commands.base import CommandResult
from crawler.cli.commands.batch import BatchDownloadCommand
from crawler.domain.entities import Problem, UpdateMode
from crawler.domain.exceptions import (
    AuthenticationException,
    NetworkException,
    ProblemNotFoundException,
    RepositoryException,
    UnsupportedPlatformException,
)
from crawler.domain.value_objects import Difficulty, Example


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
def mock_observers():
    """Create a list of mock observers."""
    return [Mock(), Mock()]


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock(spec=Logger)


@pytest.fixture
def sample_problems():
    """Create sample problems for testing."""
    return [
        Problem(
            id="two-sum",
            platform="leetcode",
            title="Two Sum",
            difficulty=Difficulty("Easy"),
            description="Find two numbers that add up to target.",
            topics=["Array", "Hash Table"],
            constraints="2 <= nums.length <= 10^4",
            examples=[Example("nums = [2,7,11,15], target = 9", "[0,1]")],
            hints=["Use a hash map"],
            acceptance_rate=49.1,
        ),
        Problem(
            id="add-two-numbers",
            platform="leetcode",
            title="Add Two Numbers",
            difficulty=Difficulty("Medium"),
            description="Add two numbers represented by linked lists.",
            topics=["Linked List", "Math"],
            constraints="1 <= l1.length, l2.length <= 100",
            examples=[Example("l1 = [2,4,3], l2 = [5,6,4]", "[7,0,8]")],
            hints=["Handle carry"],
            acceptance_rate=38.5,
        ),
        Problem(
            id="median-of-two-sorted-arrays",
            platform="leetcode",
            title="Median of Two Sorted Arrays",
            difficulty=Difficulty("Hard"),
            description="Find median of two sorted arrays.",
            topics=["Array", "Binary Search"],
            constraints="0 <= nums1.length, nums2.length <= 1000",
            examples=[Example("nums1 = [1,3], nums2 = [2]", "2.0")],
            hints=["Use binary search"],
            acceptance_rate=35.2,
        ),
    ]


class TestBatchDownloadCommandSuccess:
    """Test successful batch download scenarios."""

    def test_execute_success_all_downloaded(
        self,
        mock_client,
        mock_repository,
        mock_formatter,
        mock_observers,
        mock_logger,
        sample_problems,
    ):
        """Test successful batch download with all problems downloaded."""
        # Arrange
        mock_client.fetch_solved_problems.return_value = sample_problems
        mock_client.fetch_problem.side_effect = sample_problems
        mock_client.fetch_submission.return_value = Mock()
        mock_repository.exists.return_value = False

        command = BatchDownloadCommand(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=None,
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "Successfully downloaded 3 problem(s)" in result.message
        assert isinstance(result.data, DownloadStats)
        assert result.data.total == 3
        assert result.data.downloaded == 3
        assert result.data.skipped == 0
        assert result.data.failed == 0
        assert result.error is None

    def test_execute_success_with_skipped(
        self,
        mock_client,
        mock_repository,
        mock_formatter,
        mock_observers,
        mock_logger,
        sample_problems,
    ):
        """Test batch download with some problems skipped."""
        # Arrange
        mock_client.fetch_solved_problems.return_value = sample_problems
        mock_client.fetch_problem.side_effect = sample_problems
        mock_client.fetch_submission.return_value = Mock()
        # First problem exists, others don't
        mock_repository.exists.side_effect = [True, False, False]

        command = BatchDownloadCommand(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=None,
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "2 problem(s)" in result.message
        assert "1 skipped" in result.message
        assert isinstance(result.data, DownloadStats)
        assert result.data.total == 3
        assert result.data.downloaded == 2
        assert result.data.skipped == 1
        assert result.data.failed == 0

    def test_execute_success_with_difficulty_filter(
        self,
        mock_client,
        mock_repository,
        mock_formatter,
        mock_observers,
        mock_logger,
        sample_problems,
    ):
        """Test batch download with difficulty filter."""
        # Arrange
        mock_client.fetch_solved_problems.return_value = sample_problems
        # Only Easy and Medium problems should be downloaded
        easy_medium = [p for p in sample_problems if p.difficulty.level in ["Easy", "Medium"]]
        mock_client.fetch_problem.side_effect = easy_medium
        mock_client.fetch_submission.return_value = Mock()
        mock_repository.exists.return_value = False

        command = BatchDownloadCommand(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=["Easy", "Medium"],
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert isinstance(result.data, DownloadStats)
        assert result.data.total == 2  # Only Easy and Medium
        assert result.data.downloaded == 2

    def test_execute_success_with_topic_filter(
        self,
        mock_client,
        mock_repository,
        mock_formatter,
        mock_observers,
        mock_logger,
        sample_problems,
    ):
        """Test batch download with topic filter."""
        # Arrange
        mock_client.fetch_solved_problems.return_value = sample_problems
        # Only problems with "Array" topic
        array_problems = [p for p in sample_problems if "Array" in p.topics]
        mock_client.fetch_problem.side_effect = array_problems
        mock_client.fetch_submission.return_value = Mock()
        mock_repository.exists.return_value = False

        command = BatchDownloadCommand(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=None,
            topic_filter=["Array"],
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert isinstance(result.data, DownloadStats)
        assert result.data.total == 2  # Two problems have "Array" topic
        assert result.data.downloaded == 2


class TestBatchDownloadCommandErrors:
    """Test error handling scenarios."""

    def test_execute_user_not_found(
        self, mock_client, mock_repository, mock_formatter, mock_observers, mock_logger
    ):
        """Test handling of user not found."""
        # Arrange
        mock_client.fetch_solved_problems.side_effect = ProblemNotFoundException(
            "nonexistent_user", "leetcode"
        )

        command = BatchDownloadCommand(
            username="nonexistent_user",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=None,
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "not found" in result.message
        assert "nonexistent_user" in result.message
        assert isinstance(result.error, ProblemNotFoundException)

    def test_execute_authentication_error(
        self, mock_client, mock_repository, mock_formatter, mock_observers, mock_logger
    ):
        """Test handling of authentication error."""
        # Arrange
        mock_client.fetch_solved_problems.side_effect = AuthenticationException(
            "leetcode", "Invalid session token"
        )

        command = BatchDownloadCommand(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=None,
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Authentication failed" in result.message
        assert "credentials" in result.message
        assert isinstance(result.error, AuthenticationException)

    def test_execute_network_error(
        self, mock_client, mock_repository, mock_formatter, mock_observers, mock_logger
    ):
        """Test handling of network error."""
        # Arrange
        mock_client.fetch_solved_problems.side_effect = NetworkException(
            "Connection timeout", url="https://leetcode.com/api", status_code=504
        )

        command = BatchDownloadCommand(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=None,
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Network error" in result.message
        assert "504" in result.message
        assert isinstance(result.error, NetworkException)


class TestBatchDownloadCommandValidation:
    """Test input validation."""

    def test_validate_empty_username(
        self, mock_client, mock_repository, mock_formatter, mock_observers, mock_logger
    ):
        """Test validation of empty username."""
        # Arrange
        command = BatchDownloadCommand(
            username="",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=None,
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "cannot be empty" in result.message.lower()
        assert isinstance(result.error, ValueError)

    def test_validate_invalid_difficulty(
        self, mock_client, mock_repository, mock_formatter, mock_observers, mock_logger
    ):
        """Test validation of invalid difficulty filter."""
        # Arrange
        command = BatchDownloadCommand(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=["Invalid"],
            topic_filter=None,
            limit=None,
            include_community=False,
            output_format="python",
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=mock_observers,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Invalid difficulty" in result.message
        assert isinstance(result.error, ValueError)


class TestBatchDownloadCommandArgumentParser:
    """Test argument parser configuration."""

    def test_create_argument_parser(self):
        """Test that argument parser is created correctly."""
        # Act
        parser = BatchDownloadCommand.create_argument_parser()

        # Assert
        assert parser is not None
        assert parser.description is not None

    def test_parse_required_arguments(self):
        """Test parsing of required arguments."""
        # Arrange
        parser = BatchDownloadCommand.create_argument_parser()

        # Act
        args = parser.parse_args(["john_doe", "--platform", "leetcode", "--mode", "skip"])

        # Assert
        assert args.username == "john_doe"
        assert args.platform == "leetcode"
        assert args.mode == "skip"
        assert args.format == "python"
        assert args.include_community is False

    def test_parse_with_difficulty_filter(self):
        """Test parsing with difficulty filter."""
        # Arrange
        parser = BatchDownloadCommand.create_argument_parser()

        # Act
        args = parser.parse_args(
            [
                "john_doe",
                "--platform",
                "leetcode",
                "--mode",
                "update",
                "--difficulty",
                "Easy",
                "Medium",
            ]
        )

        # Assert
        assert args.difficulty == ["Easy", "Medium"]

    def test_parse_with_topic_filter(self):
        """Test parsing with topic filter."""
        # Arrange
        parser = BatchDownloadCommand.create_argument_parser()

        # Act
        args = parser.parse_args(
            [
                "john_doe",
                "--platform",
                "leetcode",
                "--mode",
                "force",
                "--topics",
                "Array",
                "Hash Table",
            ]
        )

        # Assert
        assert args.topics == ["Array", "Hash Table"]

    def test_parse_all_arguments(self):
        """Test parsing of all arguments."""
        # Arrange
        parser = BatchDownloadCommand.create_argument_parser()

        # Act
        args = parser.parse_args(
            [
                "john_doe",
                "--platform",
                "leetcode",
                "--mode",
                "update",
                "--difficulty",
                "Easy",
                "Medium",
                "--topics",
                "Array",
                "--include-community",
                "--format",
                "markdown",
            ]
        )

        # Assert
        assert args.username == "john_doe"
        assert args.platform == "leetcode"
        assert args.mode == "update"
        assert args.difficulty == ["Easy", "Medium"]
        assert args.topics == ["Array"]
        assert args.include_community is True
        assert args.format == "markdown"
