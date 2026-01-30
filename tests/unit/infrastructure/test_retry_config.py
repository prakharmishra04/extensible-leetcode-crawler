"""
Unit tests for RetryConfig dataclass.

Tests validation logic and default values for retry configuration.
"""

import pytest

from src.crawler.infrastructure.http import RetryConfig


class TestRetryConfig:
    """Test suite for RetryConfig dataclass."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
    
    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False
        )
        
        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False
    
    def test_negative_max_retries_raises_error(self):
        """Test that negative max_retries raises ValueError."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            RetryConfig(max_retries=-1)
    
    def test_zero_max_retries_is_valid(self):
        """Test that zero max_retries is valid (no retries)."""
        config = RetryConfig(max_retries=0)
        assert config.max_retries == 0
    
    def test_zero_initial_delay_raises_error(self):
        """Test that zero initial_delay raises ValueError."""
        with pytest.raises(ValueError, match="initial_delay must be positive"):
            RetryConfig(initial_delay=0)
    
    def test_negative_initial_delay_raises_error(self):
        """Test that negative initial_delay raises ValueError."""
        with pytest.raises(ValueError, match="initial_delay must be positive"):
            RetryConfig(initial_delay=-1.0)
    
    def test_zero_max_delay_raises_error(self):
        """Test that zero max_delay raises ValueError."""
        with pytest.raises(ValueError, match="max_delay must be positive"):
            RetryConfig(max_delay=0)
    
    def test_negative_max_delay_raises_error(self):
        """Test that negative max_delay raises ValueError."""
        with pytest.raises(ValueError, match="max_delay must be positive"):
            RetryConfig(max_delay=-1.0)
    
    def test_max_delay_less_than_initial_delay_raises_error(self):
        """Test that max_delay < initial_delay raises ValueError."""
        with pytest.raises(ValueError, match="max_delay must be greater than or equal to initial_delay"):
            RetryConfig(initial_delay=10.0, max_delay=5.0)
    
    def test_max_delay_equal_to_initial_delay_is_valid(self):
        """Test that max_delay == initial_delay is valid."""
        config = RetryConfig(initial_delay=5.0, max_delay=5.0)
        assert config.initial_delay == 5.0
        assert config.max_delay == 5.0
    
    def test_exponential_base_one_raises_error(self):
        """Test that exponential_base == 1 raises ValueError."""
        with pytest.raises(ValueError, match="exponential_base must be greater than 1"):
            RetryConfig(exponential_base=1.0)
    
    def test_exponential_base_less_than_one_raises_error(self):
        """Test that exponential_base < 1 raises ValueError."""
        with pytest.raises(ValueError, match="exponential_base must be greater than 1"):
            RetryConfig(exponential_base=0.5)
    
    def test_exponential_base_greater_than_one_is_valid(self):
        """Test that exponential_base > 1 is valid."""
        config = RetryConfig(exponential_base=1.5)
        assert config.exponential_base == 1.5
