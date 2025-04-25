# LoopStep Component Usage

The **LoopStep** component allows you to iterate over a collection of items and execute specified sub-steps for each item. It is useful for processing lists or arrays of data in a structured manner.

## Importing

Import the LoopStep and its configuration:

```python
from recipe_executor.steps.loop import LoopStep, LoopStepConfig
```

## Configuration

The LoopStep is configured via a `LoopStepConfig` object. This configuration defines the collection to iterate over, the key for the current item, the sub-steps to execute, and how to handle results.

```python
class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Key in the context containing the collection to iterate over. Supports template variable syntax
               with dot notation for accessing nested data structures (e.g., "data.items", "response.results").
        item_key: Key to use when storing the current item in each iteration's context.
        max_concurrency: Maximum number of items to process concurrently.
                         Default = 1 means process items sequentially (no parallelism).
                         n > 1 means process up to n items at a time.
                         0 means no explicit limit (all items may run at once, limited only by system resources).
        delay: Time in seconds to wait between starting each parallel task.
               Default = 0 means no delay (all allowed items start immediately).
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error.
    """

    items: str
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True
```

## Parallel Execution Support

The LoopStep supports parallel processing of items:

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "max_concurrency": 3,  // Process up to 3 items in parallel
    "delay": 0.2,          // Wait 0.2 seconds between starting each task
    "substeps": [...],
    "result_key": "processed_components"
  }
}
```

### Parallel Execution Parameters

- **max_concurrency**: Maximum number of items to process concurrently.

  - `0` (default): Process all items at once (limited only by system resources)
  - `1`: Process items sequentially (no parallelism)
  - `n > 1`: Process up to n items at a time

- **delay**: Time in seconds to wait between starting each parallel task.
  - `0.0` (default): Start all allowed tasks immediately
  - `n > 0`: Add n seconds delay between starting each task

### When to Use Parallel Execution

Parallel execution is most beneficial for loops where:

- Each item's processing is independent of other items
- Processing each item involves significant wait time (e.g., LLM calls, network requests)
- The number of items is large enough to benefit from parallelism

## Step Registration

To enable the use of LoopStep in recipes, register it in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.loop import LoopStep

STEP_REGISTRY["loop"] = LoopStep
```

## Basic Usage in Recipes

The LoopStep allows you to run multiple steps for each item in a collection. Sub-steps are defined within a dedicated `substeps` array.

### Example Recipe (JSON)

```json
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "components",
        "item_key": "component",
        "substeps": [
          {
            "type": "llm_generate",
            "config": {
              "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
              "model": "{{model}}",
              "output_format": "files",
              "output_key": "component_questions"
            }
          },
          {
            "type": "write_files",
            "config": {
              "root": "{{output_dir}}/components/{{component.id}}",
              "files_key": "component_questions"
            }
          }
        ],
        "result_key": "processed_components"
      }
    }
  ]
}
```

## How It Works

For each iteration:

1. The LoopStep renders the `items` path using template rendering to resolve nested paths (e.g., "data.items" becomes the actual array from context["data"]["items"])
2. The LoopStep clones the parent context to create an isolated execution environment
3. It places the current item in the cloned context using the `item_key`
4. It executes all specified steps using the cloned context
5. After execution, it extracts the result from the context (using the same `item_key`)
6. The result is added to a collection that will be stored in the parent context under `result_key`

## Accessing Nested Data

The `items` parameter can reference nested data in the context using dot notation. This is processed using template rendering, similar to other Recipe Executor components:

```json
{
  "type": "loop",
  "config": {
    "items": "data.users.list",
    "item_key": "user",
    "substeps": [...]
  }
}
```

This example would iterate over the array found at `context["data"]["users"]["list"]`.

## Template Variables

Within each iteration, you can reference:

- The current item using the specified `item_key` (e.g., `{{current_component}}`)
- Properties of the current item (e.g., `{{current_component.id}}`)
- The iteration index using `{{__index}}` (for arrays) or key using `{{__key}}` (for objects)
- Other context values from the parent context

## Common Usage Patterns

### Processing Collection of Objects

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "component_questions"
        }
      },
      {
        "type": "write_files",
        "config": {
          "root": "output/{{component.id}}",
          "files_key": "component_questions"
        }
      }
    ],
    "result_key": "processed_components"
  }
}
```

### Processing Files from a Directory

```json
{
  "type": "loop",
  "config": {
    "items": "code_files",
    "item_key": "file",
    "substeps": [
      {
        "type": "read_files",
        "config": {
          "path": "{{file.path}}",
          "content_key": "file_content"
        }
      },
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Analyze this code file:\n{{file_content}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "file_analysis"
        }
      }
    ],
    "result_key": "analyzed_files"
  }
}
```

### Transforming an Array

```json
{
  "type": "loop",
  "config": {
    "items": "input_data",
    "item_key": "item",
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Transform this data item: {{item}}\nIndex: {{__index}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "transformed_item"
        }
      }
    ],
    "result_key": "transformed_data"
  }
}
```

### Parallel Processing Example

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "max_concurrency": 5,
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Generate a blueprint for component: {{component.name}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "blueprint"
        }
      },
      {
        "type": "write_files",
        "config": {
          "files_key": "blueprint",
          "root": "{{output_dir}}/components/{{component.id}}"
        }
      }
    ],
    "result_key": "processed_blueprints"
  }
}
```

In this example, up to 5 components will be processed simultaneously, each generating and writing a blueprint. This can significantly reduce execution time for LLM-intensive operations across multiple items.

## Error Handling

By default, the LoopStep will stop processing on the first error (`fail_fast: true`). You can change this behavior:

```json
{
  "type": "loop",
  "items": "components",
  "item_key": "component",
  "substeps": [...],
  "result_key": "processed_components",
  "fail_fast": false
}
```

With `fail_fast: false`, the LoopStep will:

- Continue processing remaining items even if some fail
- Include successful results in the output collection
- Log errors for failed items
- Add information about failed items to the `__errors` key in the result collection

## Important Notes

- Each item is processed in isolation with its own context clone
- Changes to the parent context during iteration are not visible to subsequent iterations
- The final result is always a collection, even if only one item is processed
- If the items collection is empty, an empty collection is stored in the result_key
- If a referenced key doesn't exist in the context, an error is raised
- Collection elements can be of any type (objects, strings, numbers, etc.)
- The LoopStep supports both array and object collections
