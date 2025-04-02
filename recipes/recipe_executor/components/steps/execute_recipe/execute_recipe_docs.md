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

Both the recipe path and context overrides can include template variables:

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
      "type": "read_file",
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

## Implementation Details

The ExecuteRecipeStep works by:

1. Rendering the recipe path with the current context
2. Applying context overrides (also rendered with the current context)
3. Creating a Executor instance
4. Executing the sub-recipe with the modified context

```python
def execute(self, context: Context) -> None:
    # Merge any context overrides into the current context
    if hasattr(self.config, "context_overrides") and self.config.context_overrides:
        for key, value in self.config.context_overrides.items():
            context[key] = render_template(value, context)

    # Render the recipe path
    recipe_path = render_template(self.config.recipe_path, context)

    # Verify recipe exists
    if not os.path.exists(recipe_path):
        raise FileNotFoundError(f"Sub-recipe file not found: {recipe_path}")

    # Log sub-recipe execution
    self.logger.info(f"Executing sub-recipe: {recipe_path}")

    # Execute the sub-recipe
    executor = Executor()
    executor.execute(recipe=recipe_path, context=context, logger=self.logger)

    # Log completion
    self.logger.info(f"Completed sub-recipe: {recipe_path}")
```

## Error Handling

The ExecuteRecipeStep can raise several types of errors:

```python
try:
    execute_recipe_step.execute(context)
except FileNotFoundError as e:
    # Sub-recipe file not found
    print(f"File error: {e}")
except ValueError as e:
    # Recipe format or execution errors
    print(f"Recipe error: {e}")
```

## Common Use Cases

1. **Component Generation**:

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

2. **Template-Based Recipes**:

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

3. **Multi-Step Workflows**:
   ```json
   {
     "type": "execute_recipe",
     "recipe_path": "recipes/workflow/{{workflow_name}}.json"
   }
   ```

## Important Notes

1. The sub-recipe receives the same context object as the parent recipe
2. Context overrides are applied before sub-recipe execution
3. Changes made to the context by the sub-recipe persist after it completes
4. Template variables in both recipe_path and context_overrides are resolved before execution
5. Sub-recipes can execute their own sub-recipes (nested execution)
