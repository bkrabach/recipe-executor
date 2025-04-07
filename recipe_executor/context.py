import copy
import logging
from typing import Any, Dict, Iterator, Optional, Protocol, Union


class Executor(Protocol):
    def execute(
        self, recipe: Union[str, Dict[str, Any]], context: "Context", logger: Optional[logging.Logger] = None
    ) -> None: ...


class Context:
    """
    Context is the shared state container for the Recipe Executor system,
    providing a dictionary-like interface for storing and retrieving artifacts
    along with separate configuration values.
    Additionally, it provides an executor, for steps that need to execute
    recipes.

    Attributes:
        executor (Executor): The executor for executing recipes.
        config (Dict[str, Any]): A dictionary holding the configuration values.
    """

    def __init__(
        self, executor: Executor, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store
            config: Configuration values
        """
        # Use deep copy to prevent external modifications
        self.__artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}
        self.executor = executor

    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-like setting of artifacts."""
        self.__artifacts[key] = value

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access to artifacts.

        Raises:
            KeyError: If the key does not exist in the artifacts.
        """
        if key not in self.__artifacts:
            raise KeyError(f"Key '{key}' not found in Context.")
        return self.__artifacts[key]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get an artifact with an optional default value."""
        return self.__artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in artifacts."""
        return key in self.__artifacts

    def __iter__(self) -> Iterator[str]:
        """Iterate over artifact keys."""
        # Return a list copy of keys to ensure immutability
        return iter(list(self.__artifacts.keys()))

    def keys(self) -> Iterator[str]:
        """Return an iterator over the keys of artifacts."""
        return iter(list(self.__artifacts.keys()))

    def __len__(self) -> int:
        """Return the number of artifacts."""
        return len(self.__artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """Return a deep copy of the artifacts as a dictionary to ensure immutability."""
        return copy.deepcopy(self.__artifacts)

    def clone(self) -> "Context":
        """Return a deep copy of the current context, including artifacts and configuration."""
        cloned_artifacts = copy.deepcopy(self.__artifacts)
        cloned_config = copy.deepcopy(self.config)
        return Context(executor=self.executor, artifacts=cloned_artifacts, config=cloned_config)
