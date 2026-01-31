"""Unit tests for LoggingObserver."""

import logging
from unittest.mock import Mock, call

import pytest

from crawler.application.interfaces.observer import DownloadStats
from crawler.cli.observers.logging_observer import LoggingObserver
from crawler.domain.entities import Problem
from crawler.domain.value_objects import Difficulty, Example


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        id="two-sum",
        platform="leetcode",
        title="Two Sum",
        difficulty=Difficulty("Easy"),
        description="Find two numbers that add up to a target.",
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
def mock_logger():
    """Create a mock logger for testing."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def observer(mock_logger):
    """Create a LoggingObserver instance with mock logger."""
    return LoggingObserver(logger=mock_logger)


class TestLoggingObserver:
    """Test suite for LoggingObserver."""

    def test_initialization_with_logger(self, mock_logger):
        """Test observer initialization with provided logger."""
        observer = LoggingObserver(logger=mock_logger)
        assert observer.logger is mock_logger
        assert observer._start_time is None

    def test_initialization_without_logger(self):
        """Test observer initialization creates default logger."""
        observer = LoggingObserver()
        assert observer.logger is not None
        assert observer.logger.name == "crawler.observer"
        assert observer._start_time is None

    def test_on_start_logs_info_message(self, observer, mock_logger):
        """Test that on_start logs an INFO message."""
        observer.on_start(150)

        # Verify INFO log was called
        mock_logger.info.assert_called_once()

        # Verify message content
        call_args = mock_logger.info.call_args
        assert "Starting batch download of 150 problems" in call_args[0][0]

        # Verify extra fields
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["total_problems"] == 150
        assert extra_fields["event"] == "batch_start"

        # Verify start time was set
        assert observer._start_time is not None

    def test_on_start_with_zero_problems(self, observer, mock_logger):
        """Test on_start with zero problems."""
        observer.on_start(0)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "Starting batch download of 0 problems" in call_args[0][0]

    def test_on_progress_logs_info_message(self, observer, mock_logger, sample_problem):
        """Test that on_progress logs an INFO message."""
        observer.on_progress(1, 150, sample_problem)

        # Verify INFO log was called
        mock_logger.info.assert_called_once()

        # Verify message content
        call_args = mock_logger.info.call_args
        message = call_args[0][0]
        assert "Downloaded problem 1/150" in message
        assert "Two Sum" in message
        assert "two-sum" in message

        # Verify extra fields
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["event"] == "problem_downloaded"
        assert extra_fields["problem_id"] == "two-sum"
        assert extra_fields["problem_title"] == "Two Sum"
        assert extra_fields["platform"] == "leetcode"
        assert extra_fields["difficulty"] == "Easy"
        assert extra_fields["current"] == 1
        assert extra_fields["total"] == 150
        assert extra_fields["percentage"] == 0.7  # 1/150 * 100 rounded to 1 decimal

    def test_on_progress_with_zero_total(self, observer, mock_logger, sample_problem):
        """Test on_progress handles zero total gracefully."""
        observer.on_progress(0, 0, sample_problem)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["percentage"] == 0

    def test_on_progress_percentage_calculation(self, observer, mock_logger, sample_problem):
        """Test that percentage is calculated correctly."""
        observer.on_progress(50, 100, sample_problem)

        call_args = mock_logger.info.call_args
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["percentage"] == 50.0

    def test_on_progress_at_completion(self, observer, mock_logger, sample_problem):
        """Test on_progress at 100% completion."""
        observer.on_progress(150, 150, sample_problem)

        call_args = mock_logger.info.call_args
        message = call_args[0][0]
        assert "Downloaded problem 150/150" in message

        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["percentage"] == 100.0

    def test_on_skip_logs_warning_message(self, observer, mock_logger, sample_problem):
        """Test that on_skip logs a WARNING message."""
        observer.on_skip(sample_problem, "Already exists")

        # Verify WARNING log was called
        mock_logger.warning.assert_called_once()

        # Verify message content
        call_args = mock_logger.warning.call_args
        message = call_args[0][0]
        assert "Skipped problem" in message
        assert "Two Sum" in message
        assert "two-sum" in message
        assert "Already exists" in message

        # Verify extra fields
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["event"] == "problem_skipped"
        assert extra_fields["problem_id"] == "two-sum"
        assert extra_fields["problem_title"] == "Two Sum"
        assert extra_fields["platform"] == "leetcode"
        assert extra_fields["skip_reason"] == "Already exists"

    def test_on_skip_with_different_reasons(self, observer, mock_logger, sample_problem):
        """Test on_skip with various skip reasons."""
        reasons = [
            "Already exists",
            "Filtered by difficulty",
            "Filtered by topic",
            "User requested skip",
        ]

        for reason in reasons:
            mock_logger.reset_mock()
            observer.on_skip(sample_problem, reason)

            call_args = mock_logger.warning.call_args
            message = call_args[0][0]
            assert reason in message

            extra_fields = call_args[1]["extra"]["extra_fields"]
            assert extra_fields["skip_reason"] == reason

    def test_on_error_logs_error_message(self, observer, mock_logger, sample_problem):
        """Test that on_error logs an ERROR message."""
        error = Exception("Network timeout")
        observer.on_error(sample_problem, error)

        # Verify ERROR log was called
        mock_logger.error.assert_called_once()

        # Verify message content
        call_args = mock_logger.error.call_args
        message = call_args[0][0]
        assert "Failed to download problem" in message
        assert "Two Sum" in message
        assert "two-sum" in message
        assert "Network timeout" in message

        # Verify extra fields
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["event"] == "problem_failed"
        assert extra_fields["problem_id"] == "two-sum"
        assert extra_fields["problem_title"] == "Two Sum"
        assert extra_fields["platform"] == "leetcode"
        assert extra_fields["error_type"] == "Exception"
        assert extra_fields["error_message"] == "Network timeout"

        # Verify exc_info is True (for traceback)
        assert call_args[1]["exc_info"] is True

    def test_on_error_with_different_exception_types(self, observer, mock_logger, sample_problem):
        """Test on_error with various exception types."""
        exceptions = [
            ValueError("Invalid value"),
            TypeError("Type mismatch"),
            RuntimeError("Runtime error"),
            ConnectionError("Connection failed"),
        ]

        for exc in exceptions:
            mock_logger.reset_mock()
            observer.on_error(sample_problem, exc)

            call_args = mock_logger.error.call_args
            extra_fields = call_args[1]["extra"]["extra_fields"]
            assert extra_fields["error_type"] == type(exc).__name__
            assert extra_fields["error_message"] == str(exc)

    def test_on_complete_logs_info_message(self, observer, mock_logger):
        """Test that on_complete logs an INFO message."""
        stats = DownloadStats(total=150, downloaded=145, skipped=3, failed=2, duration=120.5)

        observer.on_complete(stats)

        # Verify INFO log was called (once for main message, once for debug)
        assert mock_logger.info.call_count == 1
        assert mock_logger.debug.call_count == 1

        # Verify main INFO message content
        info_call_args = mock_logger.info.call_args
        message = info_call_args[0][0]
        assert "Batch download complete" in message
        assert "145/150 downloaded" in message
        assert "3 skipped" in message
        assert "2 failed" in message

        # Verify extra fields
        extra_fields = info_call_args[1]["extra"]["extra_fields"]
        assert extra_fields["event"] == "batch_complete"
        assert extra_fields["total"] == 150
        assert extra_fields["downloaded"] == 145
        assert extra_fields["skipped"] == 3
        assert extra_fields["failed"] == 2
        assert extra_fields["duration_seconds"] == 120.5
        assert extra_fields["success_rate"] == 96.7  # 145/150 * 100 rounded to 1 decimal

    def test_on_complete_with_zero_total(self, observer, mock_logger):
        """Test on_complete with zero total problems."""
        stats = DownloadStats(total=0, downloaded=0, skipped=0, failed=0, duration=0.0)

        observer.on_complete(stats)

        info_call_args = mock_logger.info.call_args
        extra_fields = info_call_args[1]["extra"]["extra_fields"]
        assert extra_fields["success_rate"] == 0

    def test_on_complete_calculates_success_rate(self, observer, mock_logger):
        """Test that success rate is calculated correctly."""
        stats = DownloadStats(total=100, downloaded=95, skipped=3, failed=2, duration=60.0)

        observer.on_complete(stats)

        info_call_args = mock_logger.info.call_args
        extra_fields = info_call_args[1]["extra"]["extra_fields"]
        assert extra_fields["success_rate"] == 95.0

    def test_on_complete_logs_debug_details(self, observer, mock_logger):
        """Test that on_complete logs additional DEBUG details."""
        stats = DownloadStats(total=100, downloaded=95, skipped=3, failed=2, duration=60.0)

        observer.on_complete(stats)

        # Verify DEBUG log was called
        mock_logger.debug.assert_called_once()

        # Verify debug message content
        debug_call_args = mock_logger.debug.call_args
        message = debug_call_args[0][0]
        assert "Batch download details" in message
        assert "success_rate=95.0%" in message
        assert "duration=60.00s" in message

        # Verify extra fields
        extra_fields = debug_call_args[1]["extra"]["extra_fields"]
        assert extra_fields["event"] == "batch_details"
        assert extra_fields["success_rate"] == 95.0
        assert extra_fields["duration_seconds"] == 60.0

    def test_format_duration_seconds_only(self, observer):
        """Test duration formatting for less than 60 seconds."""
        assert observer._format_duration(45.2) == "45.2s"
        assert observer._format_duration(0.5) == "0.5s"
        assert observer._format_duration(59.9) == "59.9s"

    def test_format_duration_minutes_and_seconds(self, observer):
        """Test duration formatting for minutes and seconds."""
        assert observer._format_duration(60.0) == "1m 0.0s"
        assert observer._format_duration(90.5) == "1m 30.5s"
        assert observer._format_duration(150.0) == "2m 30.0s"
        assert observer._format_duration(3599.0) == "59m 59.0s"

    def test_format_duration_hours_minutes_seconds(self, observer):
        """Test duration formatting for hours, minutes, and seconds."""
        assert observer._format_duration(3600.0) == "1h 0m 0.0s"
        assert observer._format_duration(3665.0) == "1h 1m 5.0s"
        assert observer._format_duration(7325.5) == "2h 2m 5.5s"

    def test_format_duration_edge_cases(self, observer):
        """Test duration formatting edge cases."""
        assert observer._format_duration(0.0) == "0.0s"
        assert observer._format_duration(0.1) == "0.1s"

    def test_complete_workflow(self, observer, mock_logger, sample_problem):
        """Test a complete workflow from start to finish."""
        # Start
        observer.on_start(3)

        # Progress 1
        observer.on_progress(1, 3, sample_problem)

        # Progress 2 (skip)
        observer.on_skip(sample_problem, "Already exists")

        # Progress 3 (error)
        observer.on_error(sample_problem, Exception("Network error"))

        # Complete
        stats = DownloadStats(total=3, downloaded=1, skipped=1, failed=1, duration=5.5)
        observer.on_complete(stats)

        # Verify all log methods were called
        assert mock_logger.info.call_count == 3  # start, progress, complete
        assert mock_logger.warning.call_count == 1  # skip
        assert mock_logger.error.call_count == 1  # error
        assert mock_logger.debug.call_count == 1  # complete details

    def test_multiple_problems_progress(self, observer, mock_logger, sample_problem):
        """Test progress logging for multiple problems."""
        for i in range(1, 6):
            observer.on_progress(i, 5, sample_problem)

        # Verify INFO was called 5 times
        assert mock_logger.info.call_count == 5

        # Verify last call shows 100%
        last_call_args = mock_logger.info.call_args
        extra_fields = last_call_args[1]["extra"]["extra_fields"]
        assert extra_fields["current"] == 5
        assert extra_fields["total"] == 5
        assert extra_fields["percentage"] == 100.0

    def test_observer_implements_interface(self, observer):
        """Test that LoggingObserver implements DownloadObserver interface."""
        from crawler.application.interfaces.observer import DownloadObserver

        assert isinstance(observer, DownloadObserver)
        assert hasattr(observer, "on_start")
        assert hasattr(observer, "on_progress")
        assert hasattr(observer, "on_skip")
        assert hasattr(observer, "on_error")
        assert hasattr(observer, "on_complete")

    def test_logging_levels_are_appropriate(self, observer, mock_logger, sample_problem):
        """Test that appropriate logging levels are used for different events."""
        # Start - INFO
        observer.on_start(10)
        assert mock_logger.info.called

        # Progress - INFO
        mock_logger.reset_mock()
        observer.on_progress(1, 10, sample_problem)
        assert mock_logger.info.called

        # Skip - WARNING
        mock_logger.reset_mock()
        observer.on_skip(sample_problem, "Already exists")
        assert mock_logger.warning.called

        # Error - ERROR
        mock_logger.reset_mock()
        observer.on_error(sample_problem, Exception("Test error"))
        assert mock_logger.error.called

        # Complete - INFO and DEBUG
        mock_logger.reset_mock()
        stats = DownloadStats(total=10, downloaded=8, skipped=1, failed=1, duration=5.0)
        observer.on_complete(stats)
        assert mock_logger.info.called
        assert mock_logger.debug.called

    def test_extra_fields_structure(self, observer, mock_logger, sample_problem):
        """Test that extra fields are properly structured for log aggregation."""
        # Test on_start extra fields
        observer.on_start(100)
        call_args = mock_logger.info.call_args
        assert "extra" in call_args[1]
        assert "extra_fields" in call_args[1]["extra"]
        assert isinstance(call_args[1]["extra"]["extra_fields"], dict)

        # Test on_progress extra fields
        mock_logger.reset_mock()
        observer.on_progress(1, 100, sample_problem)
        call_args = mock_logger.info.call_args
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert "event" in extra_fields
        assert "problem_id" in extra_fields
        assert "platform" in extra_fields
        assert "difficulty" in extra_fields

        # Test on_skip extra fields
        mock_logger.reset_mock()
        observer.on_skip(sample_problem, "Test reason")
        call_args = mock_logger.warning.call_args
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert "event" in extra_fields
        assert "skip_reason" in extra_fields

        # Test on_error extra fields
        mock_logger.reset_mock()
        observer.on_error(sample_problem, ValueError("Test"))
        call_args = mock_logger.error.call_args
        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert "event" in extra_fields
        assert "error_type" in extra_fields
        assert "error_message" in extra_fields

    def test_duration_formatting_in_complete_message(self, observer, mock_logger):
        """Test that duration is properly formatted in complete message."""
        test_cases = [(45.2, "45.2s"), (90.5, "1m 30.5s"), (3665.0, "1h 1m 5.0s")]

        for duration, expected_format in test_cases:
            mock_logger.reset_mock()
            stats = DownloadStats(total=10, downloaded=10, skipped=0, failed=0, duration=duration)
            observer.on_complete(stats)

            call_args = mock_logger.info.call_args
            message = call_args[0][0]
            assert expected_format in message

    def test_problem_details_in_logs(self, observer, mock_logger):
        """Test that problem details are included in log messages."""
        problem = Problem(
            id="longest-substring",
            platform="leetcode",
            title="Longest Substring Without Repeating Characters",
            difficulty=Difficulty("Medium"),
            description="Test description",
            topics=["String", "Sliding Window"],
            constraints="Test constraints",
            examples=[],
            hints=[],
            acceptance_rate=33.5,
        )

        # Test progress log
        observer.on_progress(1, 10, problem)
        call_args = mock_logger.info.call_args
        message = call_args[0][0]
        assert "Longest Substring Without Repeating Characters" in message
        assert "longest-substring" in message

        extra_fields = call_args[1]["extra"]["extra_fields"]
        assert extra_fields["problem_id"] == "longest-substring"
        assert extra_fields["problem_title"] == "Longest Substring Without Repeating Characters"
        assert extra_fields["platform"] == "leetcode"
        assert extra_fields["difficulty"] == "Medium"

    def test_concurrent_observer_usage(self, sample_problem):
        """Test that multiple observers can be used independently."""
        logger1 = Mock(spec=logging.Logger)
        logger2 = Mock(spec=logging.Logger)

        observer1 = LoggingObserver(logger=logger1)
        observer2 = LoggingObserver(logger=logger2)

        # Use both observers
        observer1.on_start(10)
        observer2.on_start(20)

        observer1.on_progress(1, 10, sample_problem)
        observer2.on_progress(1, 20, sample_problem)

        # Verify each observer used its own logger
        assert logger1.info.call_count == 2
        assert logger2.info.call_count == 2

        # Verify they logged different totals
        logger1_start_call = logger1.info.call_args_list[0]
        logger2_start_call = logger2.info.call_args_list[0]

        assert "10 problems" in logger1_start_call[0][0]
        assert "20 problems" in logger2_start_call[0][0]
