"""
Unit tests for HTTPClient class.

Tests retry logic, rate limiting integration, and error handling.
"""

import logging
from unittest.mock import Mock, patch

import pytest
import requests

from src.crawler.domain.exceptions import NetworkException
from src.crawler.infrastructure.http import HTTPClient, RateLimiter, RetryConfig


class TestHTTPClient:
    """Test suite for HTTPClient class."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return Mock(spec=logging.Logger)
    
    @pytest.fixture
    def retry_config(self):
        """Create a retry config for testing."""
        return RetryConfig(
            max_retries=3,
            initial_delay=0.1,  # Short delay for faster tests
            max_delay=1.0,
            exponential_base=2.0,
            jitter=False  # Disable jitter for predictable tests
        )
    
    @pytest.fixture
    def rate_limiter(self):
        """Create a rate limiter for testing."""
        return RateLimiter(requests_per_second=100.0)  # High rate for fast tests
    
    @pytest.fixture
    def http_client(self, retry_config, rate_limiter, mock_logger):
        """Create an HTTPClient for testing."""
        return HTTPClient(retry_config, rate_limiter, mock_logger)
    
    def test_initialization(self, http_client, retry_config, rate_limiter, mock_logger):
        """Test that HTTPClient initializes correctly."""
        assert http_client.retry_config == retry_config
        assert http_client.rate_limiter == rate_limiter
        assert http_client.logger == mock_logger
        assert http_client.session is not None
    
    @patch('requests.Session.request')
    def test_successful_get_request(self, mock_request, http_client):
        """Test successful GET request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Make request
        response = http_client.get("https://api.example.com/data")
        
        # Verify
        assert response == mock_response
        mock_request.assert_called_once()
        assert mock_request.call_args[0][0] == "GET"
        assert mock_request.call_args[0][1] == "https://api.example.com/data"
    
    @patch('requests.Session.request')
    def test_successful_post_request(self, mock_request, http_client):
        """Test successful POST request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Make request
        json_data = {"key": "value"}
        response = http_client.post("https://api.example.com/data", json=json_data)
        
        # Verify
        assert response == mock_response
        mock_request.assert_called_once()
        assert mock_request.call_args[0][0] == "POST"
        assert mock_request.call_args[1]["json"] == json_data
    
    @patch('requests.Session.request')
    def test_retry_on_network_error(self, mock_request, http_client, mock_logger):
        """Test that network errors trigger retry."""
        # Setup mock to fail twice then succeed
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response
        ]
        
        # Make request
        response = http_client.get("https://api.example.com/data")
        
        # Verify
        assert response == mock_response
        assert mock_request.call_count == 3
        assert mock_logger.warning.call_count == 2
    
    @patch('requests.Session.request')
    def test_retry_on_500_error(self, mock_request, http_client, mock_logger):
        """Test that 5xx errors trigger retry."""
        # Setup mock to return 500 twice then succeed
        mock_error_response = Mock()
        mock_error_response.status_code = 500
        
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        
        mock_request.side_effect = [
            mock_error_response,
            mock_error_response,
            mock_success_response
        ]
        
        # Make request
        response = http_client.get("https://api.example.com/data")
        
        # Verify
        assert response == mock_success_response
        assert mock_request.call_count == 3
    
    @patch('requests.Session.request')
    def test_no_retry_on_400_error(self, mock_request, http_client):
        """Test that 4xx errors don't trigger retry."""
        # Setup mock to return 400
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad request")
        mock_request.return_value = mock_response
        
        # Make request and expect immediate failure
        with pytest.raises(requests.exceptions.HTTPError):
            http_client.get("https://api.example.com/data")
        
        # Should only try once (no retries for 4xx)
        assert mock_request.call_count == 1
    
    @patch('requests.Session.request')
    def test_max_retries_exhausted(self, mock_request, http_client, mock_logger):
        """Test that NetworkException is raised after max retries."""
        # Setup mock to always fail
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Make request and expect NetworkException
        with pytest.raises(NetworkException) as exc_info:
            http_client.get("https://api.example.com/data")
        
        # Verify
        assert "Request failed after 3 attempts" in str(exc_info.value)
        assert exc_info.value.url == "https://api.example.com/data"
        assert mock_request.call_count == 3
        assert mock_logger.error.call_count == 1
    
    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_exponential_backoff_delays(self, mock_sleep, mock_request, http_client):
        """Test that delays follow exponential backoff pattern."""
        # Setup mock to fail twice then succeed
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response
        ]
        
        # Make request
        http_client.get("https://api.example.com/data")
        
        # Verify exponential backoff delays
        assert mock_sleep.call_count == 2
        delays = [call[0][0] for call in mock_sleep.call_args_list]
        
        # First delay: 0.1 * (2^0) = 0.1
        # Second delay: 0.1 * (2^1) = 0.2
        assert delays[0] == pytest.approx(0.1, rel=0.01)
        assert delays[1] == pytest.approx(0.2, rel=0.01)
    
    @patch('requests.Session.request')
    def test_rate_limiter_integration(self, mock_request, retry_config, mock_logger):
        """Test that rate limiter is called for each request."""
        # Create a mock rate limiter
        mock_rate_limiter = Mock(spec=RateLimiter)
        client = HTTPClient(retry_config, mock_rate_limiter, mock_logger)
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Make request
        client.get("https://api.example.com/data")
        
        # Verify rate limiter was called
        mock_rate_limiter.acquire.assert_called_once()
    
    def test_calculate_delay_without_jitter(self, http_client):
        """Test delay calculation without jitter."""
        # Delays should be: 0.1, 0.2, 0.4, 0.8 (capped at 1.0)
        assert http_client._calculate_delay(0) == pytest.approx(0.1, rel=0.01)
        assert http_client._calculate_delay(1) == pytest.approx(0.2, rel=0.01)
        assert http_client._calculate_delay(2) == pytest.approx(0.4, rel=0.01)
        assert http_client._calculate_delay(3) == pytest.approx(0.8, rel=0.01)
        assert http_client._calculate_delay(4) == pytest.approx(1.0, rel=0.01)  # Capped at max_delay
    
    def test_calculate_delay_with_jitter(self, retry_config, rate_limiter, mock_logger):
        """Test delay calculation with jitter."""
        # Enable jitter
        retry_config.jitter = True
        client = HTTPClient(retry_config, rate_limiter, mock_logger)
        
        # Calculate delay multiple times
        delays = [client._calculate_delay(0) for _ in range(10)]
        
        # All delays should be between 0.05 and 0.1 (0.1 * [0.5, 1.0])
        for delay in delays:
            assert 0.05 <= delay <= 0.1
        
        # Delays should vary (not all the same)
        assert len(set(delays)) > 1
    
    def test_calculate_delay_respects_max_delay(self, http_client):
        """Test that calculated delay never exceeds max_delay."""
        # Test with large attempt numbers
        for attempt in range(10, 20):
            delay = http_client._calculate_delay(attempt)
            assert delay <= http_client.retry_config.max_delay
    
    @patch('requests.Session.request')
    def test_custom_headers_passed_through(self, mock_request, http_client):
        """Test that custom headers are passed to the request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        headers = {"Authorization": "Bearer token123"}
        http_client.get("https://api.example.com/data", headers=headers)
        
        assert mock_request.call_args[1]["headers"] == headers
    
    @patch('requests.Session.request')
    def test_query_params_passed_through(self, mock_request, http_client):
        """Test that query parameters are passed to the request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        params = {"page": 1, "limit": 10}
        http_client.get("https://api.example.com/data", params=params)
        
        assert mock_request.call_args[1]["params"] == params
