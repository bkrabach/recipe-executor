from typing import Protocol, runtime_checkable, Any, Optional, Iterator, Dict, Union
import logging


@runtime_checkable
class ContextProtocol(Protocol):
    """Interface for context objects holding shared state with dictionary-like access."""

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def as_dict(self) -> Dict[str, Any]:
        """Return a copy of the internal state as a dictionary."""
        ...

    def clone(self) -> 'ContextProtocol':
        """Return a deep copy of the context."""
        ...


@runtime_checkable
class StepProtocol(Protocol):
    """Interface for executable steps in the recipe."""

    async def execute(self, context: ContextProtocol) -> None:
        """Execute the step using the provided context."""
        ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    """Interface for recipe executors that run recipes using a given context and optional logger."""

    async def execute(
        self,
        recipe: Union[str, Dict[str, Any]],
        context: ContextProtocol,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Execute a recipe represented as a file path, JSON string, or dictionary using the context.

        Raises:
            Exception: When execution fails.
        """
        ...
