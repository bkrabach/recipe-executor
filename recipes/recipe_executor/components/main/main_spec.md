# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, invokes the executor to run the specified recipe, and handles top-level error reporting (exit codes and exceptions).

## Core Requirements

- Provide a command-line interface for executing recipes (accept recipe path and optional parameters).
- Load environment variables from a `.env` file at startup (using python-dotenv).
- Parse context values supplied via command-line arguments (`--context key=value`) into an initial Context state.
- Initialize a logging system and direct log output to a specified directory.
- Create the Context and Executor instances and orchestrate the recipe execution by calling `Executor.execute` with the provided context.
- Handle successful completion by reporting execution time, and handle errors by logging and exiting with a non-zero status.

## Implementation Considerations

- Use Python's built-in `argparse` for argument parsing.
- Support multiple `--context` arguments by accumulating them into a list and parsing into a dictionary of strings.
- Use the `ContextProtocol` interface (via the concrete `Context` implementation) to store context data. The Main component should not depend on the internal details of Context beyond the interface.
- Use the `ExecutorProtocol` interface (via the concrete `Executor` class) to run recipes. This decouples Main from the Executor's implementation except for the known `execute` method contract.
- Prevent import cycles by importing the Executor and Context through the package (ensuring the Protocols component is used for type references, but in implementation Main will instantiate the concrete classes).
- Keep the main logic linear and straightforward: parse inputs, setup context and logger, run executor, handle errors. Avoid additional complexity or long-running logic in Main; delegate to Executor and other components.
- Ensure that any exception raised during execution is caught and results in a clean error message to `stderr` and an appropriate exit code (`1` for failure).
- Maintain minimal state in Main (it should primarily act as a procedural script). Do not retain references to context or executor after execution beyond what’s needed for logging.
- Follow the project philosophy of simplicity: avoid global state, singletons, or complex initialization in the Main component.

## Component Dependencies

### Internal Components

- **Context** - (Required) Creates the Context object (implements the `ContextProtocol` interface) to hold initial artifacts parsed from CLI.
- **Executor** - (Required) Uses the Executor to run the specified recipe (through the `ExecutorProtocol` interface for execution).
- **Protocols** - (Required) References `ContextProtocol` and `ExecutorProtocol` for defining interactions between Main, Context, and Executor in a decoupled manner.
- **Logger** - (Required) Uses the Logger component (via `init_logger`) to initialize logging for the execution.

### External Libraries

- **python-dotenv** - (Required) Loads environment variables from a file at startup.
- **argparse** - (Required) Parses command-line arguments.
- **logging** - (Required) The Python standard logging library is used indirectly via the Logger component and for any ad-hoc logging in Main.
- **sys** and **time** - (Required) Used for exiting with status codes and measuring execution time.
- **typing** - (Optional) Used for type annotations (e.g., `Dict[str, str]` for context parsing).

### Configuration Dependencies

- **Environment File** - The presence of a `.env` file is optional; if present, it's loaded for environment configuration (like API keys for steps, etc., though Main itself mainly cares about logging configuration if any).
- **Logging Directory** - Uses the `--log-dir` argument (default "logs") to determine where log files are written.

## Logging

- Debug: Log the start of execution, the parsed arguments, and the initial context artifact dictionary for traceability.
- Info: Log high-level events such as "Starting Recipe Executor Tool", the recipe being executed, and a success message with execution time.
- Error: On exceptions, log the error message and stack trace (`exc_info=True`) for debugging, and mirror the error to standard error output.

## Error Handling

- Incorrect context argument format (missing `=`) results in a `ValueError` from `parse_context`; Main catches this and outputs a clear error message to `stderr` before exiting with code 1.
- Failures in logger initialization (e.g., invalid log directory permissions) are caught and cause the program to exit with an error message.
- Any exception during Executor execution is caught in Main; it logs the error (including traceback) and ensures the program exits with a non-zero status.
- Main distinguishes between normal execution termination and error termination by exit codes (0 for success, 1 for any failure case).
- After handling an error, Main uses `sys.exit(1)` to terminate the process, as no further steps should be taken.

## Output Files

- `main.py`

## Future Considerations

- Support additional command-line arguments for features like selecting a specific execution model or verbosity level for logging.
- Possibly allow Main to accept recipes in other formats or from other sources (e.g., via URL or stdin) in the future, with minimal changes.
- Integration with a higher-level CLI framework or packaging (for instance, making `recipe-executor` an installable CLI command, which is already partially done via the `pyproject.toml` script entry).
- Additional error codes for different failure modes (though currently all failures are generalized to exit code 1 for simplicity).
