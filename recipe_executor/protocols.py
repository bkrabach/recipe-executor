"""
Protocols Component
-------------------

Defines the core interface protocols for the Recipe Executor system.
Provides standard contracts for Context, Step, and Executor components.
Designed for maximal decoupling and minimalist, structural subtyping via Python's typing.Protocol.
"""

from __future__ import annotations

from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterator,
    Protocol,
    Union,
    runtime_checkable,
)

# Reference to Recipe type as a forward declaration (not imported to avoid dependency cycles)
Recipe = Any  # Typically a class or struct defined elsewhere


@runtime_checkable
class ContextProtocol(Protocol):
    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...

    def __delitem__(self, key: str) -> None: ...

    def __contains__(self, key: str) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __len__(self) -> int: ...

    def get(self, key: str, default: Any = None) -> Any: ...

    def clone(self) -> "ContextProtocol": ...

    def dict(self) -> Dict[str, Any]: ...

    def json(self) -> str: ...

    def keys(self) -> Iterator[str]: ...

    def get_config(self) -> Dict[str, Any]: ...

    def set_config(self, config: Dict[str, Any]) -> None: ...


@runtime_checkable
class StepProtocol(Protocol):
    async def execute(self, context: ContextProtocol) -> None: ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None: ...
