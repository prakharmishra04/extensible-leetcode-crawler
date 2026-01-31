"""Unit tests for BatchDownloadUseCase."""

import logging
from unittest.mock import MagicMock, Mock, call

import pytest

from crawler.application.use_cases.batch_download import (
    BatchDownloadOptions,
    BatchDownloadUseCase,
    DownloadStats,
)
from crawler.domain.entities import Problem, Submission, UpdateMode
from crawler.domain.value_objects import Difficulty, Example


@pytest.fixture
def mock_client():
    """Create a mock platform client."""
    return Mock()


@pytest.fixture
def mock_repository():
    """Create a mock problem repository."""
    return Mock()


@pytest.fixture
def mock_formatter():
    """Create a mock output formatter."""
    formatter = Mock()
    formatter.get_file_extension.return_value = "py"
    return formatter


@pytest.fixture
def mock_observer():
    """Create a mock download observer."""
    return Mock()


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id="two-sum",
        platform="leetcode",
        title="Two Sum",
        difficulty=Difficulty("Easy"),
        description="Find two numbers that add up to target",
        topics=["Array", "Hash Table"],
        constraints="2 <= nums.length <= 10^4",
        examples=[
            Example(
                input="nums = [2,7,11,15], target = 9",
                output="[0,1]",
                explanation="nums[0] + nums[1] == 9",
            )
        ],
        hints=["Use a hash table"],
        acceptance_rate=45.5,
    )


@pytest.fixture
def sample_submission():
    """Create a sample submission for testing."""
    from crawler.domain.entities import SubmissionStatus

    return Submission(
        id="sub-123",
        problem_id="two-sum",
        language="python3",
        code="def twoSum(nums, target):\n    pass",
        status=SubmissionStatus.ACCEPTED,
        runtime="50 ms",
        memory="14.5 MB",
        timestamp=1234567890,
    )


@pytest.fixture
def use_case(mock_client, mock_repository, mock_formatter, mock_observer, mock_logger):
    """Create a BatchDownloadUseCase instance with mocked dependencies."""
    return BatchDownloadUseCase(
        client=mock_client,
        repository=mock_repository,
        formatter=mock_formatter,
        observers=[mock_observer],
        logger=mock_logger,
    )


class TestBatchDownloadUseCase:
    """Test BatchDownloadUseCase class."""

    def test_init(self, mock_client, mock_repository, mock_formatter, mock_observer, mock_logger):
        """Test initialization of BatchDownloadUseCase."""
        use_case = BatchDownloadUseCase(
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=[mock_observer],
            logger=mock_logger,
        )

        assert use_case.client == mock_client
        assert use_case.repository == mock_repository
        assert use_case.formatter == mock_formatter
        assert use_case.observers == [mock_observer]
        assert use_case.logger == mock_logger

    def test_execute_with_empty_problem_list(self, use_case, mock_client, mock_observer):
        """Test execute with no problems to download."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = []
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify
        assert stats.total == 0
        assert stats.downloaded == 0
        assert stats.skipped == 0
        assert stats.failed == 0
        assert stats.duration >= 0

        # Verify observer was notified
        mock_observer.on_start.assert_called_once_with(0)
        mock_observer.on_complete.assert_called_once()

    def test_execute_with_single_problem_skip_mode(
        self, use_case, mock_client, mock_repository, mock_observer, sample_problem
    ):
        """Test execute with single problem in SKIP mode when problem exists.

        With the new behavior, problems are pre-filtered in SKIP mode,
        so already-existing problems are filtered out before download attempts.
        This means stats.total will be 0 and no download attempts are made.
        """
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = True
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify - problem was filtered out before download
        assert stats.total == 0
        assert stats.downloaded == 0
        assert stats.skipped == 0  # Not counted as skipped since pre-filtered
        assert stats.failed == 0

        # Verify repository was checked during filtering but not saved
        mock_repository.exists.assert_called_once_with("two-sum", "leetcode")
        mock_repository.save.assert_not_called()

        # Verify observer was notified with 0 problems to download
        mock_observer.on_start.assert_called_once_with(0)
        mock_observer.on_complete.assert_called_once()
        # on_skip should not be called since problem was pre-filtered
        mock_observer.on_skip.assert_not_called()

    def test_execute_with_single_problem_force_mode(
        self,
        use_case,
        mock_client,
        mock_repository,
        mock_observer,
        sample_problem,
        sample_submission,
    ):
        """Test execute with single problem in FORCE mode."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_client.fetch_problem.return_value = sample_problem
        mock_client.fetch_submission.return_value = sample_submission
        mock_repository.exists.return_value = True
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.FORCE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify
        assert stats.total == 1
        assert stats.downloaded == 1
        assert stats.skipped == 0
        assert stats.failed == 0

        # Verify problem was fetched and saved
        mock_client.fetch_problem.assert_called_once_with("two-sum")
        mock_client.fetch_submission.assert_called_once_with("two-sum", "john_doe")
        mock_repository.save.assert_called_once_with(sample_problem, sample_submission)

        # Verify observer was notified
        mock_observer.on_start.assert_called_once_with(1)
        mock_observer.on_progress.assert_called_once_with(1, 1, sample_problem)
        mock_observer.on_complete.assert_called_once()

    def test_execute_with_difficulty_filter(
        self, use_case, mock_client, mock_observer, mock_repository
    ):
        """Test execute with difficulty filter."""
        # Setup
        easy_problem = Problem(
            id="easy-1",
            platform="leetcode",
            title="Easy Problem",
            difficulty=Difficulty("Easy"),
            description="Easy problem",
            topics=["Array"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=50.0,
        )
        hard_problem = Problem(
            id="hard-1",
            platform="leetcode",
            title="Hard Problem",
            difficulty=Difficulty("Hard"),
            description="Hard problem",
            topics=["Array"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=20.0,
        )

        mock_client.fetch_all_problems_with_status.return_value = [easy_problem, hard_problem]
        mock_repository.exists.return_value = False  # Problems don't exist yet
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=["Easy"],
        )

        # Execute
        stats = use_case.execute(options)

        # Verify - only easy problem should be processed
        assert stats.total == 1
        mock_observer.on_start.assert_called_once_with(1)

    def test_execute_with_topic_filter(self, use_case, mock_client, mock_observer, mock_repository):
        """Test execute with topic filter."""
        # Setup
        array_problem = Problem(
            id="array-1",
            platform="leetcode",
            title="Array Problem",
            difficulty=Difficulty("Easy"),
            description="Array problem",
            topics=["Array", "Hash Table"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=50.0,
        )
        graph_problem = Problem(
            id="graph-1",
            platform="leetcode",
            title="Graph Problem",
            difficulty=Difficulty("Medium"),
            description="Graph problem",
            topics=["Graph", "DFS"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=30.0,
        )

        mock_client.fetch_all_problems_with_status.return_value = [array_problem, graph_problem]
        mock_repository.exists.return_value = False  # Problems don't exist yet
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            topic_filter=["Array"],
        )

        # Execute
        stats = use_case.execute(options)

        # Verify - only array problem should be processed
        assert stats.total == 1
        mock_observer.on_start.assert_called_once_with(1)

    def test_execute_with_partial_failure(
        self, use_case, mock_client, mock_repository, mock_observer, sample_problem
    ):
        """Test execute handles partial failures gracefully."""
        # Setup
        problem1 = sample_problem
        problem2 = Problem(
            id="problem-2",
            platform="leetcode",
            title="Problem 2",
            difficulty=Difficulty("Medium"),
            description="Problem 2",
            topics=["Array"],
            constraints="",
            examples=[],
            hints=[],
            acceptance_rate=40.0,
        )

        mock_client.fetch_all_problems_with_status.return_value = [problem1, problem2]
        mock_repository.exists.return_value = False

        # Make first problem succeed, second fail
        mock_client.fetch_problem.side_effect = [
            problem1,
            Exception("Network error"),
        ]

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.FORCE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify - one succeeded, one failed
        assert stats.total == 2
        assert stats.downloaded == 1
        assert stats.skipped == 0
        assert stats.failed == 1

        # Verify observer was notified of error
        mock_observer.on_error.assert_called_once()
        mock_observer.on_complete.assert_called_once()

    def test_execute_with_submission_fetch_failure(
        self, use_case, mock_client, mock_repository, mock_observer, sample_problem
    ):
        """Test execute continues when submission fetch fails."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_client.fetch_problem.return_value = sample_problem
        mock_client.fetch_submission.side_effect = Exception("Submission not found")
        mock_repository.exists.return_value = False

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.FORCE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify - problem saved without submission
        assert stats.total == 1
        assert stats.downloaded == 1
        assert stats.failed == 0

        # Verify problem was saved without submission
        mock_repository.save.assert_called_once_with(sample_problem, None)

    def test_execute_with_multiple_observers(
        self, mock_client, mock_repository, mock_formatter, mock_logger, sample_problem
    ):
        """Test execute notifies multiple observers.

        With pre-filtering in SKIP mode, if problem exists, it's filtered out
        before download, so observers are notified with 0 problems.
        """
        # Setup
        observer1 = Mock()
        observer2 = Mock()
        use_case = BatchDownloadUseCase(
            client=mock_client,
            repository=mock_repository,
            formatter=mock_formatter,
            observers=[observer1, observer2],
            logger=mock_logger,
        )

        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = True
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify both observers were notified with 0 problems (pre-filtered)
        observer1.on_start.assert_called_once_with(0)
        observer2.on_start.assert_called_once_with(0)
        # on_skip should not be called since problem was pre-filtered
        observer1.on_skip.assert_not_called()
        observer2.on_skip.assert_not_called()
        observer1.on_complete.assert_called_once()
        observer2.on_complete.assert_called_once()

    def test_execute_handles_observer_exceptions(
        self, use_case, mock_client, mock_repository, mock_observer, sample_problem
    ):
        """Test execute continues when observer raises exception.

        With pre-filtering in SKIP mode, if problem exists, it's filtered out
        before download, so stats.total will be 0.
        """
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = True
        mock_observer.on_start.side_effect = Exception("Observer error")

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        # Execute - should not raise exception
        stats = use_case.execute(options)

        # Verify execution completed despite observer error
        # Problem was pre-filtered, so total is 0
        assert stats.total == 0
        assert stats.skipped == 0

    def test_execute_update_mode_skips_when_submission_up_to_date(
        self, use_case, mock_client, mock_repository, sample_problem, sample_submission
    ):
        """Test UPDATE mode skips problem when stored submission is up-to-date."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = True
        mock_repository.get_submission_timestamp.return_value = 1234567890

        # Platform has same or older submission
        mock_client.fetch_submission.return_value = sample_submission  # timestamp=1234567890

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.UPDATE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify problem was skipped
        assert stats.total == 1
        assert stats.downloaded == 0
        assert stats.skipped == 1
        assert stats.failed == 0

    def test_execute_update_mode_downloads_when_newer_submission_exists(
        self, use_case, mock_client, mock_repository, sample_problem, sample_submission
    ):
        """Test UPDATE mode downloads problem when platform has newer submission."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = True
        mock_repository.get_submission_timestamp.return_value = 1000000000  # Older

        # Platform has newer submission
        newer_submission = Mock()
        newer_submission.timestamp = 1640995200  # Newer
        mock_client.fetch_submission.return_value = newer_submission
        mock_client.fetch_problem.return_value = sample_problem

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.UPDATE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify problem was downloaded
        assert stats.total == 1
        assert stats.downloaded == 1
        assert stats.skipped == 0
        assert stats.failed == 0
        mock_repository.save.assert_called_once()

    def test_execute_update_mode_downloads_when_no_submission_stored(
        self, use_case, mock_client, mock_repository, sample_problem, sample_submission
    ):
        """Test UPDATE mode downloads problem when it exists but has no submission."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = True
        mock_repository.get_submission_timestamp.return_value = None  # No submission stored

        mock_client.fetch_problem.return_value = sample_problem
        mock_client.fetch_submission.return_value = sample_submission

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.UPDATE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify problem was downloaded
        assert stats.total == 1
        assert stats.downloaded == 1
        assert stats.skipped == 0
        assert stats.failed == 0
        mock_repository.save.assert_called_once()

    def test_execute_update_mode_skips_when_fetch_submission_fails(
        self, use_case, mock_client, mock_repository, sample_problem
    ):
        """Test UPDATE mode skips problem when fetching submission for comparison fails."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = True
        mock_repository.get_submission_timestamp.return_value = 1234567890

        # Fetching submission for comparison fails
        mock_client.fetch_submission.side_effect = Exception("API error")

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.UPDATE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify problem was skipped due to error
        assert stats.total == 1
        assert stats.downloaded == 0
        assert stats.skipped == 1
        assert stats.failed == 0

    def test_execute_update_mode_downloads_when_problem_not_exists(
        self, use_case, mock_client, mock_repository, sample_problem, sample_submission
    ):
        """Test UPDATE mode downloads problem when it doesn't exist yet."""
        # Setup
        mock_client.fetch_all_problems_with_status.return_value = [sample_problem]
        mock_repository.exists.return_value = False  # Problem doesn't exist

        mock_client.fetch_problem.return_value = sample_problem
        mock_client.fetch_submission.return_value = sample_submission

        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.UPDATE,
        )

        # Execute
        stats = use_case.execute(options)

        # Verify problem was downloaded
        assert stats.total == 1
        assert stats.downloaded == 1
        assert stats.skipped == 0
        assert stats.failed == 0
        mock_repository.save.assert_called_once()
