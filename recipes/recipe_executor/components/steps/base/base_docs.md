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

       async def execute(self, context: ContextProtocol) -> None:
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
