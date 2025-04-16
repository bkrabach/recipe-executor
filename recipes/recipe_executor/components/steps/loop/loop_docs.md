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
        items: Key in the context containing the collection to iterate over.
        item_key: Key to use when storing the current item in each iteration's context.
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error (default: True).
    """

    items: str
    item_key: str
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True
```

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
      "items": "components",
      "item_key": "component",
      "substeps": [
        {
          "type": "generate",
          "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
          "model": "{{model}}",
          "artifact": "component_questions"
        },
        {
          "type": "write_files",
          "artifact": "component_questions",
          "root": "{{output_dir}}/components/{{component.id}}"
        }
      ],
      "result_key": "processed_components"
    }
  ]
}
```

## How It Works

For each iteration:

1. The LoopStep clones the parent context to create an isolated execution environment
2. It places the current item in the cloned context using the `item_key`
3. It executes all specified steps using the cloned context
4. After execution, it extracts the result from the context (using the same `item_key`)
5. The result is added to a collection that will be stored in the parent context under `result_key`

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
  "items": "components",
  "item_key": "component",
  "substeps": [
    {
      "type": "generate",
      "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
      "model": "{{model}}",
      "artifact": "component_questions"
    },
    {
      "type": "write_files",
      "artifact": "component_questions",
      "root": "output/{{component.id}}"
    }
  ],
  "result_key": "processed_components"
}
```

### Processing Files from a Directory

```json
{
  "type": "loop",
  "items": "code_files",
  "item_key": "file",
  "substeps": [
    {
      "type": "read_files",
      "path": "{{file.path}}",
      "artifact": "file_content"
    },
    {
      "type": "generate",
      "prompt": "Analyze this code file:\n{{file_content}}",
      "model": "{{model}}",
      "artifact": "file_analysis"
    }
  ],
  "result_key": "analyzed_files"
}
```

### Transforming an Array

```json
{
  "type": "loop",
  "items": "input_data",
  "item_key": "item",
  "substeps": [
    {
      "type": "generate",
      "prompt": "Transform this data item: {{item}}\nIndex: {{__index}}",
      "model": "{{model}}",
      "artifact": "transformed_item"
    }
  ],
  "result_key": "transformed_data"
}
```

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
