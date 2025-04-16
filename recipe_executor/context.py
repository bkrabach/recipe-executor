import copy
import json
from typing import Any, Dict, Iterator, Optional

# Import the ContextProtocol type only for type checking and compliance.
# Avoid circular imports by importing ContextProtocol inside functions where absolutely necessary.
try:
    from recipe_executor.protocols import ContextProtocol
except ImportError:
    ContextProtocol = object  # type: ignore


class Context:
    """
    Context component: shared state (artifacts + config) for Recipe Executor.
    Behaves like a dict for artifacts, with separate .config attribute.
    Implements ContextProtocol interface.
    """

    __slots__ = ("_artifacts", "config")

    def __init__(
        self,
        artifacts: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    # --- Dict-like interface for artifacts ---
    def __getitem__(self, key: str) -> Any:
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self._artifacts:
            del self._artifacts[key]
            return
        raise KeyError(f"Key '{key}' not found in Context.")

    def __contains__(self, key: str) -> bool:
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Return an iterator over a static list of the current keys
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        # Explicit keys() method, yields keys as a static snapshot.
        return iter(list(self._artifacts.keys()))

    def get(self, key: str, default: Any = None) -> Any:
        return self._artifacts.get(key, default)

    # --- Cloning, serialization, configuration access ---
    def clone(self) -> "Context":
        return Context(
            artifacts=copy.deepcopy(self._artifacts),
            config=copy.deepcopy(self.config),
        )

    def dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._artifacts)

    def json(self) -> str:
        return json.dumps(self._artifacts, default=str)

    # --- Protocol config methods ---
    def get_config(self) -> Dict[str, Any]:
        return self.config

    def set_config(self, config: Dict[str, Any]) -> None:
        self.config = copy.deepcopy(config)


# For mypy and protocol compliance
ContextProtocol.register(Context)  # type: ignore
