"""
Unit tests for domain exceptions.

This module tests all exception classes in the crawler exception hierarchy,
verifying that they:
- Initialize correctly with required parameters
- Store attributes properly
- Generate appropriate error messages
- Inherit from the correct base classes
"""

import pytest

from crawler.domain.exceptions import (
    AuthenticationException,
    CommandException,
    CommandExecutionException,
    CommandValidationException,
    ConfigurationException,
    CrawlerException,
    NetworkException,
    ProblemNotFoundException,
    RepositoryException,
    UnsupportedPlatformException,
    ValidationException,
)


class TestCrawlerException:
    """Tests for the base CrawlerException class."""
    
    def test_crawler_exception_inherits_from_exception(self):
        """Test that CrawlerException inherits from Exception."""
        assert issubclass(CrawlerException, Exception)
    
    def test_crawler_exception_can_be_raised(self):
        """Test that CrawlerException can be raised and caught."""
        with pytest.raises(CrawlerException, match="Test error"):
            raise CrawlerException("Test error")
    
    def test_crawler_exception_message(self):
        """Test that CrawlerException stores the error message."""
        exc = CrawlerException("Test error message")
        assert str(exc) == "Test error message"


class TestNetworkException:
    """Tests for NetworkException."""
    
    def test_network_exception_inherits_from_crawler_exception(self):
        """Test that NetworkException inherits from CrawlerException."""
        assert issubclass(NetworkException, CrawlerException)
    
    def test_network_exception_with_message_only(self):
        """Test NetworkException with only a message."""
        exc = NetworkException("Connection failed")
        assert str(exc) == "Connection failed"
        assert exc.url is None
        assert exc.status_code is None
    
    def test_network_exception_with_url(self):
        """Test NetworkException with URL."""
        exc = NetworkException(
            "Connection failed",
            url="https://api.example.com/problems"
        )
        assert str(exc) == "Connection failed"
        assert exc.url == "https://api.example.com/problems"
        assert exc.status_code is None
    
    def test_network_exception_with_status_code(self):
        """Test NetworkException with status code."""
        exc = NetworkException(
            "Server error",
            status_code=500
        )
        assert str(exc) == "Server error"
        assert exc.url is None
        assert exc.status_code == 500
    
    def test_network_exception_with_all_parameters(self):
        """Test NetworkException with all parameters."""
        exc = NetworkException(
            "Request failed",
            url="https://api.example.com/problems",
            status_code=429
        )
        assert str(exc) == "Request failed"
        assert exc.url == "https://api.example.com/problems"
        assert exc.status_code == 429
    
    def test_network_exception_can_be_caught_as_crawler_exception(self):
        """Test that NetworkException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise NetworkException("Connection failed")


class TestProblemNotFoundException:
    """Tests for ProblemNotFoundException."""
    
    def test_problem_not_found_exception_inherits_from_crawler_exception(self):
        """Test that ProblemNotFoundException inherits from CrawlerException."""
        assert issubclass(ProblemNotFoundException, CrawlerException)
    
    def test_problem_not_found_exception_message(self):
        """Test ProblemNotFoundException generates correct message."""
        exc = ProblemNotFoundException("two-sum", "leetcode")
        assert str(exc) == "Problem 'two-sum' not found on leetcode"
        assert exc.problem_id == "two-sum"
        assert exc.platform == "leetcode"
    
    def test_problem_not_found_exception_stores_attributes(self):
        """Test that ProblemNotFoundException stores problem_id and platform."""
        exc = ProblemNotFoundException("valid-parentheses", "hackerrank")
        assert exc.problem_id == "valid-parentheses"
        assert exc.platform == "hackerrank"
    
    def test_problem_not_found_exception_can_be_caught_as_crawler_exception(self):
        """Test that ProblemNotFoundException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise ProblemNotFoundException("test-problem", "leetcode")


class TestAuthenticationException:
    """Tests for AuthenticationException."""
    
    def test_authentication_exception_inherits_from_crawler_exception(self):
        """Test that AuthenticationException inherits from CrawlerException."""
        assert issubclass(AuthenticationException, CrawlerException)
    
    def test_authentication_exception_message(self):
        """Test AuthenticationException generates correct message."""
        exc = AuthenticationException("leetcode", "Invalid session token")
        assert str(exc) == "Authentication failed for leetcode: Invalid session token"
        assert exc.platform == "leetcode"
        assert exc.reason == "Invalid session token"
    
    def test_authentication_exception_stores_attributes(self):
        """Test that AuthenticationException stores platform and reason."""
        exc = AuthenticationException("hackerrank", "API key expired")
        assert exc.platform == "hackerrank"
        assert exc.reason == "API key expired"
    
    def test_authentication_exception_can_be_caught_as_crawler_exception(self):
        """Test that AuthenticationException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise AuthenticationException("leetcode", "Invalid credentials")


class TestUnsupportedPlatformException:
    """Tests for UnsupportedPlatformException."""
    
    def test_unsupported_platform_exception_inherits_from_crawler_exception(self):
        """Test that UnsupportedPlatformException inherits from CrawlerException."""
        assert issubclass(UnsupportedPlatformException, CrawlerException)
    
    def test_unsupported_platform_exception_message(self):
        """Test UnsupportedPlatformException generates correct message."""
        exc = UnsupportedPlatformException("topcoder")
        assert str(exc) == "Platform 'topcoder' is not supported"
        assert exc.platform == "topcoder"
    
    def test_unsupported_platform_exception_stores_platform(self):
        """Test that UnsupportedPlatformException stores platform."""
        exc = UnsupportedPlatformException("atcoder")
        assert exc.platform == "atcoder"
    
    def test_unsupported_platform_exception_can_be_caught_as_crawler_exception(self):
        """Test that UnsupportedPlatformException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise UnsupportedPlatformException("unknown")


class TestValidationException:
    """Tests for ValidationException."""
    
    def test_validation_exception_inherits_from_crawler_exception(self):
        """Test that ValidationException inherits from CrawlerException."""
        assert issubclass(ValidationException, CrawlerException)
    
    def test_validation_exception_message(self):
        """Test ValidationException generates correct message."""
        exc = ValidationException("problem_id", "", "cannot be empty")
        assert str(exc) == "Validation failed for problem_id='': cannot be empty"
        assert exc.field == "problem_id"
        assert exc.value == ""
        assert exc.reason == "cannot be empty"
    
    def test_validation_exception_with_numeric_value(self):
        """Test ValidationException with numeric value."""
        exc = ValidationException("acceptance_rate", 150, "must be between 0 and 100")
        assert str(exc) == "Validation failed for acceptance_rate='150': must be between 0 and 100"
        assert exc.field == "acceptance_rate"
        assert exc.value == 150
        assert exc.reason == "must be between 0 and 100"
    
    def test_validation_exception_stores_attributes(self):
        """Test that ValidationException stores field, value, and reason."""
        exc = ValidationException("difficulty", "Super Hard", "invalid level")
        assert exc.field == "difficulty"
        assert exc.value == "Super Hard"
        assert exc.reason == "invalid level"
    
    def test_validation_exception_can_be_caught_as_crawler_exception(self):
        """Test that ValidationException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise ValidationException("field", "value", "reason")


class TestRepositoryException:
    """Tests for RepositoryException."""
    
    def test_repository_exception_inherits_from_crawler_exception(self):
        """Test that RepositoryException inherits from CrawlerException."""
        assert issubclass(RepositoryException, CrawlerException)
    
    def test_repository_exception_can_be_raised(self):
        """Test that RepositoryException can be raised and caught."""
        with pytest.raises(RepositoryException, match="Failed to save problem"):
            raise RepositoryException("Failed to save problem")
    
    def test_repository_exception_message(self):
        """Test that RepositoryException stores the error message."""
        exc = RepositoryException("Permission denied")
        assert str(exc) == "Permission denied"
    
    def test_repository_exception_can_be_caught_as_crawler_exception(self):
        """Test that RepositoryException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise RepositoryException("Repository error")


class TestCommandException:
    """Tests for the base CommandException class."""
    
    def test_command_exception_inherits_from_crawler_exception(self):
        """Test that CommandException inherits from CrawlerException."""
        assert issubclass(CommandException, CrawlerException)
    
    def test_command_exception_can_be_raised(self):
        """Test that CommandException can be raised and caught."""
        with pytest.raises(CommandException, match="Command error"):
            raise CommandException("Command error")
    
    def test_command_exception_message(self):
        """Test that CommandException stores the error message."""
        exc = CommandException("Command failed")
        assert str(exc) == "Command failed"
    
    def test_command_exception_can_be_caught_as_crawler_exception(self):
        """Test that CommandException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise CommandException("Command error")


class TestCommandValidationException:
    """Tests for CommandValidationException."""
    
    def test_command_validation_exception_inherits_from_command_exception(self):
        """Test that CommandValidationException inherits from CommandException."""
        assert issubclass(CommandValidationException, CommandException)
    
    def test_command_validation_exception_message(self):
        """Test CommandValidationException generates correct message."""
        exc = CommandValidationException("download", "problem_id", "cannot be empty")
        expected = "Invalid argument 'problem_id' for command 'download': cannot be empty"
        assert str(exc) == expected
        assert exc.command == "download"
        assert exc.argument == "problem_id"
        assert exc.reason == "cannot be empty"
    
    def test_command_validation_exception_stores_attributes(self):
        """Test that CommandValidationException stores command, argument, and reason."""
        exc = CommandValidationException("batch", "difficulty", "invalid value")
        assert exc.command == "batch"
        assert exc.argument == "difficulty"
        assert exc.reason == "invalid value"
    
    def test_command_validation_exception_can_be_caught_as_command_exception(self):
        """Test that CommandValidationException can be caught as CommandException."""
        with pytest.raises(CommandException):
            raise CommandValidationException("list", "sort_by", "invalid field")
    
    def test_command_validation_exception_can_be_caught_as_crawler_exception(self):
        """Test that CommandValidationException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise CommandValidationException("download", "platform", "unsupported")


class TestConfigurationException:
    """Tests for ConfigurationException."""
    
    def test_configuration_exception_inherits_from_crawler_exception(self):
        """Test that ConfigurationException inherits from CrawlerException."""
        assert issubclass(ConfigurationException, CrawlerException)
    
    def test_configuration_exception_message(self):
        """Test ConfigurationException generates correct message."""
        exc = ConfigurationException("file", "config.yaml not found")
        assert str(exc) == "Configuration error from file: config.yaml not found"
        assert exc.config_source == "file"
        assert exc.reason == "config.yaml not found"
    
    def test_configuration_exception_with_env_source(self):
        """Test ConfigurationException with environment variable source."""
        exc = ConfigurationException("env", "LEETCODE_SESSION not set")
        assert str(exc) == "Configuration error from env: LEETCODE_SESSION not set"
        assert exc.config_source == "env"
        assert exc.reason == "LEETCODE_SESSION not set"
    
    def test_configuration_exception_with_cli_source(self):
        """Test ConfigurationException with CLI argument source."""
        exc = ConfigurationException("cli", "invalid format specified")
        assert str(exc) == "Configuration error from cli: invalid format specified"
        assert exc.config_source == "cli"
        assert exc.reason == "invalid format specified"
    
    def test_configuration_exception_stores_attributes(self):
        """Test that ConfigurationException stores config_source and reason."""
        exc = ConfigurationException("file", "invalid YAML syntax")
        assert exc.config_source == "file"
        assert exc.reason == "invalid YAML syntax"
    
    def test_configuration_exception_can_be_caught_as_crawler_exception(self):
        """Test that ConfigurationException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise ConfigurationException("file", "parse error")


class TestCommandExecutionException:
    """Tests for CommandExecutionException."""
    
    def test_command_execution_exception_inherits_from_command_exception(self):
        """Test that CommandExecutionException inherits from CommandException."""
        assert issubclass(CommandExecutionException, CommandException)
    
    def test_command_execution_exception_message(self):
        """Test CommandExecutionException generates correct message."""
        exc = CommandExecutionException("download", "unexpected error occurred")
        assert str(exc) == "Command 'download' execution failed: unexpected error occurred"
        assert exc.command == "download"
        assert exc.reason == "unexpected error occurred"
        assert exc.original_exception is None
    
    def test_command_execution_exception_with_original_exception(self):
        """Test CommandExecutionException with original exception."""
        original = ValueError("Invalid input")
        exc = CommandExecutionException(
            "batch",
            "validation failed",
            original_exception=original
        )
        assert str(exc) == "Command 'batch' execution failed: validation failed"
        assert exc.command == "batch"
        assert exc.reason == "validation failed"
        assert exc.original_exception is original
    
    def test_command_execution_exception_stores_attributes(self):
        """Test that CommandExecutionException stores command, reason, and original_exception."""
        original = RuntimeError("Something went wrong")
        exc = CommandExecutionException(
            "list",
            "runtime error",
            original_exception=original
        )
        assert exc.command == "list"
        assert exc.reason == "runtime error"
        assert exc.original_exception is original
    
    def test_command_execution_exception_can_be_caught_as_command_exception(self):
        """Test that CommandExecutionException can be caught as CommandException."""
        with pytest.raises(CommandException):
            raise CommandExecutionException("download", "execution failed")
    
    def test_command_execution_exception_can_be_caught_as_crawler_exception(self):
        """Test that CommandExecutionException can be caught as CrawlerException."""
        with pytest.raises(CrawlerException):
            raise CommandExecutionException("batch", "execution failed")


class TestExceptionHierarchy:
    """Tests for the overall exception hierarchy."""
    
    def test_all_exceptions_inherit_from_crawler_exception(self):
        """Test that all custom exceptions inherit from CrawlerException."""
        exceptions = [
            NetworkException,
            ProblemNotFoundException,
            AuthenticationException,
            UnsupportedPlatformException,
            ValidationException,
            RepositoryException,
            CommandException,
            CommandValidationException,
            ConfigurationException,
            CommandExecutionException,
        ]
        
        for exc_class in exceptions:
            assert issubclass(exc_class, CrawlerException), \
                f"{exc_class.__name__} should inherit from CrawlerException"
    
    def test_command_exceptions_inherit_from_command_exception(self):
        """Test that CLI command exceptions inherit from CommandException."""
        command_exceptions = [
            CommandValidationException,
            CommandExecutionException,
        ]
        
        for exc_class in command_exceptions:
            assert issubclass(exc_class, CommandException), \
                f"{exc_class.__name__} should inherit from CommandException"
    
    def test_all_exceptions_can_be_caught_as_exception(self):
        """Test that all custom exceptions can be caught as base Exception."""
        exceptions = [
            (NetworkException, ("message",)),
            (ProblemNotFoundException, ("id", "platform")),
            (AuthenticationException, ("platform", "reason")),
            (UnsupportedPlatformException, ("platform",)),
            (ValidationException, ("field", "value", "reason")),
            (RepositoryException, ("message",)),
            (CommandException, ("message",)),
            (CommandValidationException, ("command", "arg", "reason")),
            (ConfigurationException, ("source", "reason")),
            (CommandExecutionException, ("command", "reason")),
        ]
        
        for exc_class, args in exceptions:
            with pytest.raises(Exception):
                raise exc_class(*args)


class TestExceptionUsagePatterns:
    """Tests for common exception usage patterns."""
    
    def test_catching_specific_exception(self):
        """Test catching a specific exception type."""
        with pytest.raises(NetworkException) as exc_info:
            raise NetworkException("Connection failed", url="https://api.example.com")
        
        assert exc_info.value.url == "https://api.example.com"
    
    def test_catching_base_crawler_exception(self):
        """Test catching any CrawlerException."""
        exceptions_to_test = [
            NetworkException("Network error"),
            ProblemNotFoundException("id", "platform"),
            AuthenticationException("platform", "reason"),
            ValidationException("field", "value", "reason"),
        ]
        
        for exc in exceptions_to_test:
            with pytest.raises(CrawlerException):
                raise exc
    
    def test_exception_chaining(self):
        """Test exception chaining with original exception."""
        original = ValueError("Invalid value")
        
        try:
            raise original
        except ValueError as e:
            exc = CommandExecutionException(
                "download",
                "validation failed",
                original_exception=e
            )
            assert exc.original_exception is original
    
    def test_multiple_exception_handlers(self):
        """Test handling different exception types differently."""
        def raise_exception(exc_type):
            if exc_type == "network":
                raise NetworkException("Network error")
            elif exc_type == "auth":
                raise AuthenticationException("leetcode", "Invalid token")
            elif exc_type == "validation":
                raise ValidationException("field", "value", "invalid")
        
        # Test network exception
        with pytest.raises(NetworkException):
            raise_exception("network")
        
        # Test authentication exception
        with pytest.raises(AuthenticationException):
            raise_exception("auth")
        
        # Test validation exception
        with pytest.raises(ValidationException):
            raise_exception("validation")
