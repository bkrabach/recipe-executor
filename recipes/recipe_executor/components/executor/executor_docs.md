# Executor Component Usage

## Importing

```python
from recipe_executor.executor import Executor
```

## Basic Usage

The Executor has a single primary method: `execute()`. This method loads and runs a recipe with a given context:

```python
# Method signature
def execute(
    self,
    recipe: str | Dict[str, Any],
    context: Context,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Execute a recipe with the given context.

    Args:
        recipe: Recipe to execute, can be a file path, JSON string, or dictionary
        context: Context instance to use for execution
        logger: Optional logger to use, creates a default one if not provided

    Raises:
        ValueError: If recipe format is invalid or step execution fails
        TypeError: If recipe type is not supported
    """
```

Examples:

```python
# Create context and executor
context = Context()
executor = Executor()

# Execute a recipe from a file
executor.execute("path/to/recipe.json", context)

# Or from a JSON string
json_string = '{"steps": [{"type": "read_file", "path": "example.txt", "artifact": "content"}]}'
executor.execute(json_string, context)

# Or from a dictionary
recipe_dict: Dict[str, List[Dict[str, Any]]] = {
    "steps": [
        {"type": "read_file", "path": "example.txt", "artifact": "content"}
    ]
}
executor.execute(recipe_dict, context)
```

## Recipe Structure

The recipe structure must contain a "steps" key, which is a list of step definitions. Each step must have a "type" field that matches a registered step type. The step type determines how the step is executed.

### Example Recipe

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "input.txt",
      "artifact": "input_content"
    },
    {
      "type": "generate",
      "prompt": "Generate based on: {{input_content}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generation_result"
    }
  ]
}
```

```python
# Example of a recipe as a dictionary
recipe_dict = {
    "steps": [
        {
            "type": "read_file",
            "path": "input.txt",
            "artifact": "input_content"
        },
        {
            "type": "generate",
            "prompt": "Generate based on: {{input_content}}",
            "model": "{{model|default:'openai:o3-mini'}}",
            "artifact": "generation_result"
        }
    ]
}
```

## Custom Logging

You can provide a custom logger to the executor:

```python
import logging

logger = logging.getLogger("my_custom_logger")
logger.setLevel(logging.DEBUG)

executor.execute(recipe, context, logger=logger)
```

## Integration with Steps

The executor uses the Step Registry to instantiate steps based on their type:

```python
# Each step in a recipe must have a "type" field:
step: Dict[str, Any] = {
    "type": "read_file",  # Must match a key in STEP_REGISTRY
    "path": "input.txt",
    "artifact": "content"
}
```

## Important Notes

1. Recipes must contain valid steps with "type" fields
2. All step types must be registered in the STEP_REGISTRY before use
3. Each step receives the same context object
4. Execution is sequential by default
