import copy
from typing import Any, Dict, Iterator, Optional

from recipe_executor.protocols import ContextProtocol


class Context(ContextProtocol):
    """
    Context component for Recipe Executor system.

    Maintains a store for artifacts and configuration values, and provides a dictionary-like interface
    for accessing and modifying artifacts. Configuration is stored separately in a 'config' attribute.

    Example usage:

        context = Context(artifacts={"input": "data"}, config={"mode": "test"})
        context["result"] = 42
        value = context["result"]
        if "result" in context:
            print(context["result"])

    The clone() method creates a deep copy of both artifacts and configuration, ensuring isolation when needed.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        # Deep copy to ensure caller modifications do not affect internal state
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self._artifacts:
            del self._artifacts[key]
        else:
            raise KeyError(f"Key '{key}' not found in Context.")

    def __contains__(self, key: object) -> bool:
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Return an iterator over a snapshot of the keys
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        """
        Return an iterator of keys in the artifacts store.
        """
        return iter(list(self._artifacts.keys()))

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._artifacts.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts as a dictionary.
        """
        return copy.deepcopy(self._artifacts)

    def clone(self) -> ContextProtocol:
        """
        Create a deep copy of the Context including both artifacts and configuration.
        """
        return Context(artifacts=copy.deepcopy(self._artifacts), config=copy.deepcopy(self.config))


__all__ = ["Context"]
