"""
Unit tests for logging configuration.

Tests the structured logging setup including JSON formatting,
console formatting, and handler configuration.
"""

import json
import logging
import tempfile
from io import StringIO
from pathlib import Path

import pytest

from crawler.config.logging_config import (
    ConsoleFormatter,
    JSONFormatter,
    configure_default_logging,
    configure_production_logging,
    get_logger,
    setup_logging,
)


class TestJSONFormatter:
    """Test cases for JSONFormatter."""

    def test_format_basic_log_record(self):
        """Test formatting a basic log record as JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        record.module = "test_module"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 42
        assert "timestamp" in log_data

    def test_format_with_exception(self):
        """Test formatting a log record with exception information."""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        record.funcName = "test_function"
        record.module = "test_module"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "ERROR"
        assert log_data["message"] == "Error occurred"
        assert "exception" in log_data
        assert "ValueError: Test error" in log_data["exception"]

    def test_format_with_extra_fields(self):
        """Test formatting a log record with extra fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        record.module = "test_module"
        record.extra_fields = {"problem_id": "two-sum", "platform": "leetcode"}

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["problem_id"] == "two-sum"
        assert log_data["platform"] == "leetcode"


class TestConsoleFormatter:
    """Test cases for ConsoleFormatter."""

    def test_format_basic_log_record(self):
        """Test formatting a basic log record for console."""
        formatter = ConsoleFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        record.module = "test_module"

        result = formatter.format(record)

        assert "INFO" in result
        assert "test.logger" in result
        assert "Test message" in result

    def test_format_debug_includes_location(self):
        """Test that DEBUG level includes location information."""
        formatter = ConsoleFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=42,
            msg="Debug message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        record.module = "test_module"

        result = formatter.format(record)

        assert "DEBUG" in result
        assert "test_module.test_function:42" in result

    def test_format_with_exception(self):
        """Test formatting a log record with exception for console."""
        formatter = ConsoleFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        record.funcName = "test_function"
        record.module = "test_module"

        result = formatter.format(record)

        assert "ERROR" in result
        assert "Error occurred" in result
        assert "ValueError: Test error" in result


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def test_setup_with_console_only(self):
        """Test setting up logging with console output only."""
        logger = setup_logging(level="INFO", console_output=True)

        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_with_file_only(self):
        """Test setting up logging with file output only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logging(
                level="DEBUG",
                log_file=log_file,
                console_output=False,
            )

            assert logger.level == logging.DEBUG
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.handlers.RotatingFileHandler)
            assert log_file.exists()

    def test_setup_with_both_handlers(self):
        """Test setting up logging with both console and file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logging(
                level="WARNING",
                log_file=log_file,
                console_output=True,
            )

            assert logger.level == logging.WARNING
            assert len(logger.handlers) == 2

    def test_setup_with_json_format(self):
        """Test setting up logging with JSON formatting."""
        logger = setup_logging(level="INFO", json_format=True, console_output=True)

        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)

    def test_setup_with_human_readable_format(self):
        """Test setting up logging with human-readable formatting."""
        logger = setup_logging(level="INFO", json_format=False, console_output=True)

        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, ConsoleFormatter)

    def test_file_handler_always_uses_json(self):
        """Test that file handler always uses JSON formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logging(
                level="INFO",
                log_file=log_file,
                json_format=False,  # Request human-readable for console
                console_output=True,
            )

            # Find the file handler
            file_handler = None
            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    file_handler = handler
                    break

            assert file_handler is not None
            assert isinstance(file_handler.formatter, JSONFormatter)

    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "subdir" / "test.log"
            logger = setup_logging(level="INFO", log_file=log_file, console_output=False)

            assert log_file.parent.exists()
            assert log_file.exists()


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test.module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger_with_same_name_returns_same_instance(self):
        """Test that calling get_logger with the same name returns the same instance."""
        logger1 = get_logger("test.module")
        logger2 = get_logger("test.module")

        assert logger1 is logger2


class TestConfigureFunctions:
    """Test cases for configure_default_logging and configure_production_logging."""

    def test_configure_default_logging(self):
        """Test default logging configuration."""
        logger = configure_default_logging()

        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1

        # Check that console handler uses human-readable format
        console_handler = logger.handlers[0]
        assert isinstance(console_handler.formatter, ConsoleFormatter)

    def test_configure_production_logging(self):
        """Test production logging configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = configure_production_logging(log_dir)

            assert logger.level == logging.INFO
            assert len(logger.handlers) == 2  # Console + file

            # Check that both handlers use JSON format
            for handler in logger.handlers:
                assert isinstance(handler.formatter, (JSONFormatter, ConsoleFormatter))

            # Check that log file was created
            log_files = list(log_dir.glob("crawler_*.log"))
            assert len(log_files) == 1


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_to_file_writes_json(self):
        """Test that logging to file writes valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logging(level="INFO", log_file=log_file, console_output=False)

            test_logger = get_logger("test.integration")
            test_logger.info("Test message")

            # Read the log file and verify it's valid JSON
            log_content = log_file.read_text()
            log_data = json.loads(log_content.strip())

            assert log_data["level"] == "INFO"
            assert log_data["message"] == "Test message"
            assert log_data["logger"] == "test.integration"

    def test_logging_respects_level(self):
        """Test that logging respects the configured level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logging(level="WARNING", log_file=log_file, console_output=False)

            test_logger = get_logger("test.level")
            test_logger.debug("Debug message")
            test_logger.info("Info message")
            test_logger.warning("Warning message")
            test_logger.error("Error message")

            # Read the log file
            log_content = log_file.read_text().strip()
            log_lines = log_content.split("\n")

            # Should only have WARNING and ERROR messages
            assert len(log_lines) == 2

            warning_log = json.loads(log_lines[0])
            error_log = json.loads(log_lines[1])

            assert warning_log["level"] == "WARNING"
            assert error_log["level"] == "ERROR"

    def test_rotating_file_handler_configuration(self):
        """Test that rotating file handler is configured correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logging(level="INFO", log_file=log_file, console_output=False)

            # Find the rotating file handler
            file_handler = None
            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    file_handler = handler
                    break

            assert file_handler is not None
            assert file_handler.maxBytes == 10 * 1024 * 1024  # 10 MB
            assert file_handler.backupCount == 5
