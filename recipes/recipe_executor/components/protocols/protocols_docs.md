# Protocols Component Usage

The Protocols component provides **interface definitions** for key parts of the Recipe Executor system. By defining formal contracts (`Protocol` classes) for the `Executor`, `Context`, and `Step`, this component decouples implementations from each other and serves as the single source of truth for how components interact. All components that implement or use these interfaces should refer to the `Protocols` component to ensure consistency. Where the concrete implementations are needed, consider importing them inside the method or class that requires them, rather than at the top of the file. This helps to prevent circular imports and keeps the code clean.

## Provided Interfaces

### `ContextProtocol`

The `ContextProtocol` defines the interface for the context object used throughout the Recipe Executor system. It specifies methods for accessing, modifying, and managing context data. This includes standard dictionary-like operations (like `__getitem__`, `__setitem__`, etc.) as well as additional methods like `clone`, `dict`, and `json` for deep copying and serialization. In addition, it provides methods for managing configuration data, such as `get_config` and `set_config`.

```python
from typing import Protocol, Dict, Any, Iterator
class ContextProtocol(Protocol):
    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __contains__(self, key: str) -> bool:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def clone(self) -> "ContextProtocol":
        ...

    def dict(self) -> Dict[str, Any]:
        ...

    def json(self) -> str:
        ...

    def keys(self) -> Iterator[str]:
        ...

    def get_config(self) -> Dict[str, Any]:
        ...

    def set_config(self, config: Dict[str, Any]) -> None:
        ...
```

### `StepProtocol`

The `StepProtocol` defines the interface for steps within a recipe. Each step must implement an `execute` method that takes a context (any `ContextProtocol` implementation) and performs its designated action. This allows for a consistent way to execute steps, regardless of their specific implementations.

```python
from typing import Protocol
class StepProtocol(Protocol):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        ...

    def execute(self, context: ContextProtocol) -> None:
        ...
```

### `ExecutorProtocol`

The `ExecutorProtocol` defines the interface for the executor component, which is responsible for executing recipes. It specifies an `execute` method that takes a recipe (which can be a string, path, or a Recipe object) and a context. This allows the executor to run recipes in a consistent manner, regardless of their specific implementations.

```python
from typing import Protocol
from recipe_executor.models import Recipe

class ExecutorProtocol(Protocol):
    def __init__(self, logger: logging.Logger) -> None:
        ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None:
        ...
```

## How to Use These Protocols

Developers should **import the protocol interfaces** when writing type hints or designing new components. For example, to annotate variables or function parameters:

```python
from recipe_executor import Executor, Context
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol

context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor(logger)
executor.execute("path/to/recipe.json", context)
```

In this example, `Context` is the concrete implementation provided by the system (which implements `ContextProtocol`), and `Executor` is the concrete executor implementing `ExecutorProtocol`. By annotating them as `ContextProtocol` and `ExecutorProtocol`, we emphasize that our code relies only on the defined interface, not a specific implementation. This is optional for running the code (the system will work with or without the annotations), but it is useful for clarity and static type checking.

```python
from recipe_executor.protocols import ContextProtocol, ExecutorProtocol

class MyCustomExecutor(ExecutorProtocol):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(self, recipe: str, context: ContextProtocol) -> None:
        # Custom implementation
        pass
```

In this example, `MyCustomExecutor` implements the `ExecutorProtocol`, ensuring it adheres to the expected interface. This allows it to be used interchangeably with any other executor that also implements `ExecutorProtocol`.

## Implementation Notes for Developers

- **For Implementers**: When creating a new Context or Executor implementation (or any new Step), ensure it provides all methods defined in the corresponding protocol. It is recommended to inherit from the protocol class to ensure compliance. This way, you can be sure that your implementation will work seamlessly with any code that relies on the protocol.

- **For Consumers**: If you use the protocols as the type hints in your code, you can be sure that your code will work with any implementation of the protocol. This allows for greater flexibility and easier testing, as you can swap out different implementations without changing the code that uses them.

- **Decoupling and Cycle Prevention**: By using these protocols, components like the Executor and steps do not need to import each other's concrete classes. This breaks import cycles (for example, steps can call executor functionality through `ExecutorProtocol` without a direct import of the Executor class). The Protocols component thus centralizes interface knowledge: it owns the definitions of `execute` methods and context operations that others rely on.

All developers and AI recipes should reference **this protocols documentation** when implementing or using components. This ensures that all components are consistent and adhere to the same interface definitions, enables decoupling, and prevents import cycles. It also allows for easier testing and swapping of implementations, as all components can be treated as interchangeable as long as they adhere to the defined protocols.
