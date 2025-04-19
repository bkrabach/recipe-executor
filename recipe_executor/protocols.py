"""
Protocols Component
-------------------

Defines protocols (interface contracts) for core components of the Recipe Executor system. These
enable loose coupling and prevent circular import dependencies. For usage and rationale, see
`protocols_docs.md`.
"""
from typing import (
    Protocol,
    runtime_checkable,
    Any,
    Dict,
    Iterator,
    Union,
)
import logging
from pathlib import Path

# Import only for type hints; concrete import in function signatures avoids cyclical dependencies.
from recipe_executor.models import Recipe


@runtime_checkable
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


@runtime_checkable
class StepProtocol(Protocol):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        ...

    async def execute(self, context: ContextProtocol) -> None:
        ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    def __init__(self, logger: logging.Logger) -> None:
        ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None:
        ...
