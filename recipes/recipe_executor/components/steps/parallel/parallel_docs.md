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
