# Steps Base Component Specification

## Purpose

The Steps Base component defines the foundational classes and interfaces for all step implementations in the Recipe Executor system. It establishes a common structure and contract for steps, ensuring consistent behavior and seamless integration with the executor and context.

## Core Requirements

- Provide a base class (`BaseStep`) that all step classes will inherit from.
- Provide a base configuration model class (`StepConfig`) using Pydantic for validation of step-specific configuration.
- Enforce a consistent interface for step execution (each step must implement an async `execute(context)` method).
- Utilize generics to allow `BaseStep` to be typed with a specific `StepConfig` subclass for that step, enabling type-safe access to configuration attributes within step implementations.
- Integrate logging into steps, so each step has an optional logger to record its actions.
- Keep the base step minimal—only define structure and common functionality, deferring actual execution logic to subclasses.

## Implementation Considerations

- **StepConfig (Pydantic Model)**: Define a `StepConfig` class as a subclass of `BaseModel`. This serves as a base for all configurations. By default, it has no predefined fields (each step will define its own fields by extending this model). Using Pydantic ensures that step configurations are validated and parsed (e.g., types are enforced, missing fields are caught) when constructing the step.
- **Generic ConfigType**: Use a `TypeVar` and generic class definition (`BaseStep[ConfigType]`) so that each step class can specify what config type it expects. For instance, a `PrintStep` could be `BaseStep[PrintConfig]`. This allows the step implementation to access `self.config` with the correct type.
- **BaseStep Class**:
  - Inherit from `Generic[ConfigType]` to support the generic config typing.
  - Provide an `__init__` that stores the `config` (of type ConfigType) and sets up a logger. The logger default can be a module or application logger (e.g., named "RecipeExecutor") if none is provided. This logger is used by steps to log their internal operations.
  - The `__init__` should log a debug message indicating the class name and config with which the step was initialized. This is useful for tracing execution in logs.
  - Declare a `async execute(context: ContextProtocol) -> None` method. This is the core contract: every step must implement this method as an async method. The use of `ContextProtocol` in the signature ensures that steps are written against the interface of context, not a specific implementation, aligning with decoupling philosophy.
  - `BaseStep` should not provide any implementation (aside from possibly a placeholder raise of NotImplementedError, which is a safeguard).
- **ContextProtocol Usage**: By typing the `context` parameter of `execute` as `ContextProtocol`, BaseStep makes it clear that steps should not assume a specific Context class. They just need an object that fulfills the context interface (get/set/etc.). The actual context passed at runtime will be the standard `Context` class, but this allows for flexibility in testing or future changes.
- **Logging in Steps**: Steps can use `self.logger` to log debug or info messages. By default, if the step author does nothing, a logger is available. This logger is typically passed in by the Executor (it passes its own logger to step constructors). If the Executor passes a logger, all step logs become part of the executor's logging output, keeping everything unified.
- **No Execution Logic in BaseStep**: BaseStep should not implement any actual step logic in `execute`. It may, however, include common utility methods for steps in the future, though currently it does not (keeping things simple).
- **Step Interface Protocol**: The `BaseStep` (and by extension all steps) fulfill the `StepProtocol` as defined in the Protocols component. That protocol essentially mirrors the requirement of the `execute(context)` method. This means that any code expecting a `StepProtocol` can accept a `BaseStep` instance (or subclass).

## Logging

- Debug: BaseStep’s `__init__` logs a message when a step is initialized (including the provided configuration).
- Info: BaseStep itself does not log at info level, but actual steps may log info messages (e.g., to note high-level actions).
- Error: BaseStep does not handle errors; exceptions in `execute` bubble up to the Executor. Actual steps should use the logger to record errors and let exceptions propagate unless they can handle them meaningfully.

## Component Dependencies

### Internal Components

- **Protocols** - (Required) Uses `ContextProtocol` for the type of the context parameter in `execute`. Also, by design, `BaseStep` and its subclasses implement `StepProtocol` as defined in the Protocols component.
- **Models** - (Required) Depends on the Pydantic models component (via `BaseModel`) for defining and validating step configuration (StepConfig and its subclasses).

### External Libraries

- **pydantic** - (Required) The Pydantic library is used for defining step configuration classes and performing validation when instantiating them.
- **logging** - (Required) Uses Python's logging module to handle the logger for steps.
- **asyncio** - (Required) Used for asynchronous execution and coroutine handling.
- **typing** - (Required) Uses `TypeVar` and `Generic` for typing the BaseStep with its config model.

### Configuration Dependencies

- **None.** The Steps Base component itself has no external configuration. It serves as a framework that other step components use.

## Error Handling

- BaseStep does not implement run-time error handling. It defines the interface and common setup. Any exceptions that occur within an actual step's `execute` method will propagate up unless handled inside that step.
- In the unlikely case that `BaseStep.execute` is called (e.g., via `super()` call from a subclass that doesn't override it), it will raise `NotImplementedError`, clearly indicating that the subclass should implement it. This is a safeguard and developmental aid.

## Output Files

- `steps/base.py`

## Future Considerations

- **Additional Base Functionality**: If many steps end up needing common helper functions (for example, to emit standardized log messages or handle common error patterns), such helpers could be added to BaseStep.
- **Step Lifecycle Hooks**: Potentially provide hooks like `async setup()` or `async teardown()` in BaseStep that steps can override for pre- and post-execution logic. Currently, this is not needed.
- **Integration with Executor**: Ensure that any changes here remain compatible with how the Executor instantiates and uses steps. For instance, if we changed the `execute` signature or added new responsibilities to BaseStep, we must update the Protocols and Executor accordingly.
