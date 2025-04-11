=== File: recipes/recipe_executor/ai_context/DEV_GUIDE_FOR_PYTHON.md ===
# Dev Guide for Python

When contributing to the Python codebase, please follow these guidelines to ensure consistency and maintainability.

- Place import statements at the top of the file.
- All optional parameters should use `Optional` from the `typing` module.
- Set types for all variables, including `self` variables in classes.
- Use `List`, `Dict`, and other type hints from the `typing` module for type annotations, include the type of the list or dictionary.
- Initialize any variables that will be used outside of a block prior to the block, including `if`, `for`, `while`, `try`, etc.
- Assume that all dependencies mentioned in the component spec or docs are installed, do not write guards for them.
- Do not create main functions for components that do not have a main function listed in the spec.
- Use full names for variables, classes, and functions. For example, use `get_workspace` instead of `gw`.
- For `__init__.py` files, use `__all__` to define the public API of the module.


=== File: recipes/recipe_executor/components/context/context_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "context",
        "component_path": "/",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/context/context_docs.md ===
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
from recipe_executor.protocols import ContextProtocol
```

_(The `ContextProtocol` interface is imported for typing or interface reference, while `Context` is the concrete class you instantiate.)_

## Initialization

You can create a Context with or without initial data:

```python
# Create an empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"input": "example data"})

# With configuration values
context = Context(config={"run_mode": "test"})

# With both artifacts and configuration
context = Context(
    artifacts={"input": "example data"},
    config={"run_mode": "test"}
)
```

When providing initial artifacts or config, Context will deep-copy them. Changes to the original dictionaries after creation won’t affect the Context.

## Core API

Once you have a Context, you use it like a dictionary for artifacts:

### Storing Values

```python
context["result"] = 42
```

Stores the value `42` under the key `"result"` in the context’s artifacts.

### Retrieving Values

```python
value = context["result"]          # Retrieves the value for "result" (KeyError if missing)
value_or_default = context.get("missing", default_value)
```

Use `context[key]` for direct access (which will throw an error if the key is not present), or `context.get(key, default)` to safely retrieve a value with a fallback.

### Checking for Keys

```python
if "result" in context:
    # Key exists in context
    print(context["result"])
```

The `in` operator checks if a given artifact key exists in the context.

### Iterating over Keys

```python
for key in context:
    print(key, context[key])

# Or equivalently:
for key in context.keys():
    print(key, context[key])
```

Context supports iteration, yielding each artifact key (internally, it iterates over a snapshot list of keys to avoid issues if you modify the context during iteration). You can also call `keys()` to get an iterator of keys explicitly. The `len(context)` function returns the number of artifacts currently stored.

### Getting All Values

```python
snapshot = context.as_dict()
```

`as_dict()` returns a deep copy of all artifacts in the context as a regular Python dictionary. This is useful if you need to inspect or serialize the entire state without risk of modifying the Context itself.

### Cloning the Context

```python
new_context = context.clone()
```

The `clone()` method creates a deep copy of the Context, including all artifacts and configuration. The returned object is a new `Context` instance that can be modified independently of the original. This is often used when running sub-recipes or parallel steps to ensure each execution has an isolated context state.

## Important Notes

- **Shared State**: The Context is shared across all steps in a recipe execution. Any step that writes to the context (e.g., `context["x"] = value`) is making that data available to subsequent steps. This is how data flows through a recipe.
- **No Thread Safety**: The Context class does not implement any locking or thread-safety mechanisms. It assumes sequential access. If you need to use it in parallel, each parallel thread or process should work on a cloned copy of the Context to avoid race conditions (as done in the Parallel step implementation).
- **Protocols Interface**: The `Context` class implements the `ContextProtocol` interface defined in the Protocols component. When writing code that interacts with contexts, you can use `ContextProtocol` in type hints to allow any context implementation. In practice, you will typically use the provided `Context` class unless you extend the system.
- **Configuration vs Artifacts**: Remember that `context.config` is a public attribute (a dict) meant for static configuration values. It is not manipulated via the dictionary interface (`__getitem__`/`__setitem__`). This separation is by convention; Context does not prevent you from modifying `context.config` directly, so it’s up to the user to treat config as read-only during execution.


=== File: recipes/recipe_executor/components/context/context_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/context.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/context/context_spec.md ===
# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple, dictionary-like interface that steps and other components use to store and retrieve data (artifacts) during recipe execution, along with a separate space for configuration values.

## Core Requirements

- Maintain a store for **artifacts** (dynamic data produced and consumed by steps) and a separate store for **configuration** (static or initial settings).
- Support dictionary-like operations for artifacts:
  - Setting values by key (e.g., `context["x"] = value`).
  - Retrieving values by key (e.g., `value = context["x"]` or `context.get("x")`).
  - Checking for keys (`"x" in context`).
  - Iterating over keys (for example, `for k in context: ...`).
- Ensure that modifying the context in one step affects subsequent steps (shared mutability), while also allowing safe copying when needed.
- Provide a `clone()` method to create a deep copy of the entire context (both artifacts and configuration) for use cases like parallel execution where isolation is required.
- Remain lightweight and straightforward, following minimalist design principles (it should essentially behave like a `dict` with a config attached, without extra complexity).

## Implementation Considerations

- Use a Python dictionary internally to store artifacts. The keys are strings and values can be of any type (no restriction on artifact data types).
- Store configuration in a separate dictionary (`config` attribute) to distinguish it from runtime artifacts. Configuration might be populated at context creation and typically remains constant, but it's not enforced as immutable by the class.
- On initialization (`__init__`), deep copy any provided artifacts or config dictionaries. This prevents unintentional side effects if the caller modifies the dictionaries after passing them in.
- Implement the magic methods `__getitem__`, `__setitem__`, `__contains__`, `__iter__`, and `__len__` to mimic standard dict behavior for artifacts. Also provide a `keys()` method for convenience.
- The `get` method should allow a default value, similar to `dict.get`, to avoid raising exceptions on missing keys.
- When iterating (`__iter__` or using `keys()`), return a static list or iterator that won’t be affected by concurrent modifications (for example, by copying the key list).
- The `clone()` method should deep copy both artifacts and configuration to produce a completely independent Context. This is important for features like running sub-recipes in parallel or reusing a context as a template.
- Raise a `KeyError` with a clear message in `__getitem__` if a key is not found, to help with debugging missing artifact issues.
- Do not implement any locking or thread-safety measures; the context is intended for sequential use within the executor (concurrent modifications are handled by using `clone` for parallelism instead).
- The Context class should implement the `ContextProtocol` interface defined in the Protocols component. That means any changes to the interface (methods or behavior) should be reflected in both the class and the protocol definition. In practice, the Context class already provides all methods required by `ContextProtocol`.

## Logging

- Debug: Not typically used within Context. (If needed, could log when keys are set or retrieved, but by default it stays silent.)
- Info: None. The Context operations are low-level and usually do not produce log output by themselves.

## Dependency Integration Considerations

### Internal Components

- **Protocols** - (Required) The Context component conforms to the `ContextProtocol` interface, which is defined in the Protocols component. This ensures other components (like Executor or Steps) interact with Context through a well-defined contract.

### External Libraries

- **copy** (Python stdlib) - (Required) Uses `copy.deepcopy` for cloning internal state safely.
- **typing** - (Required) Used for type hints (e.g., `Dict[str, Any]`, `Iterator[str]`) to clarify usage. (The Protocol for Context is also part of typing integration.)

### Configuration Dependencies

- **None.** The Context component does not rely on external configuration. It is typically configured via its constructor arguments (artifacts and config dicts) provided at runtime by Main or a calling component.

## Error Handling

- Attempts to access a missing artifact key via `context["missing_key"]` result in a `KeyError`. The error message explicitly names the missing key for clarity (e.g., `"Key 'foo' not found in Context."`).
- The `get` method returns a default (or `None` if not provided) instead of raising an error for missing keys, offering a safe way to query the context.
- Setting a key (`context["x"] = value`) has no special error cases; it will overwrite existing values if the key already exists.
- Cloning always succeeds barring extreme cases (like objects in the context that are not copyable); such cases would raise exceptions from `copy.deepcopy` which propagate up (this is acceptable, as it would be a misusage of context content types).

## Output Files

- `context.py`

## Future Considerations

- **Namespacing or Hierarchies**: In larger workflows, there might be a need to namespace context data (e.g., per step or per sub-recipe) to avoid key collisions. Future versions might introduce optional namespacing schemes or structured keys.
- **Selective Cloning**: For efficiency, a future context might support partial clone or lazy copy on write if performance becomes a concern with very large contexts.
- **Serialization**: Consider methods to serialize and deserialize the entire context (for caching or checkpointing execution state).
- **Immutable Context Option**: Possibly provide a mode or subclass for an immutable context (read-only once created) for scenarios where you want to ensure no step modifies the data (this would be a significant change and is speculative).


=== File: recipes/recipe_executor/components/executor/executor_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/registry/registry_docs.md",
      "artifact": "registry_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "executor",
        "component_path": "/",
        "existing_code": "{{existing_code}}",
        "additional_content": "<REGISTRY_DOCS>\n{{registry_docs}}\n</REGISTRY_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/executor/executor_docs.md ===
# Executor Component Usage

## Importing

```python
from recipe_executor.executor import Executor
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
```

_(Import the concrete `Executor` to create an instance, and import `ExecutorProtocol`/`ContextProtocol` if you want to use interfaces in type hints.)_

## Basic Usage

The Executor has a single primary method: `execute()`. This method loads and runs a recipe with a given context. Typically, you will create a `Context` (for artifacts) and an `Executor`, then call execute:

```python
from recipe_executor import Context

# Create context and executor (with protocol typing for clarity)
context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor()

# Execute a recipe from a JSON file path
executor.execute("path/to/recipe.json", context)

# Execute a recipe from a JSON string
json_string = '{"steps": [{"type": "read_files", "path": "example.txt", "artifact": "file_content"}]}'
executor.execute(json_string, context)

# Execute a recipe from a pre-defined dictionary
recipe_dict = {
    "steps": [
        {"type": "write_files", "files": [{"path": "out.txt", "content": "Hello"}]}
    ]
}
executor.execute(recipe_dict, context)
```

In each case, the Executor will parse the input (if needed) and sequentially execute each step in the recipe using the same `context`. After execution, the `context` may contain new artifacts produced by the steps (for example, in the above cases, `context["file_content"]` might hold data read from a file, or data written can be confirmed by reading back from disk).

## Behavior Details

- The context passed into `execute` is mutated in-place by the steps. You should create a fresh Context (or clone an existing one) if you plan to reuse it for multiple recipe executions to avoid cross-contamination of data.
- If the recipe path is invalid or the JSON is malformed, `execute` will raise an error (ValueError or TypeError). Ensure you handle exceptions when calling `execute` if there's a possibility of bad input.
- The Executor uses the step registry to find the implementation for each step type. All default steps (like `"read_files"`, `"write_files"`, `"execute_recipe"`, etc.) are registered when you import the `recipe_executor.steps` modules. Custom steps need to be registered in the registry before Executor can use them.
- Logging: By default, Executor will use the library's logger. To integrate with your own logging, you can pass a `logging.Logger` instance via the `logger` argument to `execute()`. This will suppress the internal setup of a new logger and use yours instead.

## Important Notes

- **Interface Compliance**: The `Executor` class implements the `ExecutorProtocol` interface. Its `execute` method is designed to accept any object implementing `ContextProtocol`. In practice, you will pass a `Context` instance (which fulfills that protocol). This means the Executor is flexible — if the context were some subclass or alternative implementation, Executor would still work as long as it follows the interface.
- **One Executor, One Execution**: An `Executor` instance can be reused to run multiple recipes (simply call `execute` again with a different recipe and context), but it does not retain any state between runs. You can also create a new `Executor()` for each execution. Both approaches are acceptable; there's typically little overhead in creating a new Executor.
- **Step Instantiation**: When the Executor runs a step, it creates a new instance of the step class for each step execution (even if the same step type appears multiple times, each occurrence is a fresh instance). The step class’s `__init__` usually takes the step configuration (from the recipe) and an optional logger.
- **Error Handling**: If any step fails (raises an exception), Executor will halt the execution of the remaining steps. The exception will bubble up as a `ValueError` with context about which step failed. You should be prepared to catch exceptions around `executor.execute(...)` in contexts where a failure is possible or should not crash the entire program.
- **Context After Execution**: After `execute` completes (successfully), the context contains all the artifacts that steps have placed into it. You can inspect `context` to get results (for example, if a step writes an output, it might be found in `context["output_key"]`). The context is your way to retrieve outcomes from the recipe.


=== File: recipes/recipe_executor/components/executor/executor_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/executor.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/executor/executor_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/executor/executor_spec.md ===
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


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "ai_context/AZURE_IDENTITY_CLIENT_DOCS.md",
      "artifact": "azure_identity_client_docs"
    },
    {
      "type": "read_files",
      "path": "ai_context/PYDANTIC_AI_DOCS.md",
      "artifact": "pydantic_ai_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "azure_openai",
        "component_path": "/llm_utils",
        "existing_code": "{{existing_code}}",
        "additional_content": "<AZURE_IDENTITY_CLIENT_DOCS>\n{{azure_identity_client_docs}}\n</AZURE_IDENTITY_CLIENT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<PYDANTIC_AI_DOCUMENTATION>\n{{pydantic_ai_docs}}\n</PYDANTIC_AI_DOCUMENTATION>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_docs.md ===
# Azure OpenAI Component Usage

## Importing

```python
import recipe_executor.llm_utils.azure_openai
```

## Basic Usage

```python
def get_openai_model(model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = "RecipeExecutor") -> pydantic_ia.models.openai.OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from environment variables for Azure OpenAI.

    Args:
        model_name (str): Model name, such as "gpt-4o" or "o3-mini".
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance for Azure OpenAI.

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python
# Get an OpenAI model using Azure OpenAI
openai_model = azure_openai.get_openai_model("o3-mini")

# Get an OpenAI model using Azure OpenAI with a specific deployment name
openai_model = azure_openai.get_openai_model("o3-mini", "my_deployment_name")
```

## Environment Variables

The component uses environment variables for authentication and configuration. Depending upon the authentication method, set the following environment variables:

### Option 1: Managed Identity with Default Managed Identity

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 2: Managed Identity with Custom Client ID

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_MANAGED_IDENTITY_CLIENT_ID= # Required
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 3: API Key Authentication

```bash
AZURE_OPENAI_API_KEY= # Required
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/llm_utils/azure_openai.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/azure_openai/azure_openai_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_spec.md ===
# Azure OpenAI Component Specification

## Purpose

The Azure OpenAI component provides a PydanticAI wrapper for Azure OpenAI models for use with PydanticAI Agents. It handles model initialization and authentication.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIModel instance
- Support choice of api key or Azure Identity for authentication
- Use the `openai` library for Azure OpenAI client
- Implement basic error handling

## Implementation Considerations

- Load api keys and endpoints from environment variables, validating their presence
- If using Azure Identity:
  - AsyncAzureOpenAI client must be created with a token provider function
  - If using a custom client ID, use `ManagedIdentityCredential` with the specified client ID
- Create an `openai.AsyncAzureOpenAI` client with the provided token provider or API key
- Create a `pydantic_ai.providers.openai.OpenAIProvider` with the Azure OpenAI client
- Return a `pydantic_ai.models.openai.OpenAIModel` with the model name and provider

## Implementation Hints

```python
# Option 1: Create AsyncAzureOpenAI client with API key
azure_client = AsyncAzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Option 2: Create AsyncAzureOpenAI client with Azure Identity
azure_client = AsyncAzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Use the client to create the OpenAIProvider
openai_model = OpenAIModel(
    model_name,
    provider=OpenAIProvider(openai_client=azure_client),
)
```

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name and auth method (api key or Azure Identity)

## Component Dependencies

### Internal Components

None

### External Libraries

- **pydantic-ai** - (Required) Uses PydanticAI's OpenAIModel and OpenAIProvider for model management
- **openai** - (Required) Uses AsyncAzureOpenAI client for API communication
- **azure-identity** - (Required for managed identity) Uses DefaultAzureCredential, ManagedIdentityCredential, and get_bearer_token_provider for token provision

### Configuration Dependencies

- **AZURE_USE_MANAGED_IDENTITY** - (Optional) Boolean flag to use Azure Identity for authentication
- **AZURE_OPENAI_API_KEY** - (Required for API key auth) API key for Azure OpenAI authentication
- **AZURE_OPENAI_ENDPOINT** - (Required) Endpoint URL for Azure OpenAI service
- **AZURE_OPENAI_DEPLOYMENT_NAME** - (Required) Deployment name in Azure OpenAI
- **AZURE_OPENAI_API_VERSION** - (Required) API version to use with Azure OpenAI
- **AZURE_CLIENT_ID** - (Optional) Client ID for managed identity authentication

## Error Handling

- Log detailed error information for debugging

## Output Files

- `llm_utils/azure_openai.py`


=== File: recipes/recipe_executor/components/llm_utils/create.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/llm/llm_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/azure_openai/azure_openai_create.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/edit.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/llm/llm_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/azure_openai/azure_openai_edit.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/llm/llm_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_docs.md",
      "artifact": "models_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/azure_openai/azure_openai_docs.md",
      "artifact": "azure_openai_docs"
    },
    {
      "type": "read_files",
      "path": "ai_context/PYDANTIC_AI_DOCS.md",
      "artifact": "pydantic_ai_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "llm",
        "component_path": "/llm_utils",
        "existing_code": "{{existing_code}}",
        "additional_content": "<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<AZURE_OPENAI_DOCUMENTATION>\n{{azure_openai_docs}}\n</AZURE_OPENAI_DOCUMENTATION>\n<PYDANTIC_AI_DOCUMENTATION>\n{{pydantic_ai_docs}}\n</PYDANTIC_AI_DOCUMENTATION>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/llm/llm_docs.md ===
# LLM Component Usage

## Importing

```python
from recipe_executor.llm_utils.llm import call_llm
```

## Basic Usage

The LLM component provides one main function:

```python
def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = "RecipeExecutor") -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or 'provider:model_name:deployment_name').
        If None, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"

    Returns:
        FileGenerationResult: The structured result data containing generated files and commentary.

    Raises:
        Exception: If model value cannot be mapped to valid provider/model_name , LLM call fails, or result validation fails.
    """
```

Usage example:

```python
# Call LLM with default model
result = call_llm("Generate a Python utility module for handling dates.")

# Call with specific model
result = call_llm(
    prompt="Create a React component for a user profile page.",
    model="openai:o3-mini"
)
```

```python
def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model using structured output.

    Args:
        model_id (Optional[str]): Model identifier in format 'provider:model_name'.
        If None, defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured Agent ready to process LLM requests and return structured results with files and commentary.
    """
```

Usage example:

```python
# Get default agent (openai:gpt-4o)
default_agent = get_agent()

# Get agent with specific model
custom_agent = get_agent(model_id="anthropic:claude-3-7-sonnet-latest")
results = custom_agent.run_async("Generate a Python utility module for handling dates.")
# Access FileGenerationResult
file_generation_result = results.data

```

## Model ID Format

The component uses a standardized model identifier format:

```
All models:
provider:model_name

Additional option for Azure OpenAI (otherwise assume deployment_name is the same as model_name):
azure:model_name:deployment_name
```

### Supported providers:

- **openai**: OpenAI models (e.g., `gpt-4o`, `o3-mini`)
- **anthropic**: Anthropic models (e.g., `claude-3-7-sonnet-latest`)
- **gemini**: Gemini models (e.g., `gemini-pro`)
- **azure**: Azure OpenAI models (e.g., `azure:gpt-4o`, `azure:o3-mini`)
- **azure**: Azure OpenAI models with custom deployment name (e.g., `azure:gpt-4o:my_deployment_name`)

## Error Handling

Example of error handling:

```python
try:
    result = call_llm(prompt, model_id)
    # Process result
except ValueError as e:
    # Handle invalid model ID or format
    print(f"Invalid model configuration: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"LLM call failed: {e}")
```

## Integration with Steps

The LLM component is primarily used by the GenerateWithLLMStep:

```python
# Example from GenerateWithLLMStep.execute()
def execute(self, context: ContextProtocol) -> None:
    rendered_prompt = render_template(self.config.prompt, context)
    rendered_model = render_template(self.config.model, context)

    response = call_llm(rendered_prompt, rendered_model)

    artifact_key = render_template(self.config.artifact, context)
    context[artifact_key] = response
```

## Important Notes

- Calling a model incurs API costs with the respective provider
- OpenAI is the default provider if none is specified
- The component logs request details at debug level
- Responses are validated against the FileGenerationResult model


=== File: recipes/recipe_executor/components/llm_utils/llm/llm_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/llm.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm/llm_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/llm/llm_spec.md ===
# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini (not Vertex))
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI for consistent handling and validation of LLM responses
- Implement basic error handling
- Support structured output format for file generation

## Implementation Considerations

- Use a clear provider:model_name identifier format
- Do not need to pass api keys directly to model classes (do need to provide to AzureProvider)
- Use PydanticAI's provider-specific model classes, passing only the model name
  - pydantic_ai.models.openai.OpenAIModel (used for Azure OpenAI)
  - pydantic_ai.models.anthropic.AnthropicModel
  - pydantic_ai.models.gemini.GeminiModel
- Create a PydanticAI Agent with the model and a structured output type
- Use the `run_sync` method of the Agent to make requests
- CRITICAL: make sure to return the result.data in the call_llm method

## Logging

- Debug: Log full request payload before making call and then full response payload after receiving it
- Info: Log model name and provider before making call (do not include the request payload details) and then include response times and tokens used upon completion (do not include the response payload details)

## Component Dependencies

### Internal Components

- **Models** - (Required) Uses FileGenerationResult and FileSpec for structured output validation
- **Azure OpenAI** - (Required for Azure provider) Uses get_azure_openai_model for Azure OpenAI model initialization

### External Libraries

- **pydantic-ai** - (Required) Relies on PydanticAI for model initialization, Agent-based request handling, and structured-output response processing

### Configuration Dependencies

- **DEFAULT_MODEL** - (Optional) Environment variable specifying the default LLM model in format "provider:model_name"
- **OPENAI_API_KEY** - (Required for OpenAI) API key for OpenAI access
- **ANTHROPIC_API_KEY** - (Required for Anthropic) API key for Anthropic access
- **GEMINI_API_KEY** - (Required for Gemini) API key for Google Gemini AI access

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Output Files

- `llm_utils/llm.py`

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning

## Dependency Integration Considerations

### PydanticAI

Create a PydanticAI model for the LLM provider and model name. This will be used to initialize the model and make requests.

```python
def get_model(model_id: str) -> OpenAIModel | AnthropicModel | GeminiModel:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider:model_name' or 'provider:model_name:deployment_name'.

    Supported providers:
    - openai
    - anthropic
    - gemini
    - azure (for Azure OpenAI, use 'azure:model_name:deployment_name' or 'azure:model_name')

    Args:
        model_id (str): Model identifier in format 'provider:model_name'
            or 'provider:model_name:deployment_name'.
            If None, defaults to 'openai:gpt-4o'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai:o3-mini")
# Uses OpenAIModel('o3-mini')

# Get an Anthropic model
anthropic_model = get_model("anthropic:claude-3-7-sonnet-latest")
# Uses AnthropicModel('claude-3-7-sonnet-latest')

# Get a Gemini model
gemini_model = get_model("gemini:gemini-pro")
# Uses GeminiModel('gemini-pro')
```


=== File: recipes/recipe_executor/components/logger/logger_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "logger",
        "component_path": "/",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/logger/logger_docs.md ===
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
class ReadFilesStep(BaseStep):
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("RecipeExecutor")
        # ...
```

## Important Notes

1. Logs are cleared (truncated) on each run
2. Debug logs can get large with detailed information
3. The log directory is created if it doesn't exist
4. The logger name "RecipeExecutor" is consistent across the system


=== File: recipes/recipe_executor/components/logger/logger_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/logger.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/logger/logger_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/logger/logger_spec.md ===
# Logger Component Specification

## Purpose

The Logger component provides a consistent logging interface for the Recipe Executor system. It initializes and configures logging, writes logs to appropriate files, and ensures that all components can log messages at different severity levels.

## Core Requirements

- Initialize a logger that writes to both stdout and log files
- Support different log levels (DEBUG, INFO, ERROR)
- Create separate log files for each level
- For stdout, set the log level to INFO
- Clear existing logs on each run to prevent unbounded growth
- Provide a consistent log format with timestamps and log levels
- Create log directories if they don't exist

## Implementation Considerations

- Use Python's standard logging module directly
- Reset existing handlers to ensure consistent configuration
- Set up separate handlers for console and different log files
- Create the log directory if it doesn't exist
- Use mode="w" for file handlers to clear previous logs

## Logging

- Debug: Log that the logger is being initialized, the log directory being created, and any errors encountered during initialization
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

- **Python stdlib logging** - (Required) Uses Python's standard logging module for core functionality

### Configuration Dependencies

None

## Error Handling

- Catch and report directory creation failures
- Handle file access permission issues
- Provide clear error messages for logging setup failures

## Future Considerations

- Customizable log formats

## Output Files

- `logger.py`


=== File: recipes/recipe_executor/components/main/main_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/executor/executor_docs.md",
      "artifact": "executor_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/logger/logger_docs.md",
      "artifact": "logger_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "main",
        "component_path": "/",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<EXECUTOR_DOCS>\n{{executor_docs}}\n</EXECUTOR_DOCS>\n<LOGGER_DOCS>\n{{logger_docs}}\n</LOGGER_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/main/main_docs.md ===
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
logger.error("An error occurred during recipe execution: ...", exc_info=True)
```

The stack trace for exceptions is output to stderr (via `traceback.format_exc()`) to aid in debugging issues directly from the console.

## Important Notes

1. The main entry point is designed to be simple and minimal. It delegates the heavy lifting to the `Context` and `Executor` components.
2. All steps in the executed recipe share the same context instance, which is created by Main from the provided context arguments. This context implements the `ContextProtocol` interface (see Protocols documentation), though in usage you typically interact with it via the `Context` class.
3. The Main component itself doesn't enforce any type of step ordering beyond what the recipe dictates; it simply invokes the Executor and waits for it to process the steps sequentially.
4. Environment variables (for example, API keys for LLM steps) can be set in a `.env` file. Main will load this file at startup via `load_dotenv()`, making those values available to components that need them.
5. Logging is configured at runtime when Main calls `init_logger`. The logs (including debug information and errors) are saved in the directory specified by `--log-dir`. Each run may append to these logs, so it's advisable to monitor or clean the log directory if running many recipes.


=== File: recipes/recipe_executor/components/main/main_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/main.py,{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/__init__.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/main/main_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/main/main_spec.md ===
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


=== File: recipes/recipe_executor/components/models/models_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "models",
        "component_path": "/",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/models/models_docs.md ===
# Models Component Usage

## Importing

```python
from recipe_executor.models import (
    FileSpec,
    FileGenerationResult,
    RecipeStep,
    Recipe
)
```

## File Generation Models

### FileSpec

Represents a single file to be generated:

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """

    path: str
    content: str
```

Usage example:

```python
file = FileSpec(
    path="src/utils.py",
    content="def hello_world():\n    print('Hello, world!')"
)

# Access properties
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
```

### FileGenerationResult

Contains a collection of generated files and optional commentary:

```python
class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """

    files: List[FileSpec]
    commentary: Optional[str] = None
```

Usage example:

```python
result = FileGenerationResult(
    files=[
        FileSpec(path="src/utils.py", content="def util_function():\n    pass"),
        FileSpec(path="src/main.py", content="from utils import util_function")
    ],
    commentary="Generated utility module and main script"
)

# Iterate through files
for file in result.files:
    print(f"Writing to {file.path}")
    # ... write file.content to file.path
```

## Recipe Models

### RecipeStep

Represents a single step in a recipe:

```python
class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """

    type: str
    config: Dict
```

### Recipe

Represents a complete recipe with multiple steps:

```python
class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]
```

Usage example:

```python
from recipe_executor.models import Recipe, RecipeStep

# Create a recipe with steps
recipe = Recipe(
    steps=[
        RecipeStep(
            type="read_file",
            config={"file_path": "specs/component_spec.md", "store_key": "spec"}
        ),
        RecipeStep(
            type="generate",
            config={
                "prompt": "Generate code for: {{spec}}",
                "model": "{{model|default:'openai:o3-mini'}}",
                "artifact": "code_result"
            }
        ),
        RecipeStep(
            type="write_files",
            config={"artifact": "code_result", "root": "./output"}
        )
    ]
)

# Validate recipe structure
recipe_dict = recipe.dict()
```

## Model Validation

All models inherit from Pydantic's BaseModel, providing automatic validation:

```python
# This will raise a validation error because path is required
try:
    FileSpec(content="File content")
except Exception as e:
    print(f"Validation error: {e}")

# This works correctly
valid_file = FileSpec(path="file.txt", content="File content")
```

## Important Notes

1. Models provide runtime validation in addition to static type checking
2. Default values are provided for common configuration options
3. Models can be converted to dictionaries with `.dict()` method
4. Models can be created from dictionaries with `Model(**dict_data)`


=== File: recipes/recipe_executor/components/models/models_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/models.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/models/models_spec.md ===
# Models Component Specification

## Purpose

The Models component defines the core data structures used throughout the Recipe Executor system. It provides Pydantic models for validating and structuring data, including recipe steps, and file generation results.

## Core Requirements

- Define consistent data structures for file generation results
- Provide configuration models for various step types
- Support recipe structure validation
- Leverage Pydantic for schema validation and documentation
- Include clear type hints and docstrings

## Implementation Considerations

- Use Pydantic models for all data structures
- Keep models focused and minimal
- Provide sensible defaults where appropriate
- Use descriptive field names and docstrings
- Focus on essential fields without over-engineering

## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

- **pydantic** - (Required) Uses Pydantic for schema validation and model definition

### Configuration Dependencies

None

## Output Files

- `models.py`

## Future Considerations

- Extended validation for complex fields


=== File: recipes/recipe_executor/components/protocols/protocols_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "protocols",
        "component_path": "/",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/protocols/protocols_docs.md ===
# Protocols Component Usage

The Protocols component provides **interface definitions** for key parts of the Recipe Executor system. By defining formal contracts (`Protocol` classes) for the Executor, Context, and Step, this component decouples implementations from each other and serves as the single source of truth for how components interact. All components that implement or use these interfaces should refer to the Protocols component to ensure consistency.

## Provided Interfaces

### `ContextProtocol`

Defines the interface for context-like objects that hold shared state (artifacts and configuration). It includes dictionary-like methods (`__getitem__`, `__setitem__`, etc.), a `get` method for safe retrieval, an `as_dict` for copying all data, and a `clone` method for deep-copying the entire context. Any context implementation (such as the built-in `Context` class) should fulfill this interface.

### `StepProtocol`

Specifies the interface for an executable step. It declares a single method `execute(context: ContextProtocol) -> None`. All step classes (via the base class or otherwise) are expected to implement this method to perform their task using the provided context. This ensures a consistent entry point for executing any step.

### `ExecutorProtocol`

Describes the interface for recipe executors. It currently defines one primary method: `execute(recipe, context, logger=None) -> None`. An `ExecutorProtocol` implementor (like the concrete `Executor` class) must be able to take a recipe (in various forms) and a context (any `ContextProtocol` implementation) and execute the recipe's steps sequentially. The optional logger parameter allows injection of a logging facility.

## How to Use These Protocols

Developers should **import the protocol interfaces** when writing type hints or designing new components. For example, to annotate variables or function parameters:

```python
from recipe_executor import Executor, Context
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol

context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor()
executor.execute("path/to/recipe.json", context)
```

In this example, `Context()` is the concrete implementation provided by the system (which implements `ContextProtocol`), and `Executor()` is the concrete executor implementing `ExecutorProtocol`. By annotating them as `ContextProtocol` and `ExecutorProtocol`, we emphasize that our code relies only on the defined interface, not a specific implementation. This is optional for running the code (the system will work with or without the annotations), but it is useful for clarity and static type checking.

## Implementation Notes for Developers

- **For Implementers**: When creating a new Context or Executor implementation (or any new Step), ensure it provides all methods defined in the corresponding protocol. You don't need to explicitly subclass the `Protocol`, thanks to Python's structural typing, but documenting that it implements the interface is good practice. The existing classes (`Context`, `Executor`, and all steps via `BaseStep`) already adhere to `ContextProtocol`, `ExecutorProtocol`, and `StepProtocol` respectively.

- **For Consumers**: When writing functions or methods that accept a context or executor, use `ContextProtocol` or `ExecutorProtocol` in the type hints. This way, your code can work with any object that respects the contract, making the system more extensible. For instance, a function could be annotated to accept `context: ContextProtocol` and thus work with the standard `Context` or any future alternative context implementation.

- **Decoupling and Cycle Prevention**: By using these protocols, components like the Executor and steps do not need to import each other's concrete classes. This breaks import cycles (for example, steps can call executor functionality through `ExecutorProtocol` without a direct import of the Executor class). The Protocols component thus centralizes interface knowledge: it owns the definitions of `execute` methods and context operations that others rely on.

All developers and AI recipes should reference **this protocols documentation** and the `protocols.py` definitions when needing to understand or use the interfaces between components. This ensures that the system’s pieces remain loosely coupled and conformant to the agreed contracts.


=== File: recipes/recipe_executor/components/protocols/protocols_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/components/protocols/protocols.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/protocols/protocols_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/protocols/protocols_spec.md ===
# Protocols Component Specification

## Purpose

The Protocols component defines the shared interface contracts for core parts of the Recipe Executor system. It centralizes the definitions of how the Executor, Context, and Steps interact, matching project conventions of clear separation. By providing Protocol-based interfaces, this component ensures all implementers (and consumers) of these interfaces adhere to the same methods and signatures, thereby promoting consistency and preventing tight coupling or import cycles between components.

## Core Requirements

- Define a `ContextProtocol` that captures the required behaviors of the Context (dictionary-like access, retrieval, iteration, cloning).
- Define a `StepProtocol` that captures the execution interface for any step (the `execute(context)` method signature).
- Define an `ExecutorProtocol` that captures the interface of the executor (the `execute(recipe, context, logger)` method signature).
- Ensure these protocols are the single source of truth for their respective contracts, referenced throughout the codebase for type annotations and documentation.
- Eliminate direct references to concrete classes (e.g., `Context` or `Executor`) in other components’ interfaces by using these protocol definitions, thereby avoiding circular dependencies.
- Follow the project's minimalist design philosophy: interfaces should be concise, containing only what is necessary for inter-component communication.

## Implementation Considerations

- Use Python's `typing.Protocol` to define interfaces in a structural subtyping manner. This allows classes to implement the protocols without explicit inheritance, maintaining loose coupling.
- Mark protocol interfaces with `@runtime_checkable` to allow runtime enforcement (e.g., in tests) if needed, without impacting normal execution.
- The `ContextProtocol` should include all methods that other components (steps, executor) rely on. This includes standard mapping methods (`__getitem__`, `__setitem__`, etc.), as well as `get`, `clone`, and any other utility needed for context usage (like `keys`, `as_dict`).
- The `StepProtocol` interface is minimal by design (just the `execute` method with a `ContextProtocol` parameter), since step initialization and configuration are handled separately. This focuses the contract on execution behavior only.
- The `ExecutorProtocol` should accept a recipe in various forms (string path, JSON string, or dict) and a context implementing `ContextProtocol`. It returns `None` and is expected to raise exceptions on errors (as documented in Executor component). Logging is passed optionally.
- No actual business logic or data storage should exist in `protocols.py`; it strictly contains interface definitions with `...` (ellipsis) as method bodies. This keeps it aligned with the "contracts only" role of the component.
- Ensure naming and signatures exactly match those used in concrete classes to avoid confusion. For example, `ContextProtocol.clone()` returns a `ContextProtocol` to allow flexibility in context implementations.
- Keep the protocols in a single file (`protocols.py`) at the root of the package (no sub-package), consistent with single-file component convention. This file becomes a lightweight dependency for any module that needs the interfaces.

## Logging

- None

## Dependency Integration Considerations

### Internal Components

- None

### External Libraries

- **typing** - (Required) Uses Python's built-in `typing` module (particularly `Protocol` and related features) to define structural interfaces.
- **logging** - (Required) Uses Python's standard `logging` module for type annotations of logger parameters (no logging calls are made in protocols).

### Configuration Dependencies

- None

## Error Handling

- None

## Output Files

- `protocols.py` (contains `ContextProtocol`, `StepProtocol`, `ExecutorProtocol` definitions)

## Future Considerations

- As the system evolves, additional protocols might be introduced for new interface contracts (for example, if a new component needs a defined interface).
- If stronger type enforcement is needed, consider adding abstract base classes (ABCs) in addition to protocols. However, current philosophy favors Protocol for flexibility and minimal intrusion.
- Any changes to these protocols (such as adding a method) should be done cautiously and documented clearly in `protocols_docs.md`, as they affect multiple components. All implementers would need to be updated to comply with any interface changes.
- Continue treating the `protocols_docs.md` as the authoritative reference for interface contracts – all developers (and AI recipes) should consult it when working with or implementing core interfaces.


=== File: recipes/recipe_executor/components/steps/base/base_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_docs.md",
      "artifact": "models_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "base",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/base/base_docs.md ===
# Steps Base Component Usage

## Importing

Typically, as a recipe or step author, you won't import `BaseStep` or `StepConfig` in end-user code. These are used when defining new steps. However, for completeness:

```python
from recipe_executor.steps.base import BaseStep, StepConfig
```

When creating a new custom step, you will subclass `BaseStep` and define a `StepConfig` subclass for its configuration.

## Defining a New Step (Example)

To illustrate how `BaseStep` is used, let's say you want to create a new step type called `"EchoStep"` that simply logs a message:

1. **Define the Configuration**: Subclass `StepConfig` to define any inputs the step needs. If none are required, you could even use `StepConfig` as is, but we'll define one for example:

   ```python
   class EchoConfig(StepConfig):
       message: str
   ```

   This uses Pydantic to require a `message` field for the step.

2. **Define the Step Class**: Subclass `BaseStep` with the config type and implement `execute`:

   ```python
   class EchoStep(BaseStep[EchoConfig]):
       def __init__(self, config: dict, logger=None):
           super().__init__(EchoConfig(**config), logger)

       def execute(self, context: ContextProtocol) -> None:
           # Simply log the message
           self.logger.info(f"Echo: {self.config.message}")
   ```

   A few things to note:

   - We call `super().__init__` with a `EchoConfig(**config)` to parse the raw config dict into a Pydantic model. Now `self.config` is an `EchoConfig` instance (with attribute `message`).
   - We use `ContextProtocol` in the `execute` signature, meaning any `context` passed that implements the required interface will work. Usually this will be the standard `Context`.
   - In `execute`, we just log the message. We could also interact with `context` (e.g., read or write `context` entries) if needed.

3. **Register the Step**: Finally, to use `EchoStep` in recipes, add it to the step registry:

   ```python
   from recipe_executor.steps.registry import STEP_REGISTRY
   STEP_REGISTRY["echo"] = EchoStep
   ```

Now, any recipe with a step like `{"type": "echo", "message": "Hello World"}` will use `EchoStep`.

## Important Notes

- **Inheriting BaseStep**: All step implementations **must** inherit from `BaseStep` and implement the `execute` method. This ensures they conform to the `StepProtocol` (the interface contract for steps). If a step class does not implement `execute`, it cannot be instantiated due to the abstract base.
- **Configuration Validation**: Using Pydantic `StepConfig` for your step’s configuration is highly recommended. It will automatically validate types and required fields. In the example above, if a recipe is missing the `"message"` field or if it's not a string, the creation of `EchoConfig` would raise an error, preventing execution with bad config.
- **Context Usage**: Steps interact with the execution context via the interface methods defined in `ContextProtocol`. For example, a step can do `value = context.get("some_key")` or `context["result"] = data`. By programming against `ContextProtocol`, your step could work with any context implementation. In practice, the provided `Context` is used.
- **Logging**: Each step gets a logger (`self.logger`). Use it to log important events or data within the step. The logger is typically passed from the Executor, which means all step logs can be captured in the main log output. This is very useful for debugging complex recipes.
- **BaseStep Utility**: Aside from providing the structure, `BaseStep` doesn't interfere with your step logic. You control what happens in `execute`. However, because `BaseStep` takes care of storing config and logger, you should always call its `__init__` in your step’s constructor (as shown with `super().__init__`). This ensures the config is properly parsed and the logger is set up.
- **Step Lifecycle**: There is no explicit "tear down" method for steps. If your step allocates resources (files, network connections, etc.), you should handle those within the step itself (and possibly in the `finally` block or context managers inside `execute`). Each step instance is short-lived (used only for one execution and then discarded).
- **Adhering to StepProtocol**: By following the pattern above, your custom step automatically adheres to `StepProtocol` because it implements `execute(context: ContextProtocol)`. This means you could treat it as a `StepProtocol` in any high-level logic, but more importantly the system (Executor) will treat it correctly as a step.

In summary, `BaseStep` and `StepConfig` provide a minimal framework to create new steps with confidence that they will integrate smoothly. They enforce the presence of an `execute` method and provide convenience in config handling and logging, letting step authors focus on the core logic of the step.


=== File: recipes/recipe_executor/components/steps/base/base_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/base.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/base/base_spec.md ===
# Steps Base Component Specification

## Purpose

The Steps Base component defines the foundational abstract classes and interfaces for all step implementations in the Recipe Executor system. It establishes a common structure and contract for steps, ensuring consistent behavior and seamless integration with the executor and context.

## Core Requirements

- Provide an abstract base class (`BaseStep`) that all concrete step classes will inherit from.
- Provide a base configuration model class (`StepConfig`) using Pydantic for validation of step-specific configuration.
- Enforce a consistent interface for step execution (each step must implement an `execute(context)` method).
- Utilize generics to allow `BaseStep` to be typed with a specific `StepConfig` subclass for that step, enabling type-safe access to configuration attributes within step implementations.
- Integrate logging into steps, so each step has an optional logger to record its actions.
- Keep the base step abstract and minimal—only define structure and common functionality, deferring actual execution logic to subclasses.

## Implementation Considerations

- **StepConfig (Pydantic Model)**: Define a `StepConfig` class as a subclass of `BaseModel`. This serves as a base for all configurations. By default, it has no predefined fields (each step will define its own fields by extending this model). Using Pydantic ensures that step configurations are validated and parsed (e.g., types are enforced, missing fields are caught) when constructing the step.
- **Generic ConfigType**: Use a `TypeVar` and generic class definition (`BaseStep[ConfigType]`) so that each concrete step class can specify what config type it expects. For instance, a `PrintStep` could be `BaseStep[PrintConfig]`. This allows the step implementation to access `self.config` with the correct type.
- **BaseStep Class**:
  - Inherit from `ABC` to indicate it's abstract and cannot be instantiated on its own.
  - Inherit from `Generic[ConfigType]` to support the generic config typing.
  - Provide an `__init__` that stores the `config` (of type ConfigType) and sets up a logger. The logger default can be a module or application logger (e.g., named "RecipeExecutor") if none is provided. This logger is used by steps to log their internal operations.
  - The `__init__` should log a debug message indicating the class name and config with which the step was initialized. This is useful for tracing execution in logs.
  - Declare an abstract `execute(context: ContextProtocol) -> None` method. This is the core contract: every concrete step must implement this method. The use of `ContextProtocol` in the signature ensures that steps are written against the interface of context, not a specific implementation, aligning with decoupling philosophy.
  - The abstractmethod should not provide any implementation (aside from possibly a placeholder raise of NotImplementedError, which is a safeguard).
- **ContextProtocol Usage**: By typing the `context` parameter of `execute` as `ContextProtocol`, BaseStep makes it clear that steps should not assume a specific Context class. They just need an object that fulfills the context interface (get/set/etc.). The actual context passed at runtime will be the concrete Context, which is fine because it implements that protocol.
- **Logging in Steps**: Steps can use `self.logger` to log debug or info messages. By default, if the step author does nothing, a logger is available. This logger is typically passed in by the Executor (it passes its own logger to step constructors). If the Executor passes a logger, all step logs become part of the executor's logging output, keeping everything unified.
- **No Execution Logic in BaseStep**: BaseStep should not implement any actual step logic in `execute`—that remains abstract. It may, however, include common utility methods for steps in the future, though currently it does not (keeping things simple).
- **Step Interface Protocol**: The `BaseStep` (and by extension all steps) fulfill the `StepProtocol` as defined in the Protocols component. That protocol essentially mirrors the requirement of the `execute(context)` method. This means that any code expecting a `StepProtocol` can accept a `BaseStep` instance (or subclass).

## Logging

- Debug: BaseStep’s `__init__` logs a message when a step is initialized (including the provided configuration).
- Info: BaseStep itself does not log at info level, but concrete steps may log info messages (e.g., to note high-level actions).
- Error: BaseStep does not handle errors; exceptions in `execute` bubble up to the Executor. Concrete steps should use the logger to record errors and let exceptions propagate unless they can handle them meaningfully.

## Component Dependencies

### Internal Components

- **Protocols** - (Required) Uses `ContextProtocol` for the type of the context parameter in `execute`. Also, by design, `BaseStep` and its subclasses implement `StepProtocol` as defined in the Protocols component.
- **Models** - (Required) Depends on the Pydantic models component (via `BaseModel`) for defining and validating step configuration (StepConfig and its subclasses).

### External Libraries

- **pydantic** - (Required) The Pydantic library is used for defining step configuration classes and performing validation when instantiating them.
- **logging** - (Required) Uses Python's logging module to handle the logger for steps.
- **abc** (Python standard library) - (Required) Used to define `BaseStep` as an abstract base class with the `@abstractmethod` decorator.
- **typing** - (Required) Uses `TypeVar` and `Generic` for typing the BaseStep with its config model.

### Configuration Dependencies

- **None.** The Steps Base component itself has no external configuration. It serves as a framework that other step components use.

## Error Handling

- BaseStep does not implement run-time error handling. It defines the interface and common setup. Any exceptions that occur within a concrete step's `execute` method will propagate up unless handled inside that step.
- If a concrete step fails to implement `execute`, Python's ABC mechanism will prevent instantiation of that step class (TypeError on instantiation for not implementing abstract methods).
- In the unlikely case that `BaseStep.execute` is called (e.g., via `super()` call from a subclass that doesn't override it), it will raise `NotImplementedError`, clearly indicating that the subclass should implement it. This is a safeguard and developmental aid.

## Output Files

- `steps/base.py`

## Future Considerations

- **Additional Base Functionality**: If many steps end up needing common helper functions (for example, to emit standardized log messages or handle common error patterns), such helpers could be added to BaseStep.
- **Async Steps**: In the future, if we introduce asynchronous step execution, we might consider an async version of BaseStep or modifications to allow `execute` to be a coroutine. This would be a significant change requiring careful design.
- **Step Lifecycle Hooks**: Potentially provide hooks like `setup()` or `teardown()` in BaseStep that steps can override for pre- and post-execution logic. Currently, this is not needed.
- **Integration with Executor**: Ensure that any changes here remain compatible with how the Executor instantiates and uses steps. For instance, if we changed the `execute` signature or added new responsibilities to BaseStep, we must update the Protocols and Executor accordingly.


=== File: recipes/recipe_executor/components/steps/create.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/registry/registry_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/execute_recipe/execute_recipe_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/generate_llm/generate_llm_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/parallel/parallel_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/read_files/read_files_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/write_files/write_files_create.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/edit.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/registry/registry_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/execute_recipe/execute_recipe_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/generate_llm/generate_llm_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/parallel/parallel_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/read_files/read_files_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/write_files/write_files_edit.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/executor/executor_docs.md",
      "artifact": "executor_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "execute_recipe",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<EXECUTOR_DOCS>\n{{executor_docs}}\n</EXECUTOR_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_docs.md ===
# ExecuteRecipeStep Component Usage

## Importing

```python
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep, ExecuteRecipeConfig
```

## Configuration

The ExecuteRecipeStep is configured with an ExecuteRecipeConfig:

```python
class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, str] = {}
```

## Step Registration

The ExecuteRecipeStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep

STEP_REGISTRY["execute_recipe"] = ExecuteRecipeStep
```

## Basic Usage in Recipes

The ExecuteRecipeStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/sub_recipe.json"
    }
  ]
}
```

## Context Overrides

You can override specific context values for the sub-recipe execution:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/generate_component.json",
      "context_overrides": {
        "component_name": "Utils",
        "output_dir": "output/components/utils"
      }
    }
  ]
}
```

## Template-Based Values

Both the `recipe_path` and `context_overrides` can include template variables:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/{{recipe_type}}/{{component_id}}.json",
      "context_overrides": {
        "component_name": "{{component_display_name}}",
        "output_dir": "output/components/{{component_id}}"
      }
    }
  ]
}
```

## Recipe Composition

Sub-recipes can be composed to create more complex workflows:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/project_spec.md",
      "artifact": "project_spec"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/parse_project.json",
      "context_overrides": {
        "spec": "{{project_spec}}"
      }
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/generate_components.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/assemble_project.json"
    }
  ]
}
```

## Common Use Cases

**Component Generation**:

```json
{
  "type": "execute_recipe",
  "recipe_path": "recipes/generate_component.json",
  "context_overrides": {
    "component_id": "utils",
    "component_name": "Utils Component"
  }
}
```

**Template-Based Recipes**:

```json
{
  "type": "execute_recipe",
  "recipe_path": "recipes/component_template.json",
  "context_overrides": {
    "template_type": "create",
    "component_id": "{{component_id}}"
  }
}
```

**Multi-Step Workflows**:

```json
{
  "type": "execute_recipe",
  "recipe_path": "recipes/workflow/{{workflow_name}}.json"
}
```

## Important Notes

- The sub-recipe receives the **same context object** as the parent recipe (the shared context implements ContextProtocol)
- Context overrides are applied **before** sub-recipe execution
- Changes made to the context by the sub-recipe persist after it completes
- Template variables in both `recipe_path` and `context_overrides` are resolved before execution
- Sub-recipes can execute their own sub-recipes (nested execution)


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/execute_recipe.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/execute_recipe/execute_recipe_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_spec.md ===
# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler modules, following the building-block inspired approach to recipe construction.

## Core Requirements

- Execute sub-recipes from a specified file path
- Share the current execution context with sub-recipes
- Support context overrides for sub-recipe execution
- Apply template rendering to recipe paths and context overrides
- Include appropriate logging for sub-recipe execution
- Follow a minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Logging

- Debug: None
- Info: Log the path of the sub-recipe being executed at both the start and end of execution

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Leverages ContextProtocol for context sharing, ExecutorProtocol for execution, and StepProtocol for the step interface contract
- **Step Interface** – (Required) Implements the step execution interface (via the StepProtocol)
- **Context** – (Required) Shares data via a context object implementing the ContextProtocol between the main recipe and sub-recipes
- **Executor** – (Required) Uses an executor implementing ExecutorProtocol to run the sub-recipe
- **Utils** – (Required) Uses render_template for dynamic content resolution in paths and context overrides

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include the sub-recipe path in error messages for debugging

## Output Files

- `steps/execute_recipe.py`

## Future Considerations

- Support providing recipe content directly in configuration
- Context isolation options for sub-recipes
- Result mapping from sub-recipes back to parent recipes
- Conditional sub-recipe execution


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/llm/llm_docs.md",
      "artifact": "llm_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "generate_llm",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<LLM_DOCS>\n{{llm_docs}}\n</LLM_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_docs.md ===
# GenerateWithLLMStep Component Usage

## Importing

```python
from recipe_executor.steps.generate_llm import GenerateWithLLMStep, GenerateLLMConfig
```

## Configuration

The GenerateWithLLMStep is configured with a GenerateLLMConfig:

```python
class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider:model_name format).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str
```

## Step Registration

The GenerateWithLLMStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.generate_llm import GenerateWithLLMStep

STEP_REGISTRY["generate"] = GenerateWithLLMStep
```

## Basic Usage in Recipes

The GenerateWithLLMStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate Python code for a utility that: {{requirements}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generation_result"
    }
  ]
}
```

## Template-Based Prompts

The prompt can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md",
      "artifact": "spec"
    },
    {
      "type": "generate",
      "prompt": "You are an expert Python developer. Based on the following specification, generate code for a component:\n\n{{spec}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Model Selection

The model identifier can also use template variables:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code based on: {{spec}}",
      "model": "{{model_provider|default:'openai'}}:{{model_name|default:'o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Artifact Keys

The artifact key can be templated to create dynamic storage locations:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code for: {{component_name}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "{{component_name}}_result"
    }
  ]
}
```

## LLM Response Format

The response from `call_llm` is a FileGenerationResult object structure. For example:

```python
# FileGenerationResult structure
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)
```

This result contains a list of generated files (each as a FileSpec with a path and content) and an overall commentary.

## Important Notes

- The artifact key can be dynamic using template variables
- The prompt is rendered using the current context (ContextProtocol) before sending to the LLM
- The model identifier follows the format `"provider:model_name"`
- The LLM response is returned as a FileGenerationResult object (with `files` and `commentary` fields)
- LLM calls may incur costs with the respective provider


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/generate_llm.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/generate_llm/generate_llm_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_spec.md ===
# GenerateWithLLMStep Component Specification

## Purpose

The GenerateWithLLMStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, and storing generation results in the execution context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Call LLMs to generate content
- Store generated results in the context
- Support dynamic artifact key resolution
- Include appropriate logging for LLM operations

## Implementation Considerations

- Use template rendering for dynamic prompt generation
- Support template rendering in model selection
- Allow dynamic artifact key through template rendering
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about LLM requests

## Logging

- Debug: Log when an LLM call is being made (details of the call are handled by the LLM component)
- Info: None

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for context data access and StepProtocol for the step interface (decouples from concrete Context and BaseStep classes)
- **Step Interface** – (Required) Implements the step behavior via StepProtocol
- **Context** – (Required) Uses a context implementing ContextProtocol to retrieve input values and store generation results
- **LLM** – (Required) Uses the LLM component (e.g. call_llm function) to interact with language models
- **Utils** – (Required) Uses render_template for dynamic content resolution in prompts and model identifiers

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls

## Output Files

- `steps/generate_llm.py`

## Future Considerations

- Additional LLM parameters (e.g. temperature, max tokens, etc.)


=== File: recipes/recipe_executor/components/steps/parallel/parallel_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "parallel",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/parallel/parallel_docs.md ===
# ParallelStep Component Usage

The **ParallelStep** component enables the concurrent execution of multiple sub-steps within a recipe. It is ideal for improving performance when independent tasks can be executed in parallel.

## Importing

Import the ParallelStep and its configuration:

```python
from recipe_executor.steps.parallel import ParallelStep, ParallelConfig
```

## Configuration

The ParallelStep is configured via a ParallelConfig object. This configuration defines the list of sub-steps to run concurrently, along with optional settings for controlling concurrency.

```python
class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc).
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default = 0 means no explicit limit (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay (all allowed substeps start immediately).
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0
```

## Step Registration

To enable the use of ParallelStep in recipes, register it in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.parallel import ParallelStep

STEP_REGISTRY["parallel"] = ParallelStep
```

## Basic Usage in Recipes

The ParallelStep allows you to run multiple steps concurrently. Sub-steps are defined within a dedicated `substeps` array.

### Example Recipe (JSON)

```json
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "recipes/subtask_a.json",
          "context_overrides": {
            "input_data": "{{shared_input}}"
          }
        },
        {
          "type": "execute_recipe",
          "recipe_path": "recipes/subtask_b.json",
          "context_overrides": {
            "input_data": "{{shared_input}}"
          }
        }
      ],
      "max_concurrency": 2,
      "delay": 1
    }
  ]
}
```

## Integration with Other Steps

The ParallelStep is designed to integrate seamlessly with the rest of your recipe:

- **Copies of Context:** All sub-steps are provided a copy of the same context (the shared context implements ContextProtocol), enabling them to read from common data.
- **Independent Execution:** Use ParallelStep only for tasks that do not depend on each other nor write back to context beyond the parallel block’s lifecycle, as each cloned context is discarded after the parallel block completes.

## Important Notes

- **Error Handling:** If any sub-step fails, the entire parallel execution aborts. Handle errors within each sub-step to ensure graceful degradation.
- **Resource Constraints:** Adjust `max_concurrency` based on system resources to avoid overwhelming the executor.
- **Delay Between Sub-steps:** Use the `delay` parameter to control the timing of sub-step execution, which can help manage resource contention.


=== File: recipes/recipe_executor/components/steps/parallel/parallel_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/parallel.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/parallel/parallel_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/parallel/parallel_spec.md ===
# ParallelStep Component Specification

## Purpose

The ParallelStep component enables the Recipe Executor to run multiple sub-recipes concurrently within a single step. It improves execution efficiency by parallelizing independent tasks while maintaining isolation between them.

## Core Requirements

- Accept a list of sub-step configurations (each sub-step is an `execute_recipe` step definition)
- Clone the current execution context for each sub-step to ensure isolation
- Execute sub-steps concurrently with a configurable maximum concurrency limit
- Support an optional delay between launching each sub-step
- Wait for all sub-steps to complete before proceeding
- Implement fail-fast behavior: if any sub-step fails, stop launching new ones and report the error

## Implementation Considerations

- Use a ThreadPoolExecutor to manage parallel execution of sub-steps
- Use `Context.clone()` to create independent context copies for each sub-step
- Implement a configurable launch delay (using `time.sleep`) for staggered start times
- Monitor exceptions from each thread and implement fail-fast behavior
- Provide clear logging for sub-step lifecycle events and execution summary
- Manage resources efficiently to prevent memory or thread leaks

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for context management, ExecutorProtocol for parallel execution, and StepProtocol for the step interface
- **Step Interface** – (Required) Adheres to the step execution interface via StepProtocol
- **Context** – (Required) Utilizes a ContextProtocol implementation (e.g. using Context.clone()) to create isolated contexts for each parallel sub-step
- **Step Registry** – (Required) Uses the step registry to instantiate the `execute_recipe` step for each sub-step
- **Executor** – (Required) Uses an Executor implementing ExecutorProtocol to run each sub-recipe in a separate thread
- **Utils** – (Optional) Uses template rendering for sub-step configurations

### External Libraries

- **ThreadPoolExecutor** – (Required) Uses `concurrent.futures.ThreadPoolExecutor` for parallel execution
- **time** – (Optional) Uses `time.sleep` to implement delays between sub-step launches

### Configuration Dependencies

None

## Output Files

- `steps/parallel.py` (ParallelStep implementation)

## Logging

- Debug: Log sub-step start/completion events, thread allocation, and configuration details
- Info: Log start and completion with a summary of the parallel execution (number of steps and success/failure counts)

## Error Handling

- Implement fail-fast behavior when any sub-step encounters an error
- Cancel pending sub-steps if an error occurs
- Include clear error context identifying which sub-step failed
- Ensure proper thread pool shutdown to prevent orphaned threads
- Propagate the original exception with contextual information about the failure

## Future Considerations

- Support arbitrary step types beyond just execute_recipe
- Aggregate results from sub-steps back into the parent context
- Dynamic concurrency control based on system load
- Timeout and isolation options for sub-steps


=== File: recipes/recipe_executor/components/steps/read_files/read_files_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "read_files",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/read_files/read_files_docs.md ===
# ReadFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.read_files import ReadFilesStep, ReadFilesConfig
```

## Configuration

The ReadFilesStep is configured with a ReadFilesConfig:

```python
class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + contents
            - "dict": Store a dictionary with filenames as keys and contents as values
    """
    path: Union[str, List[str]]
    artifact: str
    optional: bool = False
    merge_mode: str = "concat"
```

## Step Registration

The ReadFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_files import ReadFilesStep

STEP_REGISTRY["read_files"] = ReadFilesStep
```

## Basic Usage in Recipes

### Reading a Single File

The ReadFilesStep can be used to read a single file (just like the original `read_file` step):

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

### Reading Multiple Files

You can read multiple files by providing a comma-separated string of paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md,specs/component_docs.md",
      "artifact": "component_specs"
    }
  ]
}
```

You can also read multiple files by providing a list of path strings:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/component_spec.md", "specs/component_docs.md"],
      "artifact": "component_specs",
      "merge_mode": "concat"
    }
  ]
}
```

### Reading Multiple Files as a Dictionary

You can store multiple files as a dictionary with filenames as keys:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/component_spec.md", "specs/component_docs.md"],
      "artifact": "component_specs",
      "merge_mode": "dict"
    }
  ]
}
```

## Template-Based Paths

The `path` parameter can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

Template variables can also be used within list paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": [
        "specs/{{component_id}}_spec.md",
        "specs/{{component_id}}_docs.md"
      ],
      "artifact": "component_files"
    }
  ]
}
```

## Optional Files

You can specify that files are optional. If an optional file doesn't exist, execution will continue:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/required_file.md", "specs/optional_file.md"],
      "artifact": "component_files",
      "optional": true
    }
  ]
}
```

If an optional file is not found:

- For a single file: an empty string is stored in the context
- For multiple files with `merge_mode: "concat"`: the missing file is skipped in the concatenated result
- For multiple files with `merge_mode: "dict"`: an empty string is stored for that file’s key

## Common Use Cases

**Loading Multiple Related Specifications**:

```json
{
  "type": "read_files",
  "path": ["specs/{{component_id}}_spec.md", "specs/{{component_id}}_docs.md"],
  "artifact": "component_files",
  "merge_mode": "concat"
}
```

**Loading Templates with Optional Components**:

```json
{
  "type": "read_files",
  "path": [
    "templates/email_base.txt",
    "templates/email_header.txt",
    "templates/email_footer.txt"
  ],
  "artifact": "email_templates",
  "optional": true,
  "merge_mode": "dict"
}
```

**Dynamic Path Resolution with Multiple Files**:

```json
{
  "type": "read_files",
  "path": [
    "docs/{{project}}/{{component}}/README.md",
    "docs/{{project}}/{{component}}/USAGE.md"
  ],
  "artifact": "documentation",
  "optional": true
}
```

**Command Line Integration**:

You can also supply paths via command-line context values:

```bash
python -m recipe_executor.main recipes/generate.json --context files_to_read="specs/component_a.md,specs/component_b.md"
```

Then in the recipe you can use that context value:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{files_to_read.split(',')|default:'specs/default.md'}}",
      "artifact": "input_files"
    }
  ]
}
```

## Important Notes

- The step uses UTF-8 encoding by default for all files
- When a file is optional and missing, it is handled according to the specified `merge_mode`
- Template variables in all paths are resolved before reading the files
- For backwards compatibility, single-file behavior matches the original `read_file` step
- When using `merge_mode: "dict"`, the keys in the output are the base names of the files (not the full paths)
- All paths support template rendering (including each path in a list)


=== File: recipes/recipe_executor/components/steps/read_files/read_files_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/read_files.py",
      "artifact": "existing_code",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/read_files/read_files_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/read_files/read_files_spec.md ===
# ReadFilesStep Component Specification

## Purpose

The ReadFilesStep component reads one or more files from the filesystem and stores their contents in the execution context. It serves as a foundational step for loading data into recipes (such as specifications, templates, and other input files) with support for both single-file and multi-file operations.

## Core Requirements

- Read a file or multiple files from specified path(s)
- Support input specified as a single path string, a comma-separated string of paths, or a list of path strings
- If a single string is provided, detect commas to determine if it represents multiple paths and split accordingly
- Support template-based path resolution for all paths
- Store all file contents in the context under a single specified key
- Provide flexible content merging options for multi-file reads
- Support optional file handling for cases when files might not exist
- Include appropriate logging and error messages
- Follow a minimal design with clear error handling

## Implementation Considerations

- Render template strings for the `path` parameter before evaluating the input type
- Use template rendering to support dynamic paths for single path, comma-separated paths in one string, and lists of paths
- Handle missing files explicitly with meaningful error messages
- Use consistent UTF-8 encoding for text files
- Implement an `optional` flag to continue execution if files are missing
- For multiple files, provide a way to merge contents (default: concatenate with newlines separating each file’s content)
- Provide a clear content structure when reading multiple files (e.g. a dictionary with filenames as keys)
- Keep the implementation simple and focused on a single responsibility
- For backwards compatibility, preserve the behavior of the original single-file read step

## Logging

- Debug: Log each file path before attempting to read (useful for diagnosing failures)
- Info: Log the successful reading of each file (including its path) and the final storage key used in the context

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for context interactions and StepProtocol for step interface implementation
- **Step Interface** – (Required) Implements the step interface via StepProtocol
- **Context** – (Required) Stores file contents using a context that implements ContextProtocol (artifacts stored under a specified key)
- **Utils** – (Required) Uses render_template for dynamic path resolution

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Raise a FileNotFoundError with a clear message when required files do not exist
- Support the `optional` flag to continue execution (with empty content) if files are missing
- Handle error cases differently for single-file versus multiple-file scenarios
- Log appropriate warnings and information during execution
- When reading multiple files and some are optional, continue processing those files that exist

## Output Files

- `steps/read_files.py`

## Future Considerations

- Directory reading and file glob patterns
- Advanced content merging options
- Additional metadata capture (e.g. file size, timestamps)
- Content transformation or pre-processing options

## Dependency Integration Considerations

None

# ReadFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.read_files import ReadFilesStep, ReadFilesConfig
```

## Configuration

The ReadFilesStep is configured with a ReadFilesConfig:

```python
class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + contents
            - "dict": Store a dictionary with filenames as keys and contents as values
    """
    path: Union[str, List[str]]
    artifact: str
    optional: bool = False
    merge_mode: str = "concat"
```

## Step Registration

The ReadFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_files import ReadFilesStep

STEP_REGISTRY["read_files"] = ReadFilesStep
```

## Basic Usage in Recipes

### Reading a Single File

The ReadFilesStep can be used to read a single file (just like the original `read_file` step):

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

### Reading Multiple Files

You can read multiple files by providing a comma-separated string of paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md,specs/component_docs.md",
      "artifact": "component_specs"
    }
  ]
}
```

You can also read multiple files by providing a list of path strings:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/component_spec.md", "specs/component_docs.md"],
      "artifact": "component_specs",
      "merge_mode": "concat"
    }
  ]
}
```

### Reading Multiple Files as a Dictionary

You can store multiple files as a dictionary with filenames as keys:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/component_spec.md", "specs/component_docs.md"],
      "artifact": "component_specs",
      "merge_mode": "dict"
    }
  ]
}
```

## Template-Based Paths

The `path` parameter can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

Template variables can also be used within list paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": [
        "specs/{{component_id}}_spec.md",
        "specs/{{component_id}}_docs.md"
      ],
      "artifact": "component_files"
    }
  ]
}
```

## Optional Files

You can specify that files are optional. If an optional file doesn't exist, execution will continue:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/required_file.md", "specs/optional_file.md"],
      "artifact": "component_files",
      "optional": true
    }
  ]
}
```

If an optional file is not found:

- For a single file: an empty string is stored in the context
- For multiple files with `merge_mode: "concat"`: the missing file is skipped in the concatenated result
- For multiple files with `merge_mode: "dict"`: an empty string is stored for that file’s key

## Common Use Cases

**Loading Multiple Related Specifications**:

```json
{
  "type": "read_files",
  "path": ["specs/{{component_id}}_spec.md", "specs/{{component_id}}_docs.md"],
  "artifact": "component_files",
  "merge_mode": "concat"
}
```

**Loading Templates with Optional Components**:

```json
{
  "type": "read_files",
  "path": [
    "templates/email_base.txt",
    "templates/email_header.txt",
    "templates/email_footer.txt"
  ],
  "artifact": "email_templates",
  "optional": true,
  "merge_mode": "dict"
}
```

**Dynamic Path Resolution with Multiple Files**:

```json
{
  "type": "read_files",
  "path": [
    "docs/{{project}}/{{component}}/README.md",
    "docs/{{project}}/{{component}}/USAGE.md"
  ],
  "artifact": "documentation",
  "optional": true
}
```

**Command Line Integration**:

You can also supply paths via command-line context values:

```bash
python -m recipe_executor.main recipes/generate.json --context files_to_read="specs/component_a.md,specs/component_b.md"
```

Then in the recipe you can use that context value:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{files_to_read.split(',')|default:'specs/default.md'}}",
      "artifact": "input_files"
    }
  ]
}
```

## Important Notes

- The step uses UTF-8 encoding by default for all files
- When a file is optional and missing, it is handled according to the specified `merge_mode`
- Template variables in all paths are resolved before reading the files
- For backwards compatibility, single-file behavior matches the original `read_file` step
- When using `merge_mode: "dict"`, the keys in the output are the base names of the files (not the full paths)
- All paths support template rendering (including each path in a list)


=== File: recipes/recipe_executor/components/steps/registry/registry_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "registry",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/registry/registry_docs.md ===
# Step Registry Component Usage

## Importing

```python
from recipe_executor.steps.registry import STEP_REGISTRY
```

## Registry Structure

The registry is a simple dictionary that maps step type names to their implementation classes:

```python
# Type definition
from typing import Dict, Type
from recipe_executor.steps.base import BaseStep

# Structure of STEP_REGISTRY
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
}
```

Custom steps can be registered in the same way:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.base import BaseStep
from my_custom_steps import CustomStep

# Register a custom step implementation
STEP_REGISTRY["custom_step"] = CustomStep
```

## Looking Up Steps

The executor uses the registry to look up step classes by type:

```python
# Example of registry usage in executor
from typing import Dict, Any
import logging
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY

def execute_step(step: Dict[str, Any], context: Context, logger: logging.Logger) -> None:
    step_type = step["type"]
    if step_type not in STEP_REGISTRY:
        raise ValueError(f"Unknown step type '{step_type}'")

    step_class = STEP_REGISTRY[step_type]
    step_instance = step_class(step, logger)
    step_instance.execute(context)
```

## Important Notes

- Step type names must be unique across the entire system
- Steps must be registered before the executor tries to use them
- Standard steps are automatically registered when the package is imported
- Custom steps need to be explicitly registered by the user


=== File: recipes/recipe_executor/components/steps/registry/registry_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/registry.py,{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/__init__.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/registry/registry_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/registry/registry_spec.md ===
# Step Registry Component Specification

## Purpose

The Step Registry component provides a central mechanism for registering and looking up step implementations by their type names. It enables the dynamic discovery of step classes during recipe execution.

## Core Requirements

- Provide a simple mapping between step type names and their implementation classes
- Support registration of step implementations from anywhere in the codebase
- Enable the executor to look up step classes by their type name
- Follow a minimal, dictionary-based approach with no unnecessary complexity

## Implementation Considerations

- Use a single, global dictionary to store all step registrations
- Allow steps to register themselves upon import
- Keep the registry structure simple and stateless
- Avoid unnecessary abstractions or wrapper functions

## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

None

### Configuration Dependencies

None

## Output Files

- `steps/registry.py`
- `steps/__init__.py` (details below)

Create the `__init__.py` file in the `steps` directory to ensure it is treated as a package. Steps are registered in the steps package `__init__.py`:

```python
# In recipe_executor/steps/__init__.py
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register steps by updating the registry
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})
```

## Future Considerations

- Dynamic loading of external step implementations
- Step metadata and documentation


=== File: recipes/recipe_executor/components/steps/write_files/write_files_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_docs.md",
      "artifact": "models_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "write_files",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/write_files/write_files_docs.md ===
# WriteFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.write_files import WriteFilesStep, WriteFilesConfig
```

## Configuration

The WriteFilesStep is configured with a WriteFilesConfig:

```python
class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        artifact: Name of the context key holding a FileGenerationResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """
    artifact: str
    root: str = "."
```

## Step Registration

The WriteFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

STEP_REGISTRY["write_files"] = WriteFilesStep
```

## Basic Usage in Recipes

The WriteFilesStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "output/project"
    }
  ]
}
```

## Supported Context Values

The WriteFilesStep can work with two types of artifacts in the context:

### FileGenerationResult

```python
from recipe_executor.models import FileGenerationResult, FileSpec

# Example of generating a FileGenerationResult
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)

# Store in context
context["generated_code"] = result
```

### List of FileSpec objects

```python
from recipe_executor.models import FileSpec

# Example of generating a list of FileSpec objects
files = [
    FileSpec(path="src/main.py", content="print('Hello, world!')"),
    FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
]

# Store in context
context["generated_files"] = files
```

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "output/{{project_name}}"
    }
  ]
}
```

File paths within the FileSpec objects can also contain templates:

```python
FileSpec(
    path="{{component_name}}/{{filename}}.py",
    content="# Generated code for {{component_name}}"
)
```

## Common Use Cases

**Writing Generated Code**:

```json
{
  "type": "write_files",
  "artifact": "generated_code",
  "root": "output/src"
}
```

**Project-Specific Output**:

```json
{
  "type": "write_files",
  "artifact": "project_files",
  "root": "output/{{project_name}}"
}
```

**Component Generation**:

```json
{
  "type": "write_files",
  "artifact": "component_result",
  "root": "output/components"
}
```

## Important Notes

- Directories are created automatically if they don’t exist
- Files are overwritten without confirmation if they already exist
- All paths are rendered using template variables from the context (ContextProtocol)
- File content is written using UTF-8 encoding
- Both FileGenerationResult and List[FileSpec] input formats are supported


=== File: recipes/recipe_executor/components/steps/write_files/write_files_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/write_files.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/write_files/write_files_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/write_files/write_files_spec.md ===
# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both FileGenerationResult and list of FileSpec formats as input
- Create directories as needed for file paths
- Apply template rendering to file paths
- Provide appropriate logging for file operations
- Follow a minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (FileGenerationResult or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically if they do not exist
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Logging

- Debug: Log each file’s path and content before writing (to help debug failures)
- Info: Log the successful writing of each file (including its path) and the size of its content

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for reading artifact data and StepProtocol for step interface compliance
- **Step Interface** – (Required) Follows the step interface via StepProtocol
- **Context** – (Required) Retrieves file content from a context implementing ContextProtocol
- **Models** – (Required) Uses FileGenerationResult and FileSpec models for content structure
- **Utils** – (Required) Uses render_template for dynamic path resolution

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the specified artifact exists in context
- Ensure the artifact contains a valid FileGenerationResult or list of FileSpec objects
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Output Files

- `steps/write_files.py`

## Future Considerations

- “Dry-run” mode that logs intended writes without performing them


=== File: recipes/recipe_executor/components/utils/utils_create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/protocols/protocols_docs.md",
      "artifact": "protocols_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/build_component.json",
      "context_overrides": {
        "component_id": "utils",
        "component_path": "/",
        "existing_code": "{{existing_code}}",
        "additional_content": "<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<PROTOCOLS_DOCS>\n{{protocols_docs}}\n</PROTOCOLS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/utils/utils_docs.md ===
# Utils Component Usage

## Importing

```python
from recipe_executor.utils import render_template
```

## Template Rendering

The Utils component provides a `render_template` function that renders Liquid templates using values from a context object implementing the ContextProtocol:

```python
def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

Basic usage example:

```python
from recipe_executor.context import Context
from recipe_executor.utils import render_template

# Create a context with some values
context: ContextProtocol = Context(artifacts={"name": "World", "count": 42})

# Render a template string using the context
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Liquid syntax. Here are some common features:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains nested dictionaries)
template = "Author: {{book.author}}"
```

### Conditionals

```python
template = "{% if user_count > 0 %}Users: {{user_count}}{% else %}No users{% endif %}"
```

### Loops

```python
template = "{% for item in items %}Item: {{item}}{% endfor %}"
```


=== File: recipes/recipe_executor/components/utils/utils_edit.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/utils.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/utils/utils_spec.md ===
# Utils Component Specification

## Purpose

The Utils component provides general utility functions for recipes, primarily focused on template rendering. It offers a way to render strings with template variables against the execution context, enabling dynamic content generation in recipes.

## Core Requirements

- Render strings as templates using context data
- Utilize a standard templating engine (Liquid) for consistency
- Ensure that all context values are accessible to the templates
- Handle errors in template rendering gracefully
- Keep the utility functions stateless and reusable

## Implementation Considerations

- Use the Liquid templating library directly without unnecessary abstraction
- Convert context values to strings before rendering to prevent type errors
- Handle rendering errors gracefully with clear error messages
- Keep the implementation stateless and focused on its single responsibility

## Logging

- Debug: Log the template text being rendered and the context keys used
- Info: None

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol definition for context data access
- **Context** – (Required) Uses a context implementing ContextProtocol for accessing artifacts during template rendering

### External Libraries

- **Liquid** – (Required) Uses the Liquid templating engine for rendering (`python-liquid`)
- **json** – (Required) Uses the built-in json module for handling dictionary-to-string conversions (when needed)

### Configuration Dependencies

None

## Error Handling

- Wrap template rendering in try/except blocks
- Provide specific error messages indicating the source of template failures
- Propagate rendering errors with useful context information

## Output Files

- `utils.py`

## Future Considerations

- Support custom template filters or tags
- Support template partials or includes
- Template validation or linting before rendering


=== File: recipes/recipe_executor/create.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/logger/logger_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/executor/executor_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/main/main_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/protocols/protocols_create.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/create.json"
    }
  ]
}


=== File: recipes/recipe_executor/edit.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/logger/logger_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/executor/executor_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/main/main_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/protocols/protocols_edit.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/create.json"
    }
  ]
}


=== File: recipes/recipe_executor/fast_create.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/logger/logger_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/executor/executor_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/main/main_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/protocols/protocols_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/llm/llm_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/azure_openai/azure_openai_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/registry/registry_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/execute_recipe/execute_recipe_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/generate_llm/generate_llm_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/parallel/parallel_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/read_files/read_files_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/write_files/write_files_create.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/fast_edit.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/context/context_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/logger/logger_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/models/models_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/utils/utils_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/executor/executor_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/main/main_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/protocols/protocols_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/llm/llm_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/llm_utils/azure_openai/azure_openai_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/registry/registry_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/base/base_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/execute_recipe/execute_recipe_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/generate_llm/generate_llm_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/parallel/parallel_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/read_files/read_files_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/components/steps/write_files/write_files_edit.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/utils/build_component.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components{{component_path}}{% if component_path != '/' %}/{% endif %}{{component_id}}/{{component_id}}_spec.md",
      "artifact": "spec"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/components{{component_path}}{% if component_path != '/' %}/{% endif %}{{component_id}}/{{component_id}}_docs.md",
      "artifact": "usage_docs",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes/recipe_executor'}}/utils/generate_code.json",
      "context_overrides": {
        "model": "{{model|default:'openai:o3-mini'}}",
        "output_root": "{{output_root|default:'output'}}",
        "output_path": "recipe_executor{{component_path}}",
        "language": "{{language|default:'python'}}",
        "spec": "{{spec}}",
        "usage_docs": "{{usage_docs}}",
        "existing_code": "{{existing_code}}",
        "additional_content": "{{additional_content}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/utils/generate_code.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "read_files",
      "path": "{{recipe_root|default:'recipes/recipe_executor'}}/ai_context/DEV_GUIDE_FOR_PYTHON.md",
      "artifact": "dev_guide",
      "optional": true
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer. Based on the following specification{% if existing_code %} and existing code{% endif %}, generate python code for the {{component_id}} component of a larger project.\n\nSpecification:\n{{spec}}\n\n{% if existing_code %}<EXISTING_CODE>\n{{existing_code}}\n</EXISTING_CODE>\n\n{% endif %}{% if usage_docs %}<USAGE_DOCUMENTATION>\n{{usage_docs}}\n</USAGE_DOCUMENTATION>\n\n{% endif %}{% if additional_content %}{{additional_content}}\n\n{% endif %}Ensure the code follows the specification exactly, implements all required functionality, and adheres to the implementation philosophy described in the tags. Include appropriate error handling and type hints. The implementation should be minimal but complete.\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<DEV_GUIDE>{{dev_guide}}</DEV_GUIDE>\n\nGenerate the appropriate file(s): {{output_path|default:'/'}}{% if component_path != '/' %}/{% endif %}{{component_id}}.<ext>, etc.\n\n",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_code"
    },
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


