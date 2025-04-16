# Executor Component Specification

## Purpose

The Executor component is responsible for executing recipes defined in JSON format. It loads the recipe, validates its structure, and sequentially executes each step using a shared context object. The Executor is designed to be stateless, meaning it does not maintain any internal state between executions. It also handles logging and error propagation to ensure that any issues encountered during execution are reported clearly.

## Core Requirements

- Accept recipe definitions in multiple formats:
  - File path to a JSON recipe file on disk.
  - Raw JSON string containing the recipe.
  - A Python dictionary already representing the recipe.
- Parse or load the recipe into the `Recipe` type.
- Validate the recipe structure.
- Iterate through the list of steps and execute them sequentially:
  - For each step, retrieve the step class from the Step Registry using the step's `"type"`.
  - Instantiate the step with its configuration.
  - Call the step's `execute(context)` method, passing in the shared context object.
- Handle errors gracefully:
  - If a step raises an exception, stop execution and wrap the exception in a clear message indicating which step failed.
  - Propagate errors up to the caller (Main or a supervising component) with context so that it can be logged or handled.
- Remain stateless aside from the execution flow; the Executor should not hold state between runs (each call to `execute` is independent).

## Implementation Considerations

- **Recipe Loading**:
  - If the recipe is a string, check if it is a file path (using `os.path.isfile()`). If so, read the file content and parse it as JSON. If not, treat it as a raw JSON string.
  - If the recipe is a dictionary, use it directly.
  - Use `json.loads()` to parse JSON strings into Python dictionaries.
  - If the recipe is a file path, use `json.load()` to read and parse the file content.
- **Format Validation**: Use `Recipe.model_validate(value)` or `Recipe.model_validate_json(value)` to validate the loaded recipe against the `Recipe` model. This ensures that the recipe adheres to the expected structure and types.
- **Step Execution**: Retrieve step implementations via `STEP_REGISTRY` (a global registry mapping step type names to their classes).
- **Context Interface**: Use the `ContextProtocol` interface for the `context` parameter to prevent coupling to a specific context implementation.
- **Protocols Compliance**: Document that Executor implements the `ExecutorProtocol`. The async `execute` method signature should match exactly what `ExecutorProtocol` defines.
- **Sequential Execution**: Execute each defined step in the order they appear in the recipe. The context object is passed to each step's `execute` method, allowing steps to read from and write to the context.
- **Error Propagation**: Wrap exceptions from steps in a `ValueError` with a message indicating the step index and type that failed, then raise it.

## Component Dependencies

### Internal Components

- **Protocols**: Uses the `ContextProtocol` definition for interacting with the context, and in concept provides the implementation for the `ExecutorProtocol`.
- **Models**: Uses the `Recipe` and `RecipeStep` models to represent the loaded recipe.
- **Step Registry**: Uses `STEP_REGISTRY` to look up and instantiate step classes by their type names.
  - _Note_: The dependency on specific step classes is indirect via the registry, preventing the Executor from needing to import each step module.
- **Logger**: The Executor will use the logger passed in by the caller

### External Libraries

- **json** - (Required) Used to parse JSON strings and files into Python dictionaries.
- **os** - (Required) Used to check file path existence and determine if a string is a file path.
- **logging** - (Required) Uses Python's logging library to report on execution progress and issues.
- **typing** - (Required) Utilizes typing for type hints (e.g., `Union[str, Dict]` for recipe input, and `ContextProtocol` for context type).

### Configuration Dependencies

- None

## Logging

- Debug:
  - Log when a recipe is loaded (including whether it came from a dict, file, or JSON string).
  - Log the entire recipe content (or a summary) and the number of steps at the start of execution.
  - Log before executing each step (index and type, plus step details for traceability).
  - Log after a step executes successfully.
  - Log a message when all steps complete.
- Info:
  - The Executor itself does not log at info level by default. (High-level info logging, like start and end of execution, is usually handled by Main or the logger setup.)
- Warning/Error:
  - If a step type is not found in the registry, log or include a message about the unknown step type (this triggers a ValueError as well).
  - No direct error logging inside Executor (it raises exceptions up, and the caller (Main) will log the error).

## Error Handling

- **Unsupported Recipe Type**: If the `recipe` argument is neither `dict` nor `str`, a `TypeError` is raised immediately.
- **File Read Errors**: If a file path is provided but reading or JSON parsing fails, a `ValueError` is raised with details (e.g., file not found or JSON decode error).
- **Invalid Recipe Structure**: If after loading, the structure isn't a dict or missing a proper steps list, a `ValueError` is raised explaining the expectation.
- **Unknown Step Type**: If a step's `"type"` is not in `STEP_REGISTRY`, raise `ValueError` indicating an unknown step type at that index.
- **Step Execution Error**: If `step_instance.execute(context)` raises an Exception, catch it. Raise a new `ValueError` that wraps the original exception, with a message specifying which step index and type failed.
- Stop execution upon the first error encountered (fail-fast behavior).

## Output Files

- `executor.py`
