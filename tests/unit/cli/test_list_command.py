"""
Unit tests for the ListCommand.

This module tests the ListCommand implementation, including:
- Successful listing scenarios with various filters
- Error handling for various exceptions
- Input validation
- Argument parser configuration
"""

from logging import Logger
from unittest.mock import Mock

import pytest

from crawler.cli.commands.base import CommandResult
from crawler.cli.commands.list import ListCommand
from crawler.domain.entities import Problem
from crawler.domain.exceptions import RepositoryException
from crawler.domain.value_objects import Difficulty, Example


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return Mock()


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock(spec=Logger)


@pytest.fixture
def sample_problems():
    """Create a list of sample problems for testing."""
    return [
        Problem(
            id="two-sum",
            platform="leetcode",
            title="Two Sum",
            difficulty=Difficulty("Easy"),
            description="Given an array of integers, return indices.",
            topics=["Array", "Hash Table"],
            constraints="2 <= nums.length <= 10^4",
            examples=[
                Example(
                    input="nums = [2,7,11,15], target = 9",
                    output="[0,1]",
                    explanation="Because nums[0] + nums[1] == 9",
                )
            ],
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
            examples=[
                Example(
                    input="l1 = [2,4,3], l2 = [5,6,4]",
                    output="[7,0,8]",
                    explanation="342 + 465 = 807",
                )
            ],
            hints=["Handle carry"],
            acceptance_rate=38.5,
        ),
        Problem(
            id="median-of-two-sorted-arrays",
            platform="leetcode",
            title="Median of Two Sorted Arrays",
            difficulty=Difficulty("Hard"),
            description="Find the median of two sorted arrays.",
            topics=["Array", "Binary Search"],
            constraints="nums1.length + nums2.length >= 1",
            examples=[
                Example(
                    input="nums1 = [1,3], nums2 = [2]",
                    output="2.0",
                    explanation="merged array = [1,2,3] and median is 2",
                )
            ],
            hints=["Use binary search"],
            acceptance_rate=35.2,
        ),
    ]


class TestListCommandSuccess:
    """Test successful listing scenarios."""

    def test_execute_success_no_filters(self, mock_repository, mock_logger, sample_problems):
        """Test successful listing with no filters."""
        # Arrange
        mock_repository.list_all.return_value = sample_problems

        command = ListCommand(
            platform=None,
            difficulty_filter=None,
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "Found 3 problems" in result.message
        assert "no filters" not in result.message  # Should not mention filters
        assert len(result.data) == 3
        # Verify problems are sorted by ID (alphabetically)
        assert result.data[0].id == "add-two-numbers"
        assert result.data[1].id == "median-of-two-sorted-arrays"
        assert result.data[2].id == "two-sum"
        assert result.error is None

        # Verify repository was called
        mock_repository.list_all.assert_called_once_with(None)

    def test_execute_success_with_platform_filter(
        self, mock_repository, mock_logger, sample_problems
    ):
        """Test successful listing with platform filter."""
        # Arrange
        mock_repository.list_all.return_value = sample_problems

        command = ListCommand(
            platform="leetcode",
            difficulty_filter=None,
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "Found 3 problems" in result.message
        assert "platform=leetcode" in result.message
        assert len(result.data) == 3
        # Verify problems are sorted by ID (alphabetically)
        assert result.data[0].id == "add-two-numbers"
        assert result.data[1].id == "median-of-two-sorted-arrays"
        assert result.data[2].id == "two-sum"
        assert result.error is None

        # Verify repository was called with platform
        mock_repository.list_all.assert_called_once_with("leetcode")

    def test_execute_success_with_difficulty_filter(
        self, mock_repository, mock_logger, sample_problems
    ):
        """Test successful listing with difficulty filter."""
        # Arrange
        # Mock repository returns all problems, use case will filter
        mock_repository.list_all.return_value = sample_problems

        command = ListCommand(
            platform=None,
            difficulty_filter=["Easy", "Medium"],
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "Found 2 problems" in result.message
        assert "difficulty=Easy, Medium" in result.message
        assert len(result.data) == 2
        assert all(p.difficulty.level in ["Easy", "Medium"] for p in result.data)
        assert result.error is None

    def test_execute_success_with_topic_filter(self, mock_repository, mock_logger, sample_problems):
        """Test successful listing with topic filter."""
        # Arrange
        mock_repository.list_all.return_value = sample_problems

        command = ListCommand(
            platform=None,
            difficulty_filter=None,
            topic_filter=["Array"],
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "Found 2 problems" in result.message
        assert "topics=Array" in result.message
        assert len(result.data) == 2
        assert all("Array" in p.topics for p in result.data)
        assert result.error is None

    def test_execute_success_with_sorting(self, mock_repository, mock_logger, sample_problems):
        """Test successful listing with custom sorting."""
        # Arrange
        mock_repository.list_all.return_value = sample_problems

        command = ListCommand(
            platform=None,
            difficulty_filter=None,
            topic_filter=None,
            sort_by="acceptance_rate",
            reverse=True,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "Found 3 problems" in result.message
        assert "sorted by acceptance_rate (descending)" in result.message
        assert result.data[0].acceptance_rate == 49.1  # Highest first
        assert result.data[-1].acceptance_rate == 35.2  # Lowest last
        assert result.error is None

    def test_execute_success_empty_result(self, mock_repository, mock_logger):
        """Test successful listing with no matching problems."""
        # Arrange
        mock_repository.list_all.return_value = []

        command = ListCommand(
            platform=None,
            difficulty_filter=None,
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "No problems found in repository" in result.message
        assert result.data == []
        assert result.error is None

    def test_execute_success_empty_result_with_filters(
        self, mock_repository, mock_logger, sample_problems
    ):
        """Test successful listing with filters that match nothing."""
        # Arrange
        mock_repository.list_all.return_value = sample_problems

        command = ListCommand(
            platform=None,
            difficulty_filter=["Easy"],
            topic_filter=["Dynamic Programming"],  # No problems have this topic
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is True
        assert "No problems found matching criteria" in result.message
        assert "difficulty=Easy" in result.message
        assert "topics=Dynamic Programming" in result.message
        assert result.data == []
        assert result.error is None


class TestListCommandErrors:
    """Test error handling scenarios."""

    def test_execute_repository_exception(self, mock_repository, mock_logger):
        """Test handling of repository exception."""
        # Arrange
        mock_repository.list_all.side_effect = RepositoryException("Failed to read")

        command = ListCommand(
            platform=None,
            difficulty_filter=None,
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Failed to list problems from repository" in result.message
        assert "check file permissions" in result.message
        assert result.data is None
        assert isinstance(result.error, RepositoryException)

    def test_execute_invalid_sort_field(self, mock_repository, mock_logger):
        """Test handling of invalid sort field."""
        # Arrange
        command = ListCommand(
            platform=None,
            difficulty_filter=None,
            topic_filter=None,
            sort_by="invalid_field",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Invalid parameter" in result.message
        assert "invalid_field" in result.message
        assert result.data is None
        assert isinstance(result.error, ValueError)

    def test_execute_invalid_difficulty(self, mock_repository, mock_logger):
        """Test handling of invalid difficulty value."""
        # Arrange
        command = ListCommand(
            platform=None,
            difficulty_filter=["Invalid"],
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Invalid parameter" in result.message
        assert "Invalid" in result.message
        assert result.data is None
        assert isinstance(result.error, ValueError)

    def test_execute_empty_platform_string(self, mock_repository, mock_logger):
        """Test handling of empty platform string."""
        # Arrange
        command = ListCommand(
            platform="   ",  # Empty after strip
            difficulty_filter=None,
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Invalid parameter" in result.message
        assert "Platform cannot be empty" in result.message
        assert result.data is None
        assert isinstance(result.error, ValueError)

    def test_execute_unexpected_exception(self, mock_repository, mock_logger):
        """Test handling of unexpected exception."""
        # Arrange
        mock_repository.list_all.side_effect = RuntimeError("Unexpected error")

        command = ListCommand(
            platform=None,
            difficulty_filter=None,
            topic_filter=None,
            sort_by="id",
            reverse=False,
            repository=mock_repository,
            logger=mock_logger,
        )

        # Act
        result = command.execute()

        # Assert
        assert result.success is False
        assert "Unexpected error" in result.message
        assert "bug" in result.message.lower()
        assert result.data is None
        assert isinstance(result.error, RuntimeError)


class TestListCommandArgumentParser:
    """Test argument parser configuration."""

    def test_create_argument_parser(self):
        """Test that argument parser is created correctly."""
        # Act
        parser = ListCommand.create_argument_parser()

        # Assert
        assert parser is not None
        assert parser.description is not None

        # Test parsing with no arguments (all optional)
        args = parser.parse_args([])
        assert args.platform is None
        assert args.difficulty is None
        assert args.topics is None
        assert args.sort_by == "id"
        assert args.reverse is False

    def test_argument_parser_with_platform(self):
        """Test parsing platform argument."""
        parser = ListCommand.create_argument_parser()

        args = parser.parse_args(["--platform", "leetcode"])
        assert args.platform == "leetcode"

    def test_argument_parser_with_difficulty(self):
        """Test parsing difficulty argument."""
        parser = ListCommand.create_argument_parser()

        args = parser.parse_args(["--difficulty", "Easy", "Medium"])
        assert args.difficulty == ["Easy", "Medium"]

    def test_argument_parser_with_topics(self):
        """Test parsing topics argument."""
        parser = ListCommand.create_argument_parser()

        args = parser.parse_args(["--topics", "Array", "Hash Table"])
        assert args.topics == ["Array", "Hash Table"]

    def test_argument_parser_with_sort_by(self):
        """Test parsing sort-by argument."""
        parser = ListCommand.create_argument_parser()

        args = parser.parse_args(["--sort-by", "acceptance_rate"])
        assert args.sort_by == "acceptance_rate"

    def test_argument_parser_with_reverse(self):
        """Test parsing reverse flag."""
        parser = ListCommand.create_argument_parser()

        args = parser.parse_args(["--reverse"])
        assert args.reverse is True

    def test_argument_parser_with_all_options(self):
        """Test parsing all arguments together."""
        parser = ListCommand.create_argument_parser()

        args = parser.parse_args(
            [
                "--platform",
                "leetcode",
                "--difficulty",
                "Easy",
                "Medium",
                "--topics",
                "Array",
                "--sort-by",
                "title",
                "--reverse",
            ]
        )

        assert args.platform == "leetcode"
        assert args.difficulty == ["Easy", "Medium"]
        assert args.topics == ["Array"]
        assert args.sort_by == "title"
        assert args.reverse is True
