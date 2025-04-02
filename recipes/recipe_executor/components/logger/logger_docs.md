# Logger Component Usage

## Importing

```python
from recipe_executor.logger import init_logger
```

## Initialization

The Logger component provides a single function to initialize a configured logger:

```python
def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
```

Examples:

```python
# Default usage
logger = init_logger()

# With custom log directory
logger = init_logger(log_dir="custom/log/path")
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
2025-03-30 15:42:38,927 [INFO] Starting Recipe Executor Tool
2025-03-30 15:42:38,928 [DEBUG] Initializing executor
2025-03-30 15:42:38,930 [INFO] Executing recipe: recipes/my_recipe.json
2025-03-30 15:42:38,935 [ERROR] Recipe execution failed: Invalid step type
```

## Console Output

The logger also writes INFO level and above messages to stdout:

```python
# This appears in both console and log files
logger.info("Executing step 1 of 5")

# This appears in log files only
logger.debug("Step config: {'path': 'input.txt', 'artifact': 'content'}")
```

## Integration with Other Components

The logger is typically initialized in the main component and passed to the executor:

```python
from recipe_executor.logger import init_logger
from recipe_executor.executor import Executor

logger = init_logger(log_dir="logs")
executor = Executor()
executor.execute(recipe_path, context, logger=logger)
```

Steps receive the logger in their constructor:

```python
class ReadFileStep(BaseStep):
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("RecipeExecutor")
        # ...
```

## Important Notes

1. Logs are cleared (truncated) on each run
2. Debug logs can get large with detailed information
3. The log directory is created if it doesn't exist
4. The logger name "RecipeExecutor" is consistent across the system
