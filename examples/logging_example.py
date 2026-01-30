"""
Example demonstrating the structured logging configuration.

This example shows how to use the logging configuration in different scenarios:
1. Development logging (console with human-readable format)
2. Production logging (console + file with JSON format)
3. Custom logging setup
"""

from pathlib import Path
from crawler.config import (
    setup_logging,
    get_logger,
    configure_default_logging,
    configure_production_logging,
    INFO,
    DEBUG,
    WARNING,
    ERROR,
)


def example_development_logging():
    """Example of development logging setup."""
    print("\n=== Development Logging Example ===\n")
    
    # Configure default logging (human-readable console output)
    configure_default_logging()
    
    # Get a logger for your module
    logger = get_logger("crawler.example")
    
    # Log at different levels
    logger.debug("This is a debug message (won't show at INFO level)")
    logger.info("Starting to process problems")
    logger.warning("Rate limit approaching")
    logger.error("Failed to fetch problem")
    
    # Log with extra context
    logger.info(
        "Downloaded problem successfully",
        extra={"extra_fields": {"problem_id": "two-sum", "platform": "leetcode"}}
    )


def example_production_logging():
    """Example of production logging setup."""
    print("\n=== Production Logging Example ===\n")
    
    # Configure production logging (JSON format, console + file)
    log_dir = Path("logs")
    configure_production_logging(log_dir)
    
    # Get a logger for your module
    logger = get_logger("crawler.production")
    
    # Log at different levels
    logger.info("Application started")
    logger.info("Processing batch download", extra={
        "extra_fields": {
            "username": "john_doe",
            "platform": "leetcode",
            "total_problems": 150
        }
    })
    logger.warning("Retry attempt 2/3")
    logger.error("Network timeout", extra={
        "extra_fields": {
            "url": "https://leetcode.com/api/problems",
            "timeout": 30
        }
    })
    
    print(f"\nLogs written to: {log_dir}")


def example_custom_logging():
    """Example of custom logging setup."""
    print("\n=== Custom Logging Example ===\n")
    
    # Custom setup with specific requirements
    log_file = Path("logs/custom.log")
    setup_logging(
        level=DEBUG,
        log_file=log_file,
        json_format=False,  # Human-readable console
        console_output=True,
    )
    
    # Get a logger
    logger = get_logger("crawler.custom")
    
    # Log at different levels
    logger.debug("Detailed debug information")
    logger.info("Custom logging configured")
    logger.warning("This is a warning")
    
    print(f"\nLogs written to: {log_file}")


def example_exception_logging():
    """Example of logging exceptions."""
    print("\n=== Exception Logging Example ===\n")
    
    configure_default_logging()
    logger = get_logger("crawler.exceptions")
    
    try:
        # Simulate an error
        result = 1 / 0
    except ZeroDivisionError:
        logger.error("Division by zero error", exc_info=True)
    
    try:
        # Simulate another error
        data = {"key": "value"}
        value = data["missing_key"]
    except KeyError as e:
        logger.error(f"Key not found: {e}", exc_info=True)


def example_structured_logging():
    """Example of structured logging with context."""
    print("\n=== Structured Logging Example ===\n")
    
    # Use JSON format for structured logs
    setup_logging(level=INFO, json_format=True, console_output=True)
    
    logger = get_logger("crawler.structured")
    
    # Log with structured context
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
    
    logger.info(
        "Batch download completed",
        extra={
            "extra_fields": {
                "username": "john_doe",
                "platform": "leetcode",
                "total": 150,
                "downloaded": 145,
                "skipped": 3,
                "failed": 2,
                "duration_seconds": 342.5,
            }
        }
    )


if __name__ == "__main__":
    print("Structured Logging Examples")
    print("=" * 50)
    
    # Run examples
    example_development_logging()
    example_production_logging()
    example_custom_logging()
    example_exception_logging()
    example_structured_logging()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
