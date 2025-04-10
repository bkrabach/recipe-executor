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
