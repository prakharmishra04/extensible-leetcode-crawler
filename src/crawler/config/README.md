# Logging Configuration

This module provides structured logging for the crawler application with support for both development and production environments.

## Features

- **Structured JSON Logging**: Machine-readable logs for production environments
- **Human-Readable Console Logging**: Colored, formatted logs for development
- **Multiple Handlers**: Support for both console and file output
- **Log Rotation**: Automatic log file rotation to prevent disk space issues
- **Flexible Configuration**: Easy setup for different environments
- **Exception Tracking**: Automatic exception information capture

## Quick Start

### Development Setup

For development, use human-readable console logging:

```python
from crawler.config import configure_default_logging, get_logger

# Configure logging
configure_default_logging()

# Get a logger for your module
logger = get_logger(__name__)

# Use the logger
logger.info("Starting application")
logger.warning("Rate limit approaching")
logger.error("Failed to fetch data")
```

### Production Setup

For production, use JSON-formatted logs with file output:

```python
from pathlib import Path
from crawler.config import configure_production_logging, get_logger

# Configure logging with log directory
log_dir = Path("/var/log/crawler")
configure_production_logging(log_dir)

# Get a logger
logger = get_logger(__name__)

# Log with structured context
logger.info(
    "Processing batch download",
    extra={
        "extra_fields": {
            "username": "john_doe",
            "platform": "leetcode",
            "total_problems": 150
        }
    }
)
```

## Log Levels

The logging system supports five log levels:

- **DEBUG**: Detailed diagnostic information (includes file location)
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

Use the provided constants:

```python
from crawler.config import DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Custom Configuration

For custom logging requirements:

```python
from pathlib import Path
from crawler.config import setup_logging, get_logger, DEBUG

# Custom setup
log_file = Path("logs/custom.log")
setup_logging(
    level=DEBUG,
    log_file=log_file,
    json_format=False,  # Human-readable format
    console_output=True,
)

logger = get_logger(__name__)
logger.debug("Custom logging configured")
```

### Configuration Parameters

- **level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **log_file**: Optional path to log file (enables file logging)
- **json_format**: If True, use JSON formatting; if False, use human-readable format
- **console_output**: If True, output logs to console

## Structured Logging

Add structured context to your logs using the `extra` parameter:

```python
logger.info(
    "Problem fetched successfully",
    extra={
        "extra_fields": {
            "problem_id": "two-sum",
            "platform": "leetcode",
            "difficulty": "Easy",
            "acceptance_rate": 49.2,
            "topics": ["Array", "Hash Table"],
            "duration_ms": 234,
        }
    }
)
```

This produces a JSON log entry:

```json
{
  "timestamp": "2026-01-30T16:00:00.000000+00:00",
  "level": "INFO",
  "logger": "crawler.client",
  "message": "Problem fetched successfully",
  "module": "leetcode_client",
  "function": "fetch_problem",
  "line": 42,
  "problem_id": "two-sum",
  "platform": "leetcode",
  "difficulty": "Easy",
  "acceptance_rate": 49.2,
  "topics": ["Array", "Hash Table"],
  "duration_ms": 234
}
```

## Exception Logging

Automatically capture exception information:

```python
try:
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

This includes the full exception traceback in the log output.

## Log Format Examples

### Console Format (Development)

```
[INFO] - 2026-01-30 21:30:16 - crawler.client - Starting to process problems
[WARNING] - 2026-01-30 21:30:16 - crawler.client - Rate limit approaching
[ERROR] - 2026-01-30 21:30:16 - crawler.client - Failed to fetch problem
[DEBUG] - 2026-01-30 21:30:16 - crawler.client - Detailed info (client.fetch_problem:42)
```

### JSON Format (Production)

```json
{
  "timestamp": "2026-01-30T16:00:16.492045+00:00",
  "level": "INFO",
  "logger": "crawler.client",
  "message": "Starting to process problems",
  "module": "leetcode_client",
  "function": "fetch_problem",
  "line": 42
}
```

## File Logging

When file logging is enabled:

- Logs are written to the specified file path
- Files use JSON format for easy parsing
- Automatic rotation when file reaches 10 MB
- Keeps up to 5 backup files
- Log directory is created automatically if it doesn't exist

## Best Practices

1. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: General progress and status updates
   - WARNING: Unexpected situations that don't prevent operation
   - ERROR: Errors that prevent specific operations
   - CRITICAL: Severe errors that may cause application failure

2. **Add context with structured logging**:
   ```python
   logger.info("Processing problem", extra={
       "extra_fields": {"problem_id": problem.id, "platform": problem.platform}
   })
   ```

3. **Log exceptions with traceback**:
   ```python
   logger.error("Failed to process", exc_info=True)
   ```

4. **Use module-specific loggers**:
   ```python
   logger = get_logger(__name__)
   ```

5. **Don't log sensitive information**:
   - Avoid logging passwords, tokens, or API keys
   - Sanitize user data before logging

## Examples

See `examples/logging_example.py` for complete working examples of:
- Development logging setup
- Production logging setup
- Custom logging configuration
- Exception logging
- Structured logging with context

## Testing

The logging configuration is fully tested. Run tests with:

```bash
pytest tests/unit/config/test_logging_config.py -v
```

## Implementation Details

### JSONFormatter

Formats log records as JSON objects with:
- ISO 8601 timestamp with timezone
- Log level name
- Logger name
- Message
- Module, function, and line number
- Exception information (if present)
- Extra fields (if provided)

### ConsoleFormatter

Formats log records for human readability with:
- ANSI color codes for different log levels
- Timestamp in local timezone
- Logger name and message
- Location information for DEBUG level
- Exception traceback (if present)

### Log Rotation

File logs use `RotatingFileHandler` with:
- Maximum file size: 10 MB
- Backup count: 5 files
- Automatic rotation when size limit is reached
- UTF-8 encoding

## Requirements

- Python 3.8+
- Standard library only (no external dependencies)
