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
