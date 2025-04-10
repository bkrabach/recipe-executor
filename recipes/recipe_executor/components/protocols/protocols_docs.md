# Protocols Component Usage

The Protocols component provides **interface definitions** for key parts of the Recipe Executor system. By defining formal contracts (`Protocol` classes) for the Executor, Context, and Step, this component decouples implementations from each other and serves as the single source of truth for how components interact. All components that implement or use these interfaces should refer to the Protocols component to ensure consistency.

## Provided Interfaces

### `ContextProtocol`

Defines the interface for context-like objects that hold shared state (artifacts and configuration). It includes dictionary-like methods (`__getitem__`, `__setitem__`, etc.), a `get` method for safe retrieval, an `as_dict` for copying all data, and a `clone` method for deep-copying the entire context. Any context implementation (such as the built-in `Context` class) should fulfill this interface.

### `StepProtocol`

Specifies the interface for an executable step. It declares a single method `execute(context: ContextProtocol) -> None`. All step classes (via the base class or otherwise) are expected to implement this method to perform their task using the provided context. This ensures a consistent entry point for executing any step.

### `ExecutorProtocol`

Describes the interface for recipe executors. It currently defines one primary method: `execute(recipe, context, logger=None) -> None`. An `ExecutorProtocol` implementor (like the concrete `Executor` class) must be able to take a recipe (in various forms) and a context (any `ContextProtocol` implementation) and execute the recipe's steps sequentially. The optional logger parameter allows injection of a logging facility.

## How to Use These Protocols

Developers should **import the protocol interfaces** when writing type hints or designing new components. For example, to annotate variables or function parameters:

```python
from recipe_executor import Executor, Context
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol

context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor()
executor.execute("path/to/recipe.json", context)
```

In this example, `Context()` is the concrete implementation provided by the system (which implements `ContextProtocol`), and `Executor()` is the concrete executor implementing `ExecutorProtocol`. By annotating them as `ContextProtocol` and `ExecutorProtocol`, we emphasize that our code relies only on the defined interface, not a specific implementation. This is optional for running the code (the system will work with or without the annotations), but it is useful for clarity and static type checking.

## Implementation Notes for Developers

- **For Implementers**: When creating a new Context or Executor implementation (or any new Step), ensure it provides all methods defined in the corresponding protocol. You don't need to explicitly subclass the `Protocol`, thanks to Python's structural typing, but documenting that it implements the interface is good practice. The existing classes (`Context`, `Executor`, and all steps via `BaseStep`) already adhere to `ContextProtocol`, `ExecutorProtocol`, and `StepProtocol` respectively.

- **For Consumers**: When writing functions or methods that accept a context or executor, use `ContextProtocol` or `ExecutorProtocol` in the type hints. This way, your code can work with any object that respects the contract, making the system more extensible. For instance, a function could be annotated to accept `context: ContextProtocol` and thus work with the standard `Context` or any future alternative context implementation.

- **Decoupling and Cycle Prevention**: By using these protocols, components like the Executor and steps do not need to import each other's concrete classes. This breaks import cycles (for example, steps can call executor functionality through `ExecutorProtocol` without a direct import of the Executor class). The Protocols component thus centralizes interface knowledge: it owns the definitions of `execute` methods and context operations that others rely on.

All developers and AI recipes should reference **this protocols documentation** and the `protocols.py` definitions when needing to understand or use the interfaces between components. This ensures that the system’s pieces remain loosely coupled and conformant to the agreed contracts.
