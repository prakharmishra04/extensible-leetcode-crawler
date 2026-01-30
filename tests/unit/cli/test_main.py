"""
Unit tests for the main CLI entry point.

This module tests the main CLI functionality including:
- Argument parsing
- Configuration loading
- Dependency injection
- Command execution
- Error handling
"""

import argparse
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

import pytest

from crawler.cli.main import (
    create_main_parser,
    load_configuration,
    setup_logging_from_args,
    create_formatter,
    create_http_client,
    execute_download_command,
    execute_batch_command,
    execute_list_command,
    main,
)
from crawler.config.settings import Config
from crawler.domain.entities import UpdateMode
from crawler.infrastructure.formatters.python_formatter import PythonFormatter
from crawler.infrastructure.formatters.markdown_formatter import MarkdownFormatter
from crawler.infrastructure.formatters.json_formatter import JSONFormatter
from crawler.infrastructure.http.client import HTTPClient


class TestCreateMainParser:
    """Tests for create_main_parser function."""
    
    def test_creates_parser_with_subcommands(self):
        """Test that parser is created with all subcommands."""
        parser = create_main_parser()
        
        assert parser is not None
        assert isinstance(parser, argparse.ArgumentParser)
    
    def test_parser_has_global_options(self):
        """Test that parser has global options."""
        parser = create_main_parser()
        
        # Parse with global options
        args = parser.parse_args([
            "--config", "config.yaml",
            "--verbose",
            "download", "two-sum", "--platform", "leetcode"
        ])
        
        assert args.config == Path("config.yaml")
        assert args.verbose is True
        assert args.command == "download"
    
    def test_parser_requires_command(self):
        """Test that parser requires a command."""
        parser = create_main_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args([])
    
    def test_parser_supports_download_command(self):
        """Test that parser supports download command."""
        parser = create_main_parser()
        
        args = parser.parse_args([
            "download", "two-sum",
            "--platform", "leetcode",
            "--force",
            "--format", "markdown"
        ])
        
        assert args.command == "download"
        assert args.problem_id == "two-sum"
        assert args.platform == "leetcode"
        assert args.force is True
        assert args.format == "markdown"
    
    def test_parser_supports_batch_command(self):
        """Test that parser supports batch command."""
        parser = create_main_parser()
        
        args = parser.parse_args([
            "batch", "john_doe",
            "--platform", "leetcode",
            "--mode", "skip",
            "--difficulty", "Easy", "Medium",
            "--format", "json"
        ])
        
        assert args.command == "batch"
        assert args.username == "john_doe"
        assert args.platform == "leetcode"
        assert args.mode == "skip"
        assert args.difficulty == ["Easy", "Medium"]
        assert args.format == "json"
    
    def test_parser_supports_list_command(self):
        """Test that parser supports list command."""
        parser = create_main_parser()
        
        args = parser.parse_args([
            "list",
            "--platform", "leetcode",
            "--difficulty", "Easy",
            "--sort-by", "acceptance_rate",
            "--reverse"
        ])
        
        assert args.command == "list"
        assert args.platform == "leetcode"
        assert args.difficulty == ["Easy"]
        assert args.sort_by == "acceptance_rate"
        assert args.reverse is True
    
    def test_parser_has_version_option(self):
        """Test that parser has version option."""
        parser = create_main_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        
        assert exc_info.value.code == 0


class TestLoadConfiguration:
    """Tests for load_configuration function."""
    
    def test_loads_default_configuration(self):
        """Test loading default configuration."""
        args = argparse.Namespace(
            config=None,
            output_dir=None,
        )
        
        config = load_configuration(args)
        
        assert isinstance(config, Config)
        assert config.output_dir == "./problems"
    
    def test_loads_configuration_with_cli_output_dir(self):
        """Test loading configuration with CLI output dir override."""
        args = argparse.Namespace(
            config=None,
            output_dir=Path("/custom/path"),
        )
        
        config = load_configuration(args)
        
        assert config.output_dir == "/custom/path"
    
    def test_loads_configuration_with_cli_format(self):
        """Test loading configuration with CLI format override."""
        args = argparse.Namespace(
            config=None,
            output_dir=None,
            format="markdown",
        )
        
        config = load_configuration(args)
        
        assert config.default_format == "markdown"
    
    @patch("crawler.cli.main.Config.load")
    def test_loads_configuration_from_file(self, mock_load):
        """Test loading configuration from file."""
        mock_load.return_value = Config()
        
        args = argparse.Namespace(
            config=Path("config.yaml"),
            output_dir=None,
        )
        
        config = load_configuration(args)
        
        mock_load.assert_called_once()
        assert isinstance(config, Config)


class TestSetupLoggingFromArgs:
    """Tests for setup_logging_from_args function."""
    
    @patch("crawler.cli.main.setup_logging")
    def test_sets_up_logging_with_default_level(self, mock_setup):
        """Test setting up logging with default level."""
        args = argparse.Namespace(
            verbose=False,
            log_file=None,
        )
        config = Config()
        
        setup_logging_from_args(args, config)
        
        mock_setup.assert_called_once_with(
            level="INFO",
            log_file=None,
            json_format=False,
            console_output=True,
        )
    
    @patch("crawler.cli.main.setup_logging")
    def test_sets_up_logging_with_verbose(self, mock_setup):
        """Test setting up logging with verbose flag."""
        args = argparse.Namespace(
            verbose=True,
            log_file=None,
        )
        config = Config()
        
        setup_logging_from_args(args, config)
        
        mock_setup.assert_called_once_with(
            level="DEBUG",
            log_file=None,
            json_format=False,
            console_output=True,
        )
    
    @patch("crawler.cli.main.setup_logging")
    def test_sets_up_logging_with_log_file(self, mock_setup):
        """Test setting up logging with log file."""
        args = argparse.Namespace(
            verbose=False,
            log_file=Path("test.log"),
        )
        config = Config()
        
        setup_logging_from_args(args, config)
        
        mock_setup.assert_called_once_with(
            level="INFO",
            log_file=Path("test.log"),
            json_format=False,
            console_output=True,
        )


class TestCreateFormatter:
    """Tests for create_formatter function."""
    
    def test_creates_python_formatter(self):
        """Test creating Python formatter."""
        formatter = create_formatter("python")
        
        assert isinstance(formatter, PythonFormatter)
    
    def test_creates_markdown_formatter(self):
        """Test creating Markdown formatter."""
        formatter = create_formatter("markdown")
        
        assert isinstance(formatter, MarkdownFormatter)
    
    def test_creates_json_formatter(self):
        """Test creating JSON formatter."""
        formatter = create_formatter("json")
        
        assert isinstance(formatter, JSONFormatter)
    
    def test_raises_error_for_unsupported_format(self):
        """Test that unsupported format raises error."""
        with pytest.raises(ValueError, match="Unsupported format"):
            create_formatter("unsupported")
    
    def test_format_type_is_case_insensitive(self):
        """Test that format type is case-insensitive."""
        formatter1 = create_formatter("PYTHON")
        formatter2 = create_formatter("Python")
        formatter3 = create_formatter("python")
        
        assert isinstance(formatter1, PythonFormatter)
        assert isinstance(formatter2, PythonFormatter)
        assert isinstance(formatter3, PythonFormatter)


class TestCreateHttpClient:
    """Tests for create_http_client function."""
    
    def test_creates_http_client_with_default_config(self):
        """Test creating HTTP client with default configuration."""
        config = Config()
        logger = Mock()
        
        http_client = create_http_client(config, logger)
        
        assert isinstance(http_client, HTTPClient)
        assert http_client.retry_config.max_retries == 3
        assert http_client.rate_limiter.requests_per_second == 2.0
    
    def test_creates_http_client_with_custom_config(self):
        """Test creating HTTP client with custom configuration."""
        config = Config(
            max_retries=5,
            requests_per_second=5.0,
        )
        logger = Mock()
        
        http_client = create_http_client(config, logger)
        
        assert http_client.retry_config.max_retries == 5
        assert http_client.rate_limiter.requests_per_second == 5.0


class TestExecuteDownloadCommand:
    """Tests for execute_download_command function."""
    
    @patch("crawler.cli.main.create_http_client")
    @patch("crawler.cli.main.PlatformClientFactory")
    @patch("crawler.cli.main.FileSystemRepository")
    @patch("crawler.cli.main.create_formatter")
    def test_executes_download_command_successfully(
        self,
        mock_create_formatter,
        mock_repository_class,
        mock_factory_class,
        mock_create_http_client,
    ):
        """Test executing download command successfully."""
        # Set up mocks
        mock_http_client = Mock()
        mock_create_http_client.return_value = mock_http_client
        
        mock_factory = Mock()
        mock_platform_client = Mock()
        mock_factory.create.return_value = mock_platform_client
        mock_factory_class.return_value = mock_factory
        
        mock_formatter = Mock()
        mock_create_formatter.return_value = mock_formatter
        
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        
        # Create args
        args = argparse.Namespace(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            format="python",
        )
        config = Config()
        logger = Mock()
        
        # Execute command
        with patch("crawler.cli.main.DownloadCommand") as mock_command_class:
            mock_command = Mock()
            mock_result = Mock(success=True, message="Success")
            mock_command.execute.return_value = mock_result
            mock_command_class.return_value = mock_command
            
            exit_code = execute_download_command(args, config, logger)
        
        # Verify
        assert exit_code == 0
        mock_command_class.assert_called_once()
        mock_command.execute.assert_called_once()
    
    @patch("crawler.cli.main.create_http_client")
    @patch("crawler.cli.main.PlatformClientFactory")
    @patch("crawler.cli.main.FileSystemRepository")
    @patch("crawler.cli.main.create_formatter")
    def test_executes_download_command_with_failure(
        self,
        mock_create_formatter,
        mock_repository_class,
        mock_factory_class,
        mock_create_http_client,
    ):
        """Test executing download command with failure."""
        # Set up mocks
        mock_http_client = Mock()
        mock_create_http_client.return_value = mock_http_client
        
        mock_factory = Mock()
        mock_platform_client = Mock()
        mock_factory.create.return_value = mock_platform_client
        mock_factory_class.return_value = mock_factory
        
        mock_formatter = Mock()
        mock_create_formatter.return_value = mock_formatter
        
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        
        # Create args
        args = argparse.Namespace(
            problem_id="two-sum",
            platform="leetcode",
            force=False,
            format="python",
        )
        config = Config()
        logger = Mock()
        
        # Execute command
        with patch("crawler.cli.main.DownloadCommand") as mock_command_class:
            mock_command = Mock()
            mock_result = Mock(success=False, message="Failed")
            mock_command.execute.return_value = mock_result
            mock_command_class.return_value = mock_command
            
            exit_code = execute_download_command(args, config, logger)
        
        # Verify
        assert exit_code == 1


class TestExecuteBatchCommand:
    """Tests for execute_batch_command function."""
    
    @patch("crawler.cli.main.create_http_client")
    @patch("crawler.cli.main.PlatformClientFactory")
    @patch("crawler.cli.main.FileSystemRepository")
    @patch("crawler.cli.main.create_formatter")
    @patch("crawler.cli.main.ConsoleProgressObserver")
    @patch("crawler.cli.main.LoggingObserver")
    def test_executes_batch_command_successfully(
        self,
        mock_logging_observer_class,
        mock_console_observer_class,
        mock_create_formatter,
        mock_repository_class,
        mock_factory_class,
        mock_create_http_client,
    ):
        """Test executing batch command successfully."""
        # Set up mocks
        mock_http_client = Mock()
        mock_create_http_client.return_value = mock_http_client
        
        mock_factory = Mock()
        mock_platform_client = Mock()
        mock_factory.create.return_value = mock_platform_client
        mock_factory_class.return_value = mock_factory
        
        mock_formatter = Mock()
        mock_create_formatter.return_value = mock_formatter
        
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        
        mock_console_observer = Mock()
        mock_console_observer_class.return_value = mock_console_observer
        
        mock_logging_observer = Mock()
        mock_logging_observer_class.return_value = mock_logging_observer
        
        # Create args
        args = argparse.Namespace(
            username="john_doe",
            platform="leetcode",
            mode="skip",
            difficulty=["Easy", "Medium"],
            topics=None,
            include_community=False,
            format="python",
            verbose=False,
        )
        config = Config()
        logger = Mock()
        
        # Execute command
        with patch("crawler.cli.main.BatchDownloadCommand") as mock_command_class:
            mock_command = Mock()
            mock_result = Mock(success=True, message="Success")
            mock_command.execute.return_value = mock_result
            mock_command_class.return_value = mock_command
            
            exit_code = execute_batch_command(args, config, logger)
        
        # Verify
        assert exit_code == 0
        mock_command_class.assert_called_once()
        mock_command.execute.assert_called_once()


class TestExecuteListCommand:
    """Tests for execute_list_command function."""
    
    @patch("crawler.cli.main.FileSystemRepository")
    @patch("crawler.cli.main.create_formatter")
    def test_executes_list_command_successfully(
        self,
        mock_create_formatter,
        mock_repository_class,
    ):
        """Test executing list command successfully."""
        # Set up mocks
        mock_formatter = Mock()
        mock_create_formatter.return_value = mock_formatter
        
        mock_repository = Mock()
        mock_repository_class.return_value = mock_repository
        
        # Create args
        args = argparse.Namespace(
            platform="leetcode",
            difficulty=["Easy"],
            topics=None,
            sort_by="id",
            reverse=False,
        )
        config = Config()
        logger = Mock()
        
        # Execute command
        with patch("crawler.cli.main.ListCommand") as mock_command_class:
            mock_command = Mock()
            mock_result = Mock(success=True, message="Success", data=[])
            mock_command.execute.return_value = mock_result
            mock_command_class.return_value = mock_command
            
            exit_code = execute_list_command(args, config, logger)
        
        # Verify
        assert exit_code == 0
        mock_command_class.assert_called_once()
        mock_command.execute.assert_called_once()


class TestMain:
    """Tests for main function."""
    
    @patch("crawler.cli.main.execute_download_command")
    @patch("crawler.cli.main.setup_logging_from_args")
    @patch("crawler.cli.main.load_configuration")
    def test_main_executes_download_command(
        self,
        mock_load_config,
        mock_setup_logging,
        mock_execute_download,
    ):
        """Test main function executes download command."""
        mock_load_config.return_value = Config()
        mock_execute_download.return_value = 0
        
        exit_code = main(["download", "two-sum", "--platform", "leetcode"])
        
        assert exit_code == 0
        mock_execute_download.assert_called_once()
    
    @patch("crawler.cli.main.execute_batch_command")
    @patch("crawler.cli.main.setup_logging_from_args")
    @patch("crawler.cli.main.load_configuration")
    def test_main_executes_batch_command(
        self,
        mock_load_config,
        mock_setup_logging,
        mock_execute_batch,
    ):
        """Test main function executes batch command."""
        mock_load_config.return_value = Config()
        mock_execute_batch.return_value = 0
        
        exit_code = main([
            "batch", "john_doe",
            "--platform", "leetcode",
            "--mode", "skip"
        ])
        
        assert exit_code == 0
        mock_execute_batch.assert_called_once()
    
    @patch("crawler.cli.main.execute_list_command")
    @patch("crawler.cli.main.setup_logging_from_args")
    @patch("crawler.cli.main.load_configuration")
    def test_main_executes_list_command(
        self,
        mock_load_config,
        mock_setup_logging,
        mock_execute_list,
    ):
        """Test main function executes list command."""
        mock_load_config.return_value = Config()
        mock_execute_list.return_value = 0
        
        exit_code = main(["list"])
        
        assert exit_code == 0
        mock_execute_list.assert_called_once()
    
    @patch("crawler.cli.main.execute_download_command")
    @patch("crawler.cli.main.setup_logging_from_args")
    @patch("crawler.cli.main.load_configuration")
    def test_main_handles_keyboard_interrupt(
        self,
        mock_load_config,
        mock_setup_logging,
        mock_execute_download,
    ):
        """Test main function handles keyboard interrupt."""
        mock_load_config.return_value = Config()
        mock_execute_download.side_effect = KeyboardInterrupt()
        
        exit_code = main(["download", "two-sum", "--platform", "leetcode"])
        
        assert exit_code == 130
    
    @patch("crawler.cli.main.execute_download_command")
    @patch("crawler.cli.main.setup_logging_from_args")
    @patch("crawler.cli.main.load_configuration")
    def test_main_handles_unexpected_exception(
        self,
        mock_load_config,
        mock_setup_logging,
        mock_execute_download,
    ):
        """Test main function handles unexpected exception."""
        mock_load_config.return_value = Config()
        mock_execute_download.side_effect = Exception("Unexpected error")
        
        exit_code = main(["download", "two-sum", "--platform", "leetcode"])
        
        assert exit_code == 1
    
    def test_main_requires_command(self):
        """Test main function requires a command."""
        with pytest.raises(SystemExit):
            main([])
    
    @patch("crawler.cli.main.setup_logging_from_args")
    @patch("crawler.cli.main.load_configuration")
    def test_main_with_verbose_flag(
        self,
        mock_load_config,
        mock_setup_logging,
    ):
        """Test main function with verbose flag."""
        mock_load_config.return_value = Config()
        
        with patch("crawler.cli.main.execute_list_command") as mock_execute:
            mock_execute.return_value = 0
            exit_code = main(["--verbose", "list"])
        
        assert exit_code == 0
        # Verify setup_logging was called
        mock_setup_logging.assert_called_once()
    
    @patch("crawler.cli.main.setup_logging_from_args")
    @patch("crawler.cli.main.load_configuration")
    def test_main_with_config_file(
        self,
        mock_load_config,
        mock_setup_logging,
    ):
        """Test main function with config file."""
        mock_load_config.return_value = Config()
        
        with patch("crawler.cli.main.execute_list_command") as mock_execute:
            mock_execute.return_value = 0
            exit_code = main(["--config", "config.yaml", "list"])
        
        assert exit_code == 0
        # Verify load_configuration was called
        mock_load_config.assert_called_once()
