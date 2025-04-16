# Logger Component Usage

## Importing

```python
from recipe_executor.logger import init_logger
```

## Initialization

The Logger component provides a single function to initialize the logger. This function sets up the logging configuration, including log levels and file handlers.

```python
def init_logger(
    log_dir: str = "logs",
    stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR".
            Note: This is not case-sensitive.
            If set to "DEBUG", all logs will be printed to stdout.
            If set to "INFO", only INFO and higher level logs will be printed to stdout.

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
```

Examples:

```python
# Default usage
logger = init_logger(log_dir="custom/log/path")

# Enable debug logging to stdout
logger = init_logger(log_dir="custom/log/path", stdio_log_level="DEBUG")

# Example usage
logger.info("This is an info message")
```

## Log Levels

The configured logger supports standard Python logging levels:

```python
# Debug level (to debug.log file and higher level logs)
logger.debug("Detailed information for diagnosing problems")

# Info level (to console, info.log, and error.log)
logger.info("Confirmation that things are working as expected")

# Warning level (to console, info.log, and error.log)
logger.warning("An indication that something unexpected happened")

# Error level (to console, info.log, and error.log)
logger.error("Due to a more serious problem, the software could not perform a function")

# Critical level (to all logs)
logger.critical("A serious error indicating the program itself may be unable to continue running")
```

## Log Files

The logger creates three log files:

1. `debug.log` - All messages (DEBUG and above)
2. `info.log` - INFO messages and above
3. `error.log` - ERROR messages and above

Example:

```
2025-03-30 15:42:38.927 [INFO] (main.py:25) Starting Recipe Executor Tool
2025-03-30 15:42:38.928 [DEBUG](executor.py:42) Initializing executor
2025-03-30 15:42:38.930 [INFO] (executor.py:156) Executing recipe: recipes/my_recipe.json
2025-03-30 15:42:38.935 [ERROR] (executor.py:256) Recipe execution failed: Invalid step type
```

## Important Notes

- Logs are cleared (overwritten) on each run
- Debug logs can get large with detailed information
- The log directory is created if it doesn't exist
- The logger is thread-safe and can be used in multi-threaded applications
