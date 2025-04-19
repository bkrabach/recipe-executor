from typing import Dict, Any, Iterator, Optional
import copy
import json as jsonlib
from recipe_executor.protocols import ContextProtocol

class Context(ContextProtocol):
    def __init__(
        self,
        artifacts: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self._config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        if key not in self._artifacts:
            raise KeyError(f"Key '{key}' not found in Context.")
        return self._artifacts[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        if key not in self._artifacts:
            raise KeyError(f"Key '{key}' not found in Context.")
        del self._artifacts[key]

    def __contains__(self, key: str) -> bool:
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Return iterator over a static list of keys to prevent issues on modification
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def get(self, key: str, default: Any = None) -> Any:
        return self._artifacts.get(key, default)

    def clone(self) -> "Context":
        return Context(
            artifacts=copy.deepcopy(self._artifacts),
            config=copy.deepcopy(self._config),
        )

    def dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._artifacts)

    def json(self) -> str:
        return jsonlib.dumps(self._artifacts)

    def keys(self) -> Iterator[str]:
        return iter(list(self._artifacts.keys()))

    def get_config(self) -> Dict[str, Any]:
        return self._config

    def set_config(self, config: Dict[str, Any]) -> None:
        self._config = config
