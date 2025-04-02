# Steps Base Component Usage

## Importing

```python
from recipe_executor.steps.base import BaseStep, StepConfig
```

## Basic Structure

The Steps Base component provides two primary classes:

1. `StepConfig` - Base class for step configuration
2. `BaseStep` - Abstract base class for step implementations

These classes are designed to work together using generics for type safety.

## Step Configuration

All step configurations extend the `StepConfig` base class:

```python
class StepConfig(BaseModel):
    """Base class for all step configs. Extend this in each step."""
    pass

# Type variable for generic configuration types
ConfigType = TypeVar("ConfigType", bound=StepConfig)
```

Example of extending StepConfig:

```python
class ReadsFileConfig(StepConfig):
    """Configuration for ReadFilesStep"""
    path: str
    artifact: str
    encoding: str = "utf-8"  # With default value
```

## Base Step Class

The BaseStep is an abstract generic class parameterized by the config type:

```python
class BaseStep(Generic[ConfigType]):
    """
    Base class for all steps. Subclasses must implement `execute(context)`.
    Each step receives a config object and a logger.

    Args:
        config (ConfigType): Configuration for the step
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")

    def execute(self, context: Context) -> None:
        """
        Execute the step with the given context.

        Args:
            context (Context): Context for execution

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Each step must implement the `execute()` method.")
```

## Implementing a Step

To implement a concrete step, create a class that:

1. Extends BaseStep with a specific config type
2. Implements the execute method
3. Takes a dictionary of configuration values in the constructor

Example:

```python
class ExampleStep(BaseStep[ExampleConfig]):
    """Example step implementation."""

    def __init__(self, config: dict, logger=None):
        # Convert dict to the appropriate config type
        super().__init__(ExampleConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Implementation specific to this step
        self.logger.info("Executing example step")

        # Access configuration values
        value = self.config.some_field

        # Do something with the context
        context["result"] = f"Processed {value}"
```

## Step Registration

All step implementations should be registered in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY

# Register the step type
STEP_REGISTRY["example_step"] = ExampleStep
```

## Handling Configuration

The base step handles configuration conversion automatically:

```python
# Step configuration in a recipe
step_config = {
    "type": "example_step",
    "some_field": "value",
    "another_field": 42
}

# In the executor
step_class = STEP_REGISTRY[step_config["type"]]
step_instance = step_class(step_config, logger)

# Configuration is validated through Pydantic
# Access in the step through self.config
```

## Logging

All steps receive a logger in their constructor:

```python
def __init__(self, config: dict, logger=None):
    # If logger is None, it defaults to logging.getLogger("RecipeExecutor")
    super().__init__(ExampleConfig(**config), logger)

def execute(self, context: Context) -> None:
    # Use the logger for various levels
    self.logger.debug("Detailed debug information")
    self.logger.info("Step execution started")
    self.logger.warning("Potential issue detected")
    self.logger.error("Error occurred during execution")
```

## Important Notes

- All step implementations must inherit from BaseStep
- The execute method must be implemented by all subclasses
- Steps should validate their configuration using Pydantic models
- Steps receive and modify a shared Context object
- Steps should use the logger for appropriate messages
