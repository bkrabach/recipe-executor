# Executor Component Specification

## Purpose

The Executor component is the central orchestration mechanism of the Recipe Executor system. It is responsible for loading a recipe (which may be provided as a file path, JSON string, or pre-parsed dictionary) and executing the recipe's steps in order, using a shared context for state. The Executor acts as the runtime engine that ties together the dynamic step execution with the static recipe definition.

## Core Requirements

- Accept recipe definitions in multiple formats:
  - File path to a JSON recipe file on disk.
  - Raw JSON string containing the recipe.
  - A Python dictionary already representing the recipe.
- Parse or load the recipe into a standard dictionary form (with a top-level `"steps"` list).
- Validate the recipe structure:
  - It should contain a `"steps"` key mapping to a list.
  - Each step entry in the list should be a dictionary with at least a `"type"` field.
  - The `"type"` of each step must correspond to a registered step in the system.
- Iterate through the list of steps and execute them sequentially:
  - For each step, retrieve the step class from the Step Registry using the step's `"type"`.
  - Instantiate the step with its configuration (the step dictionary itself, or part of it).
  - Call the step's `execute(context)` method, passing in the shared context object.
- Manage logging throughout the process:
  - Initialize a default logger if none is provided.
  - Log key events (loading recipe, starting/finishing each step, errors).
- Handle errors gracefully:
  - If a step raises an exception, stop execution and wrap the exception in a clear message indicating which step failed.
  - Propagate errors up to the caller (Main or a supervising component) with context so that it can be logged or handled.
- Remain stateless aside from the execution flow; the Executor should not hold state between runs (each call to `execute` is independent).

## Implementation Considerations

- **Recipe Loading**: Use Python's file I/O and `json` library to load recipe files. If the input is a string, first check if it points to a valid file path; if yes, attempt to open and parse it. If not a file, attempt to interpret it as a JSON string.
- **Format Validation**: After loading, ensure the result is a dictionary. If not, raise a `ValueError` indicating the recipe format is invalid.
- **Step List Validation**: Confirm that the `"steps"` key exists and is a list. If not, raise a `ValueError` (with a message that `"steps"` list is required).
- **Step Execution**: Retrieve step implementations via `STEP_REGISTRY` (a global registry mapping step type names to their classes). This registry is populated by the Steps subsystem at import time. Using the registry avoids import dependencies on individual step modules inside Executor.
- **Context Interface**: Use the `ContextProtocol` interface for the `context` parameter. The Executor should not depend on the concrete `Context` class methods beyond what the protocol guarantees (e.g., being able to get and set values). This allows future flexibility (e.g., a different context implementation) and breaks direct coupling.
- **Protocols Compliance**: Document that Executor implements the `ExecutorProtocol`. The `execute` method signature should match exactly what `ExecutorProtocol` defines.
- **Logging**: If a `logger` is provided to `execute()`, use it. Otherwise, create a logger specific to the Executor (`__name__` logger). Ensure that if the logger has no handlers (likely the case if not configured globally), attach a default `StreamHandler` so that messages are visible. Set an appropriate log level (e.g., INFO) for detailed execution traces.
- **Sequential Execution**: Execute steps in a `for` loop. The context object is mutated by each step; steps later in the list see the effects of earlier steps.
- **Error Propagation**: Wrap exceptions from steps in a `ValueError` with a message indicating the step index and type that failed, then raise it. This makes it easier for the Main component (or any caller) to identify where the failure occurred. Use `from e` to preserve the original traceback for debugging.
- **No Post-Processing**: After all steps are executed, simply return (implicitly `None`). The context will contain all final artifacts for the recipe, and the caller can decide what to do next. The Executor itself does not produce a separate result object.
- **Resource Management**: The Executor does not allocate significant resources that need cleanup. File handles are closed after reading, and any heavy lifting is done inside steps. Thus, no special cleanup is required beyond letting Python garbage collect as usual.
- **Statelessness**: The `Executor` class does not maintain any internal state between runs (no attributes other than possibly configuration in future). It can be re-used for multiple `execute` calls, or a new instance can be created per execution — both are fine. This aligns with minimal state philosophy.

## Component Dependencies

### Internal Components

- **Protocols** - (Required) Uses the `ContextProtocol` definition for interacting with the context, and in concept provides the implementation for the `ExecutorProtocol`. This allows Executor to be referenced by interface in other parts of the system.
- **Step Registry** - (Required) Uses `STEP_REGISTRY` to look up and instantiate step classes by their type names. The Step Registry is populated by the Steps component (loading all step implementations).
  - _Note_: The dependency on specific step classes is indirect via the registry, preventing the Executor from needing to import each step module.
- **Context** - (Optional) The actual Context object passed in will typically be an instance of the Context component. However, the Executor does not import or require `Context` directly (it is satisfied with any `ContextProtocol` implementer). This means in terms of code dependency, Executor is decoupled from the Context implementation.

### External Libraries

- **json** - (Required) Used to parse JSON strings and files into Python dictionaries.
- **os** - (Required) Used to check file path existence and determine if a string is a file path.
- **logging** - (Required) Uses Python's logging library to report on execution progress and issues.
- **typing** - (Required) Utilizes typing for type hints (e.g., `Union[str, Dict]` for recipe input, and `ContextProtocol` for context type).

### Configuration Dependencies

- **None.** The Executor does not rely on external configuration. All behavior is determined by the input recipe and the global step registry. (Logging configuration can affect it, but that's handled by the Logger component or by how `logger` is passed in.)

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
- **Step Execution Error**: If `step_instance.execute(context)` raises an Exception, catch it. Raise a new `ValueError` that wraps the original exception, with a message specifying which step index and type failed. This helps higher-level handlers log meaningful info. The original exception (`e`) is attached as the cause (`from e`) to preserve traceback.
- The Executor stops execution upon the first error encountered (fail-fast behavior), as continuing could produce unreliable results with a half-updated context.

## Output Files

- `executor.py`

## Future Considerations

- **Parallel Execution**: The current Executor executes steps sequentially. In the future, there may be an Executor variant or mode that supports parallel execution of independent steps or sub-recipes. The design using `ContextProtocol` would allow substituting a thread-safe context or clones for such execution.
- **Conditional Steps**: Future recipe formats might include conditional logic (if/else in recipes). The Executor might need to handle that by altering the sequential flow (skipping or jumping steps based on context state).
- **Plugin Steps**: If steps could be loaded dynamically (e.g., from external plugins), the registry mechanism would be extended; the Executor might then also handle dynamic registry updates or errors differently.
- **Result Collection**: Currently, all outputs are in the context. In the future, the Executor might return a summary or result object (especially if we introduce non-artifact results). Right now, this isn't needed as the context is considered the source of truth for results.
- **Executor Protocol Extensions**: If more methods are needed (for example, to preload or validate a recipe without executing, or to cancel execution), those could be added to `ExecutorProtocol` and implemented here.
