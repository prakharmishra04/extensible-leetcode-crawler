"""Unit tests for Percentiles value object"""

import pytest

from src.crawler.domain.value_objects import Percentiles


class TestPercentiles:
    """Test suite for Percentiles value object"""

    def test_valid_percentiles(self):
        """Test creating valid percentiles"""
        perc = Percentiles(runtime=85.5, memory=92.3)
        assert perc.runtime == 85.5
        assert perc.memory == 92.3

    def test_zero_percentiles(self):
        """Test creating percentiles with zero values"""
        perc = Percentiles(runtime=0.0, memory=0.0)
        assert perc.runtime == 0.0
        assert perc.memory == 0.0

    def test_hundred_percentiles(self):
        """Test creating percentiles with 100 values"""
        perc = Percentiles(runtime=100.0, memory=100.0)
        assert perc.runtime == 100.0
        assert perc.memory == 100.0

    def test_negative_runtime_raises_error(self):
        """Test that negative runtime raises ValueError"""
        with pytest.raises(ValueError, match="Runtime percentile must be between 0 and 100"):
            Percentiles(runtime=-1.0, memory=50.0)

    def test_negative_memory_raises_error(self):
        """Test that negative memory raises ValueError"""
        with pytest.raises(ValueError, match="Memory percentile must be between 0 and 100"):
            Percentiles(runtime=50.0, memory=-1.0)

    def test_runtime_over_100_raises_error(self):
        """Test that runtime over 100 raises ValueError"""
        with pytest.raises(ValueError, match="Runtime percentile must be between 0 and 100"):
            Percentiles(runtime=101.0, memory=50.0)

    def test_memory_over_100_raises_error(self):
        """Test that memory over 100 raises ValueError"""
        with pytest.raises(ValueError, match="Memory percentile must be between 0 and 100"):
            Percentiles(runtime=50.0, memory=101.0)

    def test_percentiles_is_immutable(self):
        """Test that Percentiles is immutable"""
        perc = Percentiles(runtime=85.5, memory=92.3)
        with pytest.raises(AttributeError):
            perc.runtime = 90.0

    def test_percentiles_equality(self):
        """Test that two percentiles with same values are equal"""
        perc1 = Percentiles(runtime=85.5, memory=92.3)
        perc2 = Percentiles(runtime=85.5, memory=92.3)
        assert perc1 == perc2
