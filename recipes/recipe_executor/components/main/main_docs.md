# Main Component Usage

## Command-Line Interface

The Recipe Executor is used from the command line. You invoke the `main` module with a recipe file and optional parameters. For example:

```bash
# Basic usage:
python -m recipe_executor.main recipes/my_recipe.json

# With a custom log directory:
python -m recipe_executor.main recipes/my_recipe.json --log-dir custom_logs

# With context values:
python -m recipe_executor.main recipes/my_recipe.json --context key1=value1 --context key2=value2
```

## Command-Line Arguments

The Main component supports these command-line arguments:

1. **`recipe_path`** (positional, required): Path to the recipe file to execute.
2. **`--log-dir`** (optional): Directory for log files (default: `"logs"`). If the directory does not exist, it will be created.
3. **`--context`** (optional, repeatable): Context values as `key=value` pairs. You can specify this option multiple times to provide multiple context entries.

## Context Parsing

If you provide context values via `--context`, the Main component will parse them into the execution context. For example:

```bash
# Given the arguments:
--context name=John --context age=30 --context active=true

# The resulting context artifacts will be:
{
    "name": "John",
    "age": "30",
    "active": "true"
}
```

_(All values are parsed as strings. It's up to individual steps to interpret types as needed.)_

## Exit Codes

Main uses exit codes to indicate outcome:

- `0` — Successful execution.
- `1` — An error occurred (e.g., invalid arguments, failure during recipe execution).

These codes can be used in shell scripts to handle success or failure of the recipe execution.

## Error Messages

Error messages and exceptions are written to standard error and also logged:

```python
# Example of an error message for a context format issue:
sys.stderr.write("Context Error: Invalid context format 'foo'\n")

# Example of logging an execution error (in logs and stderr):
logger.error("An error occurred during recipe execution: ...")
```

The stack trace for exceptions is output to stderr (via `traceback.format_exc()`) to aid in debugging issues directly from the console.

## Important Notes

1. The main entry point is designed to be simple and minimal. It delegates the heavy lifting to the `Context` and `Executor` components.
2. All steps in the executed recipe share the same context instance, which is created by Main from the provided context arguments. This context implements the `ContextProtocol` interface (see Protocols documentation), though in usage you typically interact with it via the `Context` class.
3. The Main component itself doesn't enforce any type of step ordering beyond what the recipe dictates; it simply invokes the Executor and waits for it to process the steps sequentially.
4. Environment variables (for example, API keys for LLM steps) can be set in a `.env` file. Main will load this file at startup via `load_dotenv()`, making those values available to components that need them.
5. Logging is configured at runtime when Main calls `init_logger`. The logs (including debug information and errors) are saved in the directory specified by `--log-dir`. Each run may append to these logs, so it's advisable to monitor or clean the log directory if running many recipes.
