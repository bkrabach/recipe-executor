# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, executes the specified recipe, and handles top-level error reporting.

## Core Requirements

- Provide a command-line interface for executing recipes
- Load environment variables from .env files using python-dotenv
  - python-dotenv is already installed as a dependency of the project
- Parse arguments for recipe path and context values
- Initialize the logging system
- Create the context with command-line supplied values as artifacts
- Execute the specified recipe with proper error handling
- Follow minimal design with clear user-facing error messages

## Implementation Considerations

- Call load_dotenv() early in the main function before any other initialization to make environment variables available in other components as soon as possible
- Use argparse for command-line argument parsing
- Initialize logging early in execution flow
- Parse context values from key=value pairs
- Create a clean context for recipe execution
- Keep the main function focused on orchestration
- Provide meaningful exit codes and error messages

## Implementation Details

- Import Executor using `from executor import Executor` to avoid circular import issues, despite continuing to use the full `recipe_executor.context`, etc. for other imports to maintain consistency with the rest of the codebase

## Logging

- Debug: Log the start of the main function, including parsed arguments and context values
- Info: Log the initialization of the Recipe Executor Tool and the start of recipe execution, upon completion report the success or failure of the execution along with total time taken

## Component Dependencies

### Internal Components

- **Context** - (Required) Creates the Context object with CLI-supplied values
- **Executor** - (Required) Uses Executor to run the specified recipe
- **Logger** - (Required) Uses init_logger to set up the logging system

### External Libraries

- **python-dotenv** - (Required) Uses load_dotenv to load environment variables from .env files
- **argparse** - (Required) Uses argparse for command-line argument parsing

### Configuration Dependencies

- **.env file** - (Optional) For environment variable configuration

## Error Handling

- Validate command-line arguments
- Provide clear error messages for missing or invalid recipe files
- Handle context parsing errors gracefully
- Log all errors before exiting
- Use appropriate exit codes for different error conditions
- Raise SystemExit with appropriate exit codes for different error conditions
- Employ a global try-except block to catch unhandled exceptions and log them
- Neatly format error messages for user-friendliness, considering use of `traceback.format_exc()` and other techniques for making the error reporting easy to identify main error and still provide useful context
- Use a finally block to ensure proper cleanup and logging of execution time

## Output Files

- `main.py`

## Future Considerations

- Support for environment variable configuration
- Support for directory-based recipes
