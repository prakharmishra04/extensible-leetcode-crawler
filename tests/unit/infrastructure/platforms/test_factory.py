"""Unit tests for PlatformClientFactory."""

import logging
from unittest.mock import Mock

import pytest

from crawler.application.interfaces import PlatformClient
from crawler.config.settings import Config
from crawler.domain.exceptions import UnsupportedPlatformException
from crawler.infrastructure.http import HTTPClient
from crawler.infrastructure.platforms import PlatformClientFactory
from crawler.infrastructure.platforms.leetcode.client import LeetCodeClient


class TestPlatformClientFactory:
    """Test suite for PlatformClientFactory."""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        return Mock(spec=HTTPClient)
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config()
    
    @pytest.fixture
    def logger(self):
        """Create a test logger."""
        return logging.getLogger("test")
    
    @pytest.fixture
    def factory(self, mock_http_client, config, logger):
        """Create a PlatformClientFactory instance."""
        return PlatformClientFactory(mock_http_client, config, logger)
    
    def test_factory_initialization(self, mock_http_client, config, logger):
        """Test that factory initializes correctly with dependencies."""
        factory = PlatformClientFactory(mock_http_client, config, logger)
        
        assert factory.http_client is mock_http_client
        assert factory.config is config
        assert factory.logger is logger
    
    def test_create_leetcode_client(self, factory):
        """Test creating a LeetCode client."""
        client = factory.create("leetcode")
        
        assert isinstance(client, LeetCodeClient)
        assert isinstance(client, PlatformClient)
    
    def test_create_leetcode_client_case_insensitive(self, factory):
        """Test that platform name is case-insensitive."""
        # Test various case combinations
        for platform_name in ["leetcode", "LeetCode", "LEETCODE", "LeEtCoDe"]:
            client = factory.create(platform_name)
            assert isinstance(client, LeetCodeClient)
    
    def test_create_unsupported_platform_raises_exception(self, factory):
        """Test that creating an unsupported platform raises UnsupportedPlatformException."""
        with pytest.raises(UnsupportedPlatformException) as exc_info:
            factory.create("hackerrank")
        
        assert exc_info.value.platform == "hackerrank"
        assert "hackerrank" in str(exc_info.value).lower()
    
    def test_create_unsupported_platform_various_names(self, factory):
        """Test that various unsupported platform names raise exceptions."""
        unsupported_platforms = [
            "hackerrank",
            "codechef",
            "codeforces",
            "topcoder",
            "atcoder",
            "unknown",
            "invalid",
            ""
        ]
        
        for platform in unsupported_platforms:
            with pytest.raises(UnsupportedPlatformException) as exc_info:
                factory.create(platform)
            assert exc_info.value.platform == platform.lower()
    
    def test_create_logs_leetcode_creation(self, factory, logger, caplog):
        """Test that creating LeetCode client logs the operation."""
        with caplog.at_level(logging.INFO):
            factory.create("leetcode")
        
        # Check that info log was created
        assert any("leetcode" in record.message.lower() for record in caplog.records)
    
    def test_create_logs_unsupported_platform_error(self, factory, logger, caplog):
        """Test that unsupported platform logs an error."""
        with caplog.at_level(logging.ERROR):
            try:
                factory.create("unsupported")
            except UnsupportedPlatformException:
                pass
        
        # Check that error log was created
        assert any("unsupported" in record.message.lower() for record in caplog.records)
        assert any(record.levelname == "ERROR" for record in caplog.records)
    
    def test_created_client_has_correct_dependencies(self, factory, mock_http_client, config, logger):
        """Test that created client has the correct injected dependencies."""
        client = factory.create("leetcode")
        
        # Verify the client has the correct dependencies
        assert client.http_client is mock_http_client
        assert client.config is config
        assert client.logger is logger
    
    def test_factory_creates_new_instance_each_time(self, factory):
        """Test that factory creates a new client instance each time."""
        client1 = factory.create("leetcode")
        client2 = factory.create("leetcode")
        
        # Should be different instances
        assert client1 is not client2
        
        # But both should be LeetCodeClient instances
        assert isinstance(client1, LeetCodeClient)
        assert isinstance(client2, LeetCodeClient)
    
    def test_factory_supports_only_leetcode_currently(self, factory):
        """Test that factory currently only supports LeetCode platform."""
        # This test documents the current state - only LeetCode is supported
        # When new platforms are added, this test should be updated
        
        # LeetCode should work
        client = factory.create("leetcode")
        assert isinstance(client, LeetCodeClient)
        
        # Other platforms should raise exceptions
        future_platforms = ["hackerrank", "codechef", "codeforces"]
        for platform in future_platforms:
            with pytest.raises(UnsupportedPlatformException):
                factory.create(platform)


class TestPlatformClientFactoryExtensibility:
    """Test suite for factory extensibility patterns."""
    
    @pytest.fixture
    def factory(self):
        """Create a factory with mock dependencies."""
        mock_http_client = Mock(spec=HTTPClient)
        config = Config()
        logger = logging.getLogger("test")
        return PlatformClientFactory(mock_http_client, config, logger)
    
    def test_factory_pattern_enables_runtime_platform_selection(self, factory):
        """Test that factory enables runtime platform selection.
        
        This test validates Requirement 1.2: Factory pattern enables
        platform selection at runtime.
        """
        # Platform can be determined at runtime (e.g., from config or CLI)
        platform_name = "leetcode"  # Could come from user input
        
        client = factory.create(platform_name)
        
        assert isinstance(client, PlatformClient)
        assert isinstance(client, LeetCodeClient)
    
    def test_factory_provides_clear_error_for_future_platforms(self, factory):
        """Test that factory provides clear error messages for future platforms.
        
        This test validates that the factory provides helpful error messages
        when users try to use platforms that aren't implemented yet.
        """
        with pytest.raises(UnsupportedPlatformException) as exc_info:
            factory.create("hackerrank")
        
        # Error message should be clear and include the platform name
        error_message = str(exc_info.value)
        assert "hackerrank" in error_message.lower()
        assert "not supported" in error_message.lower()
    
    def test_factory_centralizes_client_creation(self, factory):
        """Test that factory centralizes client creation logic.
        
        This test validates that the factory provides a single point
        for creating platform clients, making it easy to add new platforms.
        """
        # All client creation goes through the factory
        client = factory.create("leetcode")
        
        # The factory handles all the complexity of:
        # - Creating the adapter
        # - Injecting dependencies
        # - Configuring the client
        assert isinstance(client, LeetCodeClient)
        assert hasattr(client, 'http_client')
        assert hasattr(client, 'adapter')
        assert hasattr(client, 'config')
        assert hasattr(client, 'logger')
