from typing import Any, Dict, Iterator, Optional, Protocol, Union, runtime_checkable
import logging


@runtime_checkable
class ContextProtocol(Protocol):
    """
    Defines the interface for context-like objects that hold shared state.
    It supports dictionary-like operations and additional utility methods.
    """

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __contains__(self, key: object) -> bool:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def keys(self) -> Iterator[str]:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def as_dict(self) -> Dict[str, Any]:
        ...

    def clone(self) -> 'ContextProtocol':
        """
        Returns a deep copy of the context.
        """
        ...


@runtime_checkable
class StepProtocol(Protocol):
    """
    Protocol for an executable step in a recipe.
    
    The step must implement the execute method which takes a context
    and performs its operations.
    """

    def execute(self, context: ContextProtocol) -> None:
        ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    """
    Protocol for recipe executors.
    
    The executor must be able to execute a recipe given in various formats (string, JSON string, or dict)
    using a provided context and an optional logger. It is expected to raise exceptions on errors.
    """

    def execute(
        self, 
        recipe: Union[str, Dict[str, Any]], 
        context: ContextProtocol, 
        logger: Optional[logging.Logger] = None
    ) -> None:
        ...
