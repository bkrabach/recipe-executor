# Steps Base Component Specification

## Purpose

The purpose of the Steps Base component is to provide a foundational structure for creating and executing steps in the recipe executor. This component defines the base class for all steps, ensuring that they adhere to a consistent interface and can be easily integrated into the overall execution framework.

## Core Requirements

- Provide a base class (`BaseStep`) that all step classes will inherit from.
- Provide a base configuration model class (`StepConfig`) using Pydantic for validation of step-specific configuration.
- Enforce a consistent interface for step execution (each step must implement an async `execute(context)` method).
- Utilize generics to allow `BaseStep` to be typed with a specific `StepConfig` subclass for that step, enabling type-safe access to configuration attributes within step implementations.
- Integrate logging into steps, so each step has a logger to record its actions.
- Keep the base step minimal—only define structure and common functionality, deferring actual execution logic to subclasses.

## Implementation Considerations

- **StepConfig (Pydantic Model)**: Define a `StepConfig` class as a subclass of `BaseModel`. This serves as a base for all configurations. By default, it has no predefined fields (each step will define its own fields by extending this model). Using Pydantic ensures that step configurations are validated and parsed (e.g., types are enforced, missing fields are caught) when constructing the step.
- **Generic Config Type**: Use a `TypeVar` and generic class definition (`BaseStep[StepConfigType]`) so that each step class can specify what config type it expects. For instance, a `PrintStep` could be `BaseStep[PrintConfig]`. This allows the step implementation to access `self.config` with the correct type.
  - Example: `StepConfigType = TypeVar("StepConfigType", bound=StepConfig)`.
- **BaseStep Class**:
  - Inherit from `Generic[StepConfigType]` to support the generic config typing.
  - Provide an `__init__` that stores the `config` (of type StepConfigType) and a logger. This logger is used by steps to log their internal operations.
  - The `__init__` should log a debug message indicating the class name and config with which the step was initialized. This is useful for tracing execution in logs.
  - Declare a `async execute(context: ContextProtocol) -> None` method. This is the core contract: every step must implement this method as an async method.
  - `BaseStep` should not provide any implementation (aside from possibly a placeholder raise of NotImplementedError, which is a safeguard).
- **Logging in Steps**: Steps can use `self.logger` to log debug or info messages.
- **Step Interface Protocol**: The `BaseStep` (and by extension all steps) fulfill the `StepProtocol` as defined in the Protocols component.

## Logging

- Debug: BaseStep’s `__init__` logs a message when a step is initialized (including the provided configuration).

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for the type of the context parameter in `execute`. Also, by design, `BaseStep` and its subclasses implement `StepProtocol` as defined in the Protocols component.
- **Logger**: Uses the logger for logging messages. The logger is passed to the step during initialization.

### External Libraries

- **typing**: Uses `TypeVar` and `Generic` for typing the BaseStep with its config model.

### Configuration Dependencies

- None

## Error Handling

- BaseStep does not implement run-time error handling. It defines the interface and common setup. Any exceptions that occur within an actual step's `execute` method will propagate up unless handled inside that step.
- In the unlikely case that `BaseStep.execute` is called (e.g., via `super()` call from a subclass that doesn't override it), it will raise `NotImplementedError`, clearly indicating that the subclass should implement it. This is a safeguard and developmental aid.

## Output Files

- `recipe_executor/steps/base.py`
