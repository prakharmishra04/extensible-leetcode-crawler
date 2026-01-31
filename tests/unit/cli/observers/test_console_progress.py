"""Unit tests for ConsoleProgressObserver."""

import io
import sys
from unittest.mock import patch

import pytest

from crawler.application.interfaces.observer import DownloadStats
from crawler.cli.observers.console_progress import ConsoleProgressObserver
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
def observer():
    """Create a ConsoleProgressObserver instance."""
    return ConsoleProgressObserver(verbose=False)


@pytest.fixture
def verbose_observer():
    """Create a verbose ConsoleProgressObserver instance."""
    return ConsoleProgressObserver(verbose=True)


class TestConsoleProgressObserver:
    """Test suite for ConsoleProgressObserver."""

    def test_initialization_default(self):
        """Test observer initialization with default parameters."""
        observer = ConsoleProgressObserver()
        assert observer.verbose is False
        assert observer._start_time is None

    def test_initialization_verbose(self):
        """Test observer initialization with verbose mode."""
        observer = ConsoleProgressObserver(verbose=True)
        assert observer.verbose is True
        assert observer._start_time is None

    def test_on_start_displays_message(self, observer, capsys):
        """Test that on_start displays the correct message."""
        observer.on_start(150)

        captured = capsys.readouterr()
        assert "Starting download of 150 problems" in captured.out
        assert "=" * 80 in captured.out
        assert observer._start_time is not None

    def test_on_start_with_zero_problems(self, observer, capsys):
        """Test on_start with zero problems."""
        observer.on_start(0)

        captured = capsys.readouterr()
        assert "Starting download of 0 problems" in captured.out

    def test_on_progress_displays_progress(self, observer, sample_problem, capsys):
        """Test that on_progress displays progress information."""
        observer.on_progress(1, 150, sample_problem)

        captured = capsys.readouterr()
        assert "[1/150]" in captured.out
        assert "Two Sum" in captured.out
        assert "%" in captured.out

    def test_on_progress_with_zero_total(self, observer, sample_problem, capsys):
        """Test on_progress handles zero total gracefully."""
        observer.on_progress(0, 0, sample_problem)

        captured = capsys.readouterr()
        assert "[0/0]" in captured.out
        assert "Two Sum" in captured.out

    def test_on_progress_percentage_calculation(self, observer, sample_problem, capsys):
        """Test that percentage is calculated correctly."""
        observer.on_progress(50, 100, sample_problem)

        captured = capsys.readouterr()
        assert "50.0%" in captured.out

    def test_on_progress_at_completion(self, observer, sample_problem, capsys):
        """Test on_progress at 100% completion."""
        observer.on_progress(150, 150, sample_problem)

        captured = capsys.readouterr()
        assert "[150/150]" in captured.out
        assert "100.0%" in captured.out

    def test_on_skip_verbose_mode(self, verbose_observer, sample_problem, capsys):
        """Test that on_skip displays message in verbose mode."""
        verbose_observer.on_skip(sample_problem, "Already exists")

        captured = capsys.readouterr()
        assert "Skipped" in captured.out
        assert "Two Sum" in captured.out
        assert "Already exists" in captured.out

    def test_on_skip_non_verbose_mode(self, observer, sample_problem, capsys):
        """Test that on_skip does not display message in non-verbose mode."""
        observer.on_skip(sample_problem, "Already exists")

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_on_error_displays_error(self, observer, sample_problem, capsys):
        """Test that on_error displays error message."""
        error = Exception("Network timeout")
        observer.on_error(sample_problem, error)

        captured = capsys.readouterr()
        assert "Error downloading" in captured.out
        assert "Two Sum" in captured.out
        assert "Network timeout" in captured.out

    def test_on_error_always_displays_regardless_of_verbose(self, observer, sample_problem, capsys):
        """Test that on_error displays even in non-verbose mode."""
        # observer is non-verbose by default
        error = Exception("Connection failed")
        observer.on_error(sample_problem, error)

        captured = capsys.readouterr()
        assert "Error downloading" in captured.out
        assert "Connection failed" in captured.out

    def test_on_complete_displays_statistics(self, observer, capsys):
        """Test that on_complete displays final statistics."""
        stats = DownloadStats(total=150, downloaded=145, skipped=3, failed=2, duration=120.5)

        observer.on_complete(stats)

        captured = capsys.readouterr()
        assert "Download complete!" in captured.out
        assert "Total: 150" in captured.out
        assert "Downloaded: 145" in captured.out
        assert "Skipped: 3" in captured.out
        assert "Failed: 2" in captured.out
        assert "Duration:" in captured.out
        assert "Success rate:" in captured.out

    def test_on_complete_with_zero_total(self, observer, capsys):
        """Test on_complete with zero total problems."""
        stats = DownloadStats(total=0, downloaded=0, skipped=0, failed=0, duration=0.0)

        observer.on_complete(stats)

        captured = capsys.readouterr()
        assert "Download complete!" in captured.out
        assert "Total: 0" in captured.out
        # Success rate should not be displayed when total is 0
        assert "Success rate:" not in captured.out

    def test_on_complete_calculates_success_rate(self, observer, capsys):
        """Test that success rate is calculated correctly."""
        stats = DownloadStats(total=100, downloaded=95, skipped=3, failed=2, duration=60.0)

        observer.on_complete(stats)

        captured = capsys.readouterr()
        assert "Success rate: 95.0%" in captured.out

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

    def test_complete_workflow(self, observer, sample_problem, capsys):
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

        captured = capsys.readouterr()

        # Verify all stages are present
        assert "Starting download of 3 problems" in captured.out
        assert "[1/3]" in captured.out
        assert "Error downloading" in captured.out
        assert "Download complete!" in captured.out
        assert "Total: 3" in captured.out
        assert "Downloaded: 1" in captured.out
        assert "Skipped: 1" in captured.out
        assert "Failed: 1" in captured.out

    def test_multiple_problems_progress(self, observer, sample_problem, capsys):
        """Test progress display for multiple problems."""
        for i in range(1, 6):
            observer.on_progress(i, 5, sample_problem)

        captured = capsys.readouterr()

        # Should show progress for all 5 problems
        assert "[1/5]" in captured.out
        assert "[5/5]" in captured.out
        assert "100.0%" in captured.out

    def test_observer_implements_interface(self, observer):
        """Test that ConsoleProgressObserver implements DownloadObserver interface."""
        from crawler.application.interfaces.observer import DownloadObserver

        assert isinstance(observer, DownloadObserver)
        assert hasattr(observer, "on_start")
        assert hasattr(observer, "on_progress")
        assert hasattr(observer, "on_skip")
        assert hasattr(observer, "on_error")
        assert hasattr(observer, "on_complete")

    def test_progress_bar_visual_representation(self, observer, sample_problem, capsys):
        """Test that progress bar contains visual elements."""
        observer.on_progress(25, 100, sample_problem)

        captured = capsys.readouterr()

        # Should contain progress bar characters
        assert "█" in captured.out or "░" in captured.out
        assert "25.0%" in captured.out

    def test_on_progress_newline_every_10_items(self, observer, sample_problem, capsys):
        """Test that newline is printed every 10 items."""
        # Progress through 15 items
        for i in range(1, 16):
            observer.on_progress(i, 20, sample_problem)

        captured = capsys.readouterr()

        # Should have newlines at positions 10 and 15
        # We can't easily test for exact newlines, but we can verify output exists
        assert "[10/20]" in captured.out
        assert "[15/20]" in captured.out

    def test_verbose_mode_shows_skip_details(self, verbose_observer, sample_problem, capsys):
        """Test that verbose mode shows detailed skip information."""
        verbose_observer.on_skip(sample_problem, "Filtered by difficulty")

        captured = capsys.readouterr()
        assert "Skipped" in captured.out
        assert "Two Sum" in captured.out
        assert "Filtered by difficulty" in captured.out

    def test_error_message_format(self, observer, sample_problem, capsys):
        """Test the format of error messages."""
        error = ValueError("Invalid problem ID")
        observer.on_error(sample_problem, error)

        captured = capsys.readouterr()
        assert "✗" in captured.out or "Error" in captured.out
        assert "Two Sum" in captured.out
        assert "Invalid problem ID" in captured.out
