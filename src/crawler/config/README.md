# Configuration Management

This module provides comprehensive configuration management for the crawler application with support for multiple configuration sources and clear precedence rules.

## Features

- **Multiple Configuration Sources**: Environment variables, YAML/JSON files, CLI arguments, and defaults
- **Clear Precedence Order**: CLI > ENV > Config File > Defaults
- **Platform-Specific Credentials**: Extensible credential management for multiple platforms
- **Type Safety**: Full type hints and validation
- **Easy to Use**: Simple API with sensible defaults

## Quick Start

### Using Defaults

The simplest way to get started is with default configuration:

```python
from crawler.config import Config

# Use all defaults
config = Config()

# Or explicitly
config = Config.from_defaults()
```

### Loading from Environment Variables

Set environment variables with the `CRAWLER_` prefix:

```bash
export CRAWLER_LEETCODE_SESSION_TOKEN="your_token_here"
export CRAWLER_LEETCODE_USERNAME="your_username"
export CRAWLER_MAX_RETRIES="5"
export CRAWLER_LOG_LEVEL="DEBUG"
```

Then load in your code:

```python
from crawler.config import Config

config = Config.from_env()
```

### Loading from Configuration File

Create a `config.yaml` or `config.json` file:

```yaml
# config.yaml
leetcode_session_token: "your_token_here"
leetcode_username: "your_username"
max_retries: 5
log_level: "DEBUG"
```

Load it in your code:

```python
from pathlib import Path
from crawler.config import Config

config = Config.from_file(Path("config.yaml"))
```

### Loading with Proper Precedence

The recommended way to load configuration is using the `load()` method, which automatically applies the correct precedence order:

```python
from pathlib import Path
from crawler.config import Config

# Load with all sources
config = Config.load(
    config_file=Path("config.yaml"), cli_args={"leetcode_username": "cli_user"}
)
```

This applies the precedence: **CLI > ENV > Config File > Defaults**

## Configuration Sources

### 1. Defaults

Default values are defined in the `Config` class:

```python
config = Config.from_defaults()

# Default values:
# - leetcode_graphql_url: "https://leetcode.com/graphql"
# - requests_per_second: 2.0
# - max_retries: 3
# - initial_delay: 1.0
# - max_delay: 60.0
# - exponential_base: 2.0
# - jitter: True
# - output_dir: "./problems"
# - default_format: "python"
# - log_level: "INFO"
```

### 2. Configuration Files

Supported formats: YAML (`.yaml`, `.yml`) and JSON (`.json`)

**YAML Example** (`config.yaml`):

```yaml
leetcode_session_token: "your_token"
leetcode_username: "your_username"
requests_per_second: 3.0
max_retries: 5
output_dir: "/path/to/problems"
default_format: "markdown"
log_level: "DEBUG"
```

**JSON Example** (`config.json`):

```json
{
  "leetcode_session_token": "your_token",
  "leetcode_username": "your_username",
  "requests_per_second": 3.0,
  "max_retries": 5,
  "output_dir": "/path/to/problems",
  "default_format": "markdown",
  "log_level": "DEBUG"
}
```

Load with:

```python
config = Config.from_file(Path("config.yaml"))
```

**Note**: YAML support requires PyYAML: `pip install pyyaml`

### 3. Environment Variables

All environment variables must be prefixed with `CRAWLER_` and use uppercase:

```bash
# LeetCode credentials
export CRAWLER_LEETCODE_SESSION_TOKEN="your_token"
export CRAWLER_LEETCODE_USERNAME="your_username"

# Rate limiting
export CRAWLER_REQUESTS_PER_SECOND="3.0"

# Retry configuration
export CRAWLER_MAX_RETRIES="5"
export CRAWLER_INITIAL_DELAY="2.0"
export CRAWLER_MAX_DELAY="120.0"
export CRAWLER_EXPONENTIAL_BASE="3.0"
export CRAWLER_JITTER="true"

# Output configuration
export CRAWLER_OUTPUT_DIR="/path/to/problems"
export CRAWLER_DEFAULT_FORMAT="markdown"

# Logging configuration
export CRAWLER_LOG_LEVEL="DEBUG"
export CRAWLER_LOG_FILE="/var/log/crawler.log"
```

Load with:

```python
config = Config.from_env()
```

### 4. CLI Arguments

Pass configuration as a dictionary:

```python
cli_args = {
    "leetcode_username": "cli_user",
    "max_retries": 10,
    "log_level": "DEBUG",
}

config = Config.from_cli_args(cli_args)
```

## Configuration Precedence

When using `Config.load()`, the precedence order is:

1. **CLI Arguments** (highest priority)
1. **Environment Variables**
1. **Configuration File**
1. **Defaults** (lowest priority)

Example demonstrating precedence:

```python
# config.yaml
leetcode_username: "file_user"
max_retries: 5

# Environment
export CRAWLER_LEETCODE_USERNAME="env_user"
export CRAWLER_MAX_RETRIES="7"

# CLI
cli_args = {"leetcode_username": "cli_user"}

# Load
config = Config.load(
    config_file=Path("config.yaml"),
    cli_args=cli_args
)

# Results:
# - leetcode_username: "cli_user" (from CLI, highest priority)
# - max_retries: 7 (from ENV, overrides file)
```

## Available Configuration Options

### LeetCode Configuration

| Option                   | Type | Default                          | Description                      |
| ------------------------ | ---- | -------------------------------- | -------------------------------- |
| `leetcode_graphql_url`   | str  | `"https://leetcode.com/graphql"` | LeetCode GraphQL API endpoint    |
| `leetcode_session_token` | str  | `None`                           | Session token for authentication |
| `leetcode_username`      | str  | `None`                           | LeetCode username                |

### Future Platform Credentials

These are placeholders for Phase 3 multi-platform support:

| Option                  | Type | Default | Description           |
| ----------------------- | ---- | ------- | --------------------- |
| `hackerrank_api_key`    | str  | `None`  | HackerRank API key    |
| `codechef_username`     | str  | `None`  | CodeChef username     |
| `codechef_password`     | str  | `None`  | CodeChef password     |
| `codeforces_api_key`    | str  | `None`  | Codeforces API key    |
| `codeforces_api_secret` | str  | `None`  | Codeforces API secret |

### Rate Limiting Configuration

| Option                | Type  | Default | Description                 |
| --------------------- | ----- | ------- | --------------------------- |
| `requests_per_second` | float | `2.0`   | Maximum requests per second |

### Retry Configuration

| Option             | Type  | Default | Description                  |
| ------------------ | ----- | ------- | ---------------------------- |
| `max_retries`      | int   | `3`     | Maximum retry attempts       |
| `initial_delay`    | float | `1.0`   | Initial delay in seconds     |
| `max_delay`        | float | `60.0`  | Maximum delay in seconds     |
| `exponential_base` | float | `2.0`   | Base for exponential backoff |
| `jitter`           | bool  | `True`  | Add random jitter to delays  |

### Output Configuration

| Option           | Type | Default        | Description                                    |
| ---------------- | ---- | -------------- | ---------------------------------------------- |
| `output_dir`     | str  | `"./problems"` | Base directory for problems                    |
| `default_format` | str  | `"python"`     | Default output format (python, markdown, json) |

### Logging Configuration

| Option      | Type | Default  | Description                                           |
| ----------- | ---- | -------- | ----------------------------------------------------- |
| `log_level` | str  | `"INFO"` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `log_file`  | str  | `None`   | Optional log file path                                |

## Platform-Specific Credentials

Get credentials for a specific platform:

```python
config = Config(leetcode_session_token="lc_token", leetcode_username="lc_user")

# Get LeetCode credentials
creds = config.get_platform_credentials("leetcode")
# Returns: {"session_token": "lc_token", "username": "lc_user"}

# Get HackerRank credentials
creds = config.get_platform_credentials("hackerrank")
# Returns: {"api_key": None}
```

Supported platforms:

- `leetcode`: Returns `session_token` and `username`
- `hackerrank`: Returns `api_key`
- `codechef`: Returns `username` and `password`
- `codeforces`: Returns `api_key` and `api_secret`

## Converting to Dictionary

Convert configuration to a dictionary:

```python
config = Config(leetcode_username="user", max_retries=5)
config_dict = config.to_dict()

# Returns all configuration as a dictionary
```

## Example Usage Patterns

### Development Setup

```python
from crawler.config import Config

# Use defaults for development
config = Config()
```

### Production Setup with Config File

```python
from pathlib import Path
from crawler.config import Config

# Load from production config file
config = Config.load(config_file=Path("/etc/crawler/config.yaml"))
```

### CI/CD Setup with Environment Variables

```bash
# Set in CI/CD environment
export CRAWLER_LEETCODE_SESSION_TOKEN="${SECRET_TOKEN}"
export CRAWLER_LOG_LEVEL="INFO"
```

```python
from crawler.config import Config

# Load from environment (no file needed)
config = Config.from_env()
```

### CLI Application

```python
import argparse
from pathlib import Path
from crawler.config import Config

# Parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("--config", type=Path)
parser.add_argument("--username")
parser.add_argument("--max-retries", type=int)
args = parser.parse_args()

# Convert to dict
cli_args = {
    "leetcode_username": args.username,
    "max_retries": args.max_retries,
}

# Load with precedence
config = Config.load(
    config_file=args.config,
    cli_args={k: v for k, v in cli_args.items() if v is not None},
)
```

## Example Configuration Files

See the example configuration files in the repository:

- `config.example.yaml` - YAML format example
- `config.example.json` - JSON format example

Copy one of these files and customize it for your needs:

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your credentials
```

## Best Practices

1. **Use Config Files for Persistent Settings**: Store non-sensitive configuration in YAML/JSON files
1. **Use Environment Variables for Secrets**: Store sensitive credentials (tokens, passwords) in environment variables
1. **Use CLI Arguments for Overrides**: Override specific settings at runtime without changing files
1. **Don't Commit Secrets**: Add `config.yaml` and `config.json` to `.gitignore`
1. **Provide Example Files**: Include `config.example.yaml` in version control
1. **Document Required Settings**: Clearly document which settings are required for your use case

## Security Considerations

- **Never commit credentials** to version control
- **Use environment variables** for sensitive data in production
- **Restrict file permissions** on configuration files containing secrets
- **Rotate credentials regularly**
- **Use separate configs** for development, staging, and production

## Testing

The configuration system is fully tested. Run tests with:

```bash
pytest tests/unit/config/test_settings.py -v
```

## Requirements

- Python 3.8+
- PyYAML (optional, for YAML support): `pip install pyyaml`
