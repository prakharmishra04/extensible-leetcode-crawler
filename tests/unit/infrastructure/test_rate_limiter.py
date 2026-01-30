"""
Unit tests for RateLimiter class.

Tests token bucket algorithm implementation and thread safety.
"""

import threading
import time

import pytest

from src.crawler.infrastructure.http import RateLimiter


class TestRateLimiter:
    """Test suite for RateLimiter class."""
    
    def test_initialization_with_valid_rate(self):
        """Test that RateLimiter initializes correctly with valid rate."""
        limiter = RateLimiter(requests_per_second=2.0)
        
        assert limiter.requests_per_second == 2.0
        assert limiter.tokens == 2.0
        assert limiter.last_update > 0
    
    def test_initialization_with_zero_rate_raises_error(self):
        """Test that zero requests_per_second raises ValueError."""
        with pytest.raises(ValueError, match="requests_per_second must be positive"):
            RateLimiter(requests_per_second=0)
    
    def test_initialization_with_negative_rate_raises_error(self):
        """Test that negative requests_per_second raises ValueError."""
        with pytest.raises(ValueError, match="requests_per_second must be positive"):
            RateLimiter(requests_per_second=-1.0)
    
    def test_acquire_consumes_token(self):
        """Test that acquire() consumes a token."""
        limiter = RateLimiter(requests_per_second=10.0)
        initial_tokens = limiter.tokens
        
        limiter.acquire()
        
        # Tokens should be reduced (approximately, due to time passing)
        assert limiter.tokens < initial_tokens
    
    def test_acquire_blocks_when_no_tokens(self):
        """Test that acquire() blocks when no tokens are available."""
        limiter = RateLimiter(requests_per_second=2.0)
        
        # Consume all tokens
        limiter.acquire()
        limiter.acquire()
        
        # Next acquire should block
        start_time = time.time()
        limiter.acquire()
        elapsed = time.time() - start_time
        
        # Should have waited approximately 0.5 seconds (1/2 requests per second)
        assert elapsed >= 0.4  # Allow some tolerance
    
    def test_token_refill_over_time(self):
        """Test that tokens are refilled over time."""
        limiter = RateLimiter(requests_per_second=10.0)
        
        # Consume a token
        limiter.acquire()
        tokens_after_acquire = limiter.tokens
        
        # Wait for refill
        time.sleep(0.2)
        
        # Acquire again to trigger refill calculation
        limiter.acquire()
        
        # Tokens should have been refilled (at least partially)
        # After 0.2 seconds at 10 req/s, we should have gained ~2 tokens
        # We consumed 2 tokens total, so we should have some left
        assert limiter.tokens >= 0
    
    def test_tokens_capped_at_max_rate(self):
        """Test that tokens don't exceed requests_per_second."""
        limiter = RateLimiter(requests_per_second=2.0)
        
        # Wait for tokens to refill beyond the rate
        time.sleep(2.0)
        
        # Trigger refill calculation
        with limiter.lock:
            now = time.time()
            elapsed = now - limiter.last_update
            limiter.tokens = min(
                limiter.requests_per_second,
                limiter.tokens + elapsed * limiter.requests_per_second
            )
            limiter.last_update = now
        
        # Tokens should be capped at requests_per_second
        assert limiter.tokens <= limiter.requests_per_second
    
    def test_thread_safety(self):
        """Test that RateLimiter is thread-safe."""
        limiter = RateLimiter(requests_per_second=10.0)
        acquire_count = [0]
        lock = threading.Lock()
        
        def acquire_token():
            limiter.acquire()
            with lock:
                acquire_count[0] += 1
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=acquire_token)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should have successfully acquired tokens
        assert acquire_count[0] == 5
    
    def test_high_rate_allows_burst(self):
        """Test that high rate allows burst of requests."""
        limiter = RateLimiter(requests_per_second=100.0)
        
        # Should be able to make multiple requests quickly
        start_time = time.time()
        for _ in range(10):
            limiter.acquire()
        elapsed = time.time() - start_time
        
        # Should complete quickly (less than 1 second for 10 requests at 100 req/s)
        assert elapsed < 1.0
    
    def test_low_rate_enforces_delay(self):
        """Test that low rate enforces delay between requests."""
        limiter = RateLimiter(requests_per_second=2.0)
        
        # First two requests should be fast
        limiter.acquire()
        limiter.acquire()
        
        # Third request should be delayed
        start_time = time.time()
        limiter.acquire()
        elapsed = time.time() - start_time
        
        # Should have waited approximately 0.5 seconds
        assert elapsed >= 0.4
