"""Unit tests for BatchDownloadOptions and DownloadStats dataclasses."""

import pytest

from crawler.application.use_cases.batch_download import BatchDownloadOptions, DownloadStats
from crawler.domain.entities import UpdateMode


class TestBatchDownloadOptions:
    """Test BatchDownloadOptions dataclass."""

    def test_init_with_required_fields_only(self):
        """Test initialization with only required fields."""
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        assert options.username == "john_doe"
        assert options.platform == "leetcode"
        assert options.update_mode == UpdateMode.SKIP
        assert options.include_community is False
        assert options.difficulty_filter is None
        assert options.topic_filter is None

    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        options = BatchDownloadOptions(
            username="jane_doe",
            platform="hackerrank",
            update_mode=UpdateMode.UPDATE,
            include_community=True,
            difficulty_filter=["Easy", "Medium"],
            topic_filter=["Array", "Hash Table"],
        )

        assert options.username == "jane_doe"
        assert options.platform == "hackerrank"
        assert options.update_mode == UpdateMode.UPDATE
        assert options.include_community is True
        assert options.difficulty_filter == ["Easy", "Medium"]
        assert options.topic_filter == ["Array", "Hash Table"]

    def test_init_with_skip_mode(self):
        """Test initialization with SKIP update mode."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        assert options.update_mode == UpdateMode.SKIP

    def test_init_with_update_mode(self):
        """Test initialization with UPDATE update mode."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.UPDATE,
        )

        assert options.update_mode == UpdateMode.UPDATE

    def test_init_with_force_mode(self):
        """Test initialization with FORCE update mode."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.FORCE,
        )

        assert options.update_mode == UpdateMode.FORCE

    def test_init_with_single_difficulty_filter(self):
        """Test initialization with single difficulty filter."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=["Easy"],
        )

        assert options.difficulty_filter == ["Easy"]

    def test_init_with_multiple_difficulty_filters(self):
        """Test initialization with multiple difficulty filters."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=["Easy", "Medium", "Hard"],
        )

        assert options.difficulty_filter == ["Easy", "Medium", "Hard"]
        assert len(options.difficulty_filter) == 3

    def test_init_with_single_topic_filter(self):
        """Test initialization with single topic filter."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            topic_filter=["Array"],
        )

        assert options.topic_filter == ["Array"]

    def test_init_with_multiple_topic_filters(self):
        """Test initialization with multiple topic filters."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            topic_filter=["Array", "Hash Table", "Dynamic Programming"],
        )

        assert options.topic_filter == ["Array", "Hash Table", "Dynamic Programming"]
        assert len(options.topic_filter) == 3

    def test_init_with_empty_difficulty_filter_list(self):
        """Test initialization with empty difficulty filter list."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=[],
        )

        assert options.difficulty_filter == []

    def test_init_with_empty_topic_filter_list(self):
        """Test initialization with empty topic filter list."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            topic_filter=[],
        )

        assert options.topic_filter == []

    def test_dataclass_equality(self):
        """Test that two instances with same values are equal."""
        options1 = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )
        options2 = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        assert options1 == options2

    def test_dataclass_inequality(self):
        """Test that two instances with different values are not equal."""
        options1 = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )
        options2 = BatchDownloadOptions(
            username="user2",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        assert options1 != options2

    def test_dataclass_repr(self):
        """Test that repr includes all fields."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        repr_str = repr(options)
        assert "BatchDownloadOptions" in repr_str
        assert "username='user1'" in repr_str
        assert "platform='leetcode'" in repr_str
        assert "UpdateMode.SKIP" in repr_str

    def test_fields_are_accessible(self):
        """Test that all fields are accessible as attributes."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            include_community=True,
            difficulty_filter=["Easy"],
            topic_filter=["Array"],
        )

        # Should not raise AttributeError
        _ = options.username
        _ = options.platform
        _ = options.update_mode
        _ = options.include_community
        _ = options.difficulty_filter
        _ = options.topic_filter

    def test_fields_are_mutable(self):
        """Test that fields can be modified after initialization."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
        )

        # Modify fields
        options.username = "user2"
        options.platform = "hackerrank"
        options.update_mode = UpdateMode.FORCE
        options.include_community = True
        options.difficulty_filter = ["Hard"]
        options.topic_filter = ["Graph"]

        # Verify modifications
        assert options.username == "user2"
        assert options.platform == "hackerrank"
        assert options.update_mode == UpdateMode.FORCE
        assert options.include_community is True
        assert options.difficulty_filter == ["Hard"]
        assert options.topic_filter == ["Graph"]


class TestDownloadStats:
    """Test DownloadStats dataclass."""

    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        stats = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        assert stats.total == 100
        assert stats.downloaded == 75
        assert stats.skipped == 20
        assert stats.failed == 5
        assert stats.duration == 245.3

    def test_init_with_zero_values(self):
        """Test initialization with zero values."""
        stats = DownloadStats(
            total=0,
            downloaded=0,
            skipped=0,
            failed=0,
            duration=0.0,
        )

        assert stats.total == 0
        assert stats.downloaded == 0
        assert stats.skipped == 0
        assert stats.failed == 0
        assert stats.duration == 0.0

    def test_init_with_all_downloaded(self):
        """Test initialization when all problems were downloaded."""
        stats = DownloadStats(
            total=50,
            downloaded=50,
            skipped=0,
            failed=0,
            duration=120.5,
        )

        assert stats.total == 50
        assert stats.downloaded == 50
        assert stats.skipped == 0
        assert stats.failed == 0

    def test_init_with_all_skipped(self):
        """Test initialization when all problems were skipped."""
        stats = DownloadStats(
            total=30,
            downloaded=0,
            skipped=30,
            failed=0,
            duration=5.2,
        )

        assert stats.total == 30
        assert stats.downloaded == 0
        assert stats.skipped == 30
        assert stats.failed == 0

    def test_init_with_all_failed(self):
        """Test initialization when all problems failed."""
        stats = DownloadStats(
            total=10,
            downloaded=0,
            skipped=0,
            failed=10,
            duration=15.8,
        )

        assert stats.total == 10
        assert stats.downloaded == 0
        assert stats.skipped == 0
        assert stats.failed == 10

    def test_init_with_mixed_results(self):
        """Test initialization with mixed results."""
        stats = DownloadStats(
            total=100,
            downloaded=60,
            skipped=30,
            failed=10,
            duration=300.0,
        )

        assert stats.total == 100
        assert stats.downloaded == 60
        assert stats.skipped == 30
        assert stats.failed == 10
        # Verify sum equals total
        assert stats.downloaded + stats.skipped + stats.failed == stats.total

    def test_init_with_fractional_duration(self):
        """Test initialization with fractional duration."""
        stats = DownloadStats(
            total=10,
            downloaded=10,
            skipped=0,
            failed=0,
            duration=12.345678,
        )

        assert stats.duration == 12.345678

    def test_init_with_large_numbers(self):
        """Test initialization with large numbers."""
        stats = DownloadStats(
            total=10000,
            downloaded=8500,
            skipped=1200,
            failed=300,
            duration=3600.0,
        )

        assert stats.total == 10000
        assert stats.downloaded == 8500
        assert stats.skipped == 1200
        assert stats.failed == 300
        assert stats.duration == 3600.0

    def test_dataclass_equality(self):
        """Test that two instances with same values are equal."""
        stats1 = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )
        stats2 = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        assert stats1 == stats2

    def test_dataclass_inequality(self):
        """Test that two instances with different values are not equal."""
        stats1 = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )
        stats2 = DownloadStats(
            total=100,
            downloaded=80,
            skipped=15,
            failed=5,
            duration=245.3,
        )

        assert stats1 != stats2

    def test_dataclass_repr(self):
        """Test that repr includes all fields."""
        stats = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        repr_str = repr(stats)
        assert "DownloadStats" in repr_str
        assert "total=100" in repr_str
        assert "downloaded=75" in repr_str
        assert "skipped=20" in repr_str
        assert "failed=5" in repr_str
        assert "duration=245.3" in repr_str

    def test_fields_are_accessible(self):
        """Test that all fields are accessible as attributes."""
        stats = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        # Should not raise AttributeError
        _ = stats.total
        _ = stats.downloaded
        _ = stats.skipped
        _ = stats.failed
        _ = stats.duration

    def test_fields_are_mutable(self):
        """Test that fields can be modified after initialization."""
        stats = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        # Modify fields
        stats.total = 200
        stats.downloaded = 150
        stats.skipped = 40
        stats.failed = 10
        stats.duration = 500.0

        # Verify modifications
        assert stats.total == 200
        assert stats.downloaded == 150
        assert stats.skipped == 40
        assert stats.failed == 10
        assert stats.duration == 500.0

    def test_success_rate_calculation(self):
        """Test calculating success rate from stats."""
        stats = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        success_rate = stats.downloaded / stats.total * 100
        assert success_rate == 75.0

    def test_failure_rate_calculation(self):
        """Test calculating failure rate from stats."""
        stats = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        failure_rate = stats.failed / stats.total * 100
        assert failure_rate == 5.0

    def test_skip_rate_calculation(self):
        """Test calculating skip rate from stats."""
        stats = DownloadStats(
            total=100,
            downloaded=75,
            skipped=20,
            failed=5,
            duration=245.3,
        )

        skip_rate = stats.skipped / stats.total * 100
        assert skip_rate == 20.0


class TestBatchDownloadOptionsAndDownloadStatsIntegration:
    """Integration tests for BatchDownloadOptions and DownloadStats."""

    def test_typical_workflow(self):
        """Test typical workflow of creating options and stats."""
        # Create options
        options = BatchDownloadOptions(
            username="john_doe",
            platform="leetcode",
            update_mode=UpdateMode.UPDATE,
            difficulty_filter=["Easy", "Medium"],
        )

        # Simulate batch download results
        stats = DownloadStats(
            total=100,
            downloaded=70,
            skipped=25,
            failed=5,
            duration=180.5,
        )

        # Verify options
        assert options.username == "john_doe"
        assert options.update_mode == UpdateMode.UPDATE

        # Verify stats
        assert stats.total == 100
        assert stats.downloaded + stats.skipped + stats.failed == stats.total

    def test_options_with_no_filters_and_complete_success(self):
        """Test options with no filters and complete success stats."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.FORCE,
        )

        stats = DownloadStats(
            total=50,
            downloaded=50,
            skipped=0,
            failed=0,
            duration=120.0,
        )

        assert options.difficulty_filter is None
        assert options.topic_filter is None
        assert stats.downloaded == stats.total
        assert stats.failed == 0

    def test_options_with_filters_and_partial_success(self):
        """Test options with filters and partial success stats."""
        options = BatchDownloadOptions(
            username="user1",
            platform="leetcode",
            update_mode=UpdateMode.SKIP,
            difficulty_filter=["Hard"],
            topic_filter=["Dynamic Programming", "Graph"],
        )

        stats = DownloadStats(
            total=20,
            downloaded=10,
            skipped=8,
            failed=2,
            duration=60.0,
        )

        assert len(options.difficulty_filter) == 1
        assert len(options.topic_filter) == 2
        assert stats.downloaded + stats.skipped + stats.failed == stats.total
