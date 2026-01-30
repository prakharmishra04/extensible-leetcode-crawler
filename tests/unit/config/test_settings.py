"""Unit tests for configuration settings."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from crawler.config.settings import Config


class TestConfigDefaults:
    """Test default configuration values."""
    
    def test_from_defaults_creates_config_with_default_values(self):
        """Test that from_defaults creates a Config with all default values."""
        config = Config.from_defaults()
        
        assert config.leetcode_graphql_url == "https://leetcode.com/graphql"
        assert config.leetcode_session_token is None
        assert config.leetcode_username is None
        assert config.requests_per_second == 2.0
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert config.output_dir == "./problems"
        assert config.default_format == "python"
        assert config.log_level == "INFO"
        assert config.log_file is None
    
    def test_default_constructor_same_as_from_defaults(self):
        """Test that default constructor produces same result as from_defaults."""
        config1 = Config()
        config2 = Config.from_defaults()
        
        assert config1.leetcode_graphql_url == config2.leetcode_graphql_url
        assert config1.requests_per_second == config2.requests_per_second
        assert config1.max_retries == config2.max_retries


class TestConfigFromEnv:
    """Test loading configuration from environment variables."""
    
    def test_from_env_loads_leetcode_credentials(self, monkeypatch):
        """Test loading LeetCode credentials from environment."""
        monkeypatch.setenv("CRAWLER_LEETCODE_SESSION_TOKEN", "test_token_123")
        monkeypatch.setenv("CRAWLER_LEETCODE_USERNAME", "john_doe")
        
        config = Config.from_env()
        
        assert config.leetcode_session_token == "test_token_123"
        assert config.leetcode_username == "john_doe"
    
    def test_from_env_loads_rate_limiting_config(self, monkeypatch):
        """Test loading rate limiting configuration from environment."""
        monkeypatch.setenv("CRAWLER_REQUESTS_PER_SECOND", "5.0")
        
        config = Config.from_env()
        
        assert config.requests_per_second == 5.0
    
    def test_from_env_loads_retry_config(self, monkeypatch):
        """Test loading retry configuration from environment."""
        monkeypatch.setenv("CRAWLER_MAX_RETRIES", "5")
        monkeypatch.setenv("CRAWLER_INITIAL_DELAY", "2.0")
        monkeypatch.setenv("CRAWLER_MAX_DELAY", "120.0")
        monkeypatch.setenv("CRAWLER_EXPONENTIAL_BASE", "3.0")
        monkeypatch.setenv("CRAWLER_JITTER", "false")
        
        config = Config.from_env()
        
        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False
    
    def test_from_env_loads_output_config(self, monkeypatch):
        """Test loading output configuration from environment."""
        monkeypatch.setenv("CRAWLER_OUTPUT_DIR", "/tmp/problems")
        monkeypatch.setenv("CRAWLER_DEFAULT_FORMAT", "markdown")
        
        config = Config.from_env()
        
        assert config.output_dir == "/tmp/problems"
        assert config.default_format == "markdown"
    
    def test_from_env_loads_logging_config(self, monkeypatch):
        """Test loading logging configuration from environment."""
        monkeypatch.setenv("CRAWLER_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("CRAWLER_LOG_FILE", "/var/log/crawler.log")
        
        config = Config.from_env()
        
        assert config.log_level == "DEBUG"
        assert config.log_file == "/var/log/crawler.log"
    
    def test_from_env_loads_future_platform_credentials(self, monkeypatch):
        """Test loading future platform credentials from environment."""
        monkeypatch.setenv("CRAWLER_HACKERRANK_API_KEY", "hr_key_123")
        monkeypatch.setenv("CRAWLER_CODECHEF_USERNAME", "chef_user")
        monkeypatch.setenv("CRAWLER_CODECHEF_PASSWORD", "chef_pass")
        monkeypatch.setenv("CRAWLER_CODEFORCES_API_KEY", "cf_key")
        monkeypatch.setenv("CRAWLER_CODEFORCES_API_SECRET", "cf_secret")
        
        config = Config.from_env()
        
        assert config.hackerrank_api_key == "hr_key_123"
        assert config.codechef_username == "chef_user"
        assert config.codechef_password == "chef_pass"
        assert config.codeforces_api_key == "cf_key"
        assert config.codeforces_api_secret == "cf_secret"
    
    def test_from_env_with_base_config_overrides_only_set_values(self, monkeypatch):
        """Test that from_env only overrides values that are set in environment."""
        base_config = Config(leetcode_username="base_user", max_retries=10)
        monkeypatch.setenv("CRAWLER_LEETCODE_USERNAME", "env_user")
        
        config = Config.from_env(base_config=base_config)
        
        assert config.leetcode_username == "env_user"
        assert config.max_retries == 10  # Not overridden
    
    def test_from_env_jitter_boolean_parsing(self, monkeypatch):
        """Test that jitter boolean is parsed correctly from various formats."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
        ]
        
        for env_value, expected in test_cases:
            monkeypatch.setenv("CRAWLER_JITTER", env_value)
            config = Config.from_env()
            assert config.jitter == expected, f"Failed for env_value={env_value}"


class TestConfigFromFile:
    """Test loading configuration from files."""
    
    def test_from_file_loads_json_config(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "leetcode_session_token": "json_token",
            "leetcode_username": "json_user",
            "requests_per_second": 3.0,
            "max_retries": 5,
            "output_dir": "/tmp/json_problems",
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            config = Config.from_file(config_file)
            
            assert config.leetcode_session_token == "json_token"
            assert config.leetcode_username == "json_user"
            assert config.requests_per_second == 3.0
            assert config.max_retries == 5
            assert config.output_dir == "/tmp/json_problems"
        finally:
            config_file.unlink()
    
    def test_from_file_loads_yaml_config(self):
        """Test loading configuration from YAML file."""
        pytest.importorskip("yaml")  # Skip if PyYAML not installed
        
        config_yaml = """
leetcode_session_token: yaml_token
leetcode_username: yaml_user
requests_per_second: 4.0
max_retries: 7
output_dir: /tmp/yaml_problems
"""
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_yaml)
            config_file = Path(f.name)
        
        try:
            config = Config.from_file(config_file)
            
            assert config.leetcode_session_token == "yaml_token"
            assert config.leetcode_username == "yaml_user"
            assert config.requests_per_second == 4.0
            assert config.max_retries == 7
            assert config.output_dir == "/tmp/yaml_problems"
        finally:
            config_file.unlink()
    
    def test_from_file_raises_error_for_nonexistent_file(self):
        """Test that from_file raises FileNotFoundError for nonexistent file."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            Config.from_file(Path("/nonexistent/config.json"))
    
    def test_from_file_raises_error_for_unsupported_format(self):
        """Test that from_file raises ValueError for unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            config_file = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Unsupported config file format"):
                Config.from_file(config_file)
        finally:
            config_file.unlink()
    
    def test_from_file_raises_error_for_invalid_json(self):
        """Test that from_file raises error for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json {")
            config_file = Path(f.name)
        
        try:
            with pytest.raises(json.JSONDecodeError):
                Config.from_file(config_file)
        finally:
            config_file.unlink()
    
    def test_from_file_raises_error_for_non_dict_content(self):
        """Test that from_file raises ValueError if file doesn't contain a dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(["not", "a", "dict"], f)
            config_file = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="must contain a dictionary"):
                Config.from_file(config_file)
        finally:
            config_file.unlink()
    
    def test_from_file_with_base_config_merges_values(self):
        """Test that from_file merges with base config."""
        base_config = Config(leetcode_username="base_user", max_retries=10)
        config_data = {"leetcode_username": "file_user"}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            config = Config.from_file(config_file, base_config=base_config)
            
            assert config.leetcode_username == "file_user"
            assert config.max_retries == 10  # From base config
        finally:
            config_file.unlink()


class TestConfigFromCliArgs:
    """Test loading configuration from CLI arguments."""
    
    def test_from_cli_args_overrides_values(self):
        """Test that from_cli_args overrides values from base config."""
        base_config = Config(leetcode_username="base_user", max_retries=3)
        cli_args = {
            "leetcode_username": "cli_user",
            "max_retries": 5,
        }
        
        config = Config.from_cli_args(cli_args, base_config=base_config)
        
        assert config.leetcode_username == "cli_user"
        assert config.max_retries == 5
    
    def test_from_cli_args_preserves_unspecified_values(self):
        """Test that from_cli_args preserves values not in CLI args."""
        base_config = Config(leetcode_username="base_user", max_retries=10)
        cli_args = {"leetcode_username": "cli_user"}
        
        config = Config.from_cli_args(cli_args, base_config=base_config)
        
        assert config.leetcode_username == "cli_user"
        assert config.max_retries == 10  # Preserved from base
    
    def test_from_cli_args_with_all_parameters(self):
        """Test from_cli_args with all possible parameters."""
        cli_args = {
            "leetcode_session_token": "cli_token",
            "leetcode_username": "cli_user",
            "requests_per_second": 10.0,
            "max_retries": 7,
            "initial_delay": 0.5,
            "max_delay": 30.0,
            "exponential_base": 1.5,
            "jitter": False,
            "output_dir": "/cli/output",
            "default_format": "json",
            "log_level": "DEBUG",
            "log_file": "/cli/log.txt",
        }
        
        config = Config.from_cli_args(cli_args)
        
        assert config.leetcode_session_token == "cli_token"
        assert config.leetcode_username == "cli_user"
        assert config.requests_per_second == 10.0
        assert config.max_retries == 7
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.exponential_base == 1.5
        assert config.jitter is False
        assert config.output_dir == "/cli/output"
        assert config.default_format == "json"
        assert config.log_level == "DEBUG"
        assert config.log_file == "/cli/log.txt"


class TestConfigLoad:
    """Test the load method with proper precedence."""
    
    def test_load_with_defaults_only(self):
        """Test load with no config file or CLI args."""
        config = Config.load()
        
        assert config.leetcode_graphql_url == "https://leetcode.com/graphql"
        assert config.max_retries == 3
    
    def test_load_with_config_file_only(self):
        """Test load with config file but no CLI args."""
        config_data = {"leetcode_username": "file_user", "max_retries": 5}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            config = Config.load(config_file=config_file)
            
            assert config.leetcode_username == "file_user"
            assert config.max_retries == 5
        finally:
            config_file.unlink()
    
    def test_load_with_env_overrides_file(self, monkeypatch):
        """Test that environment variables override config file."""
        config_data = {"leetcode_username": "file_user", "max_retries": 5}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            monkeypatch.setenv("CRAWLER_LEETCODE_USERNAME", "env_user")
            config = Config.load(config_file=config_file)
            
            assert config.leetcode_username == "env_user"  # From env
            assert config.max_retries == 5  # From file
        finally:
            config_file.unlink()
    
    def test_load_with_cli_overrides_env_and_file(self, monkeypatch):
        """Test that CLI args override both env and file."""
        config_data = {"leetcode_username": "file_user", "max_retries": 5}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            monkeypatch.setenv("CRAWLER_LEETCODE_USERNAME", "env_user")
            monkeypatch.setenv("CRAWLER_MAX_RETRIES", "7")
            
            cli_args = {"leetcode_username": "cli_user"}
            config = Config.load(config_file=config_file, cli_args=cli_args)
            
            assert config.leetcode_username == "cli_user"  # From CLI (highest)
            assert config.max_retries == 7  # From env (overrides file)
        finally:
            config_file.unlink()
    
    def test_load_precedence_order(self, monkeypatch):
        """Test complete precedence: CLI > ENV > File > Defaults."""
        # Create config file
        config_data = {
            "leetcode_username": "file_user",
            "max_retries": 5,
            "output_dir": "/file/output",
            "log_level": "WARNING",
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            # Set environment variables
            monkeypatch.setenv("CRAWLER_LEETCODE_USERNAME", "env_user")
            monkeypatch.setenv("CRAWLER_MAX_RETRIES", "7")
            monkeypatch.setenv("CRAWLER_OUTPUT_DIR", "/env/output")
            
            # Provide CLI args
            cli_args = {
                "leetcode_username": "cli_user",
                "max_retries": 10,
            }
            
            config = Config.load(config_file=config_file, cli_args=cli_args)
            
            # CLI overrides everything
            assert config.leetcode_username == "cli_user"
            assert config.max_retries == 10
            
            # ENV overrides file
            assert config.output_dir == "/env/output"
            
            # File overrides defaults
            assert config.log_level == "WARNING"
            
            # Defaults used when nothing else specified
            assert config.default_format == "python"
        finally:
            config_file.unlink()
    
    def test_load_with_nonexistent_config_file_uses_defaults(self):
        """Test that load handles nonexistent config file gracefully."""
        config = Config.load(config_file=Path("/nonexistent/config.json"))
        
        # Should use defaults since file doesn't exist
        assert config.max_retries == 3


class TestGetPlatformCredentials:
    """Test getting platform-specific credentials."""
    
    def test_get_leetcode_credentials(self):
        """Test getting LeetCode credentials."""
        config = Config(
            leetcode_session_token="lc_token",
            leetcode_username="lc_user"
        )
        
        creds = config.get_platform_credentials("leetcode")
        
        assert creds == {
            "session_token": "lc_token",
            "username": "lc_user",
        }
    
    def test_get_hackerrank_credentials(self):
        """Test getting HackerRank credentials."""
        config = Config(hackerrank_api_key="hr_key")
        
        creds = config.get_platform_credentials("hackerrank")
        
        assert creds == {"api_key": "hr_key"}
    
    def test_get_codechef_credentials(self):
        """Test getting CodeChef credentials."""
        config = Config(
            codechef_username="chef_user",
            codechef_password="chef_pass"
        )
        
        creds = config.get_platform_credentials("codechef")
        
        assert creds == {
            "username": "chef_user",
            "password": "chef_pass",
        }
    
    def test_get_codeforces_credentials(self):
        """Test getting Codeforces credentials."""
        config = Config(
            codeforces_api_key="cf_key",
            codeforces_api_secret="cf_secret"
        )
        
        creds = config.get_platform_credentials("codeforces")
        
        assert creds == {
            "api_key": "cf_key",
            "api_secret": "cf_secret",
        }
    
    def test_get_platform_credentials_case_insensitive(self):
        """Test that platform name is case-insensitive."""
        config = Config(leetcode_username="user")
        
        creds1 = config.get_platform_credentials("leetcode")
        creds2 = config.get_platform_credentials("LeetCode")
        creds3 = config.get_platform_credentials("LEETCODE")
        
        assert creds1 == creds2 == creds3
    
    def test_get_platform_credentials_raises_for_unsupported_platform(self):
        """Test that get_platform_credentials raises ValueError for unknown platform."""
        config = Config()
        
        with pytest.raises(ValueError, match="Unsupported platform: unknown"):
            config.get_platform_credentials("unknown")


class TestConfigToDict:
    """Test converting configuration to dictionary."""
    
    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all configuration fields."""
        config = Config(
            leetcode_session_token="token",
            leetcode_username="user",
            max_retries=5,
        )
        
        config_dict = config.to_dict()
        
        assert "leetcode_session_token" in config_dict
        assert "leetcode_username" in config_dict
        assert "max_retries" in config_dict
        assert "requests_per_second" in config_dict
        assert "output_dir" in config_dict
        assert "log_level" in config_dict
    
    def test_to_dict_values_match_config(self):
        """Test that to_dict values match the config object."""
        config = Config(
            leetcode_username="test_user",
            max_retries=7,
            output_dir="/test/output",
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["leetcode_username"] == "test_user"
        assert config_dict["max_retries"] == 7
        assert config_dict["output_dir"] == "/test/output"
