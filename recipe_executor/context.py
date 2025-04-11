import copy
from typing import Any, Dict, Iterator, Optional

from recipe_executor.protocols import ContextProtocol


class Context(ContextProtocol):
    """
    Context is the shared state container for the Recipe Executor system.
    It maintains a store for artifacts (dynamic data) and a separate store for configuration values.

    Artifacts are accessed via a dictionary-like interface.
    Configuration can be accessed through the 'config' attribute.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize a new Context instance with optional artifacts and configuration.
        Both artifacts and configuration dictionaries are deep-copied to avoid side effects.

        Args:
            artifacts: Optional initial artifacts (dynamic data).
            config: Optional configuration values.
        """
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        """
        Retrieve the artifact associated with the given key.

        Args:
            key: The key to look up in the artifacts store.

        Returns:
            The artifact corresponding to the key.

        Raises:
            KeyError: If the key is not found in the artifacts store.
        """
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set the artifact for the given key to the specified value.

        Args:
            key: The key to set in the artifacts store.
            value: The value to associate with the key.
        """
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        """
        Delete the artifact associated with the given key.

        Args:
            key: The key to delete from the artifacts store.

        Raises:
            KeyError: If the key is not found in the artifacts store.
        """
        if key in self._artifacts:
            del self._artifacts[key]
        else:
            raise KeyError(f"Key '{key}' not found in Context.")

    def __contains__(self, key: object) -> bool:
        """
        Check if a key exists in the artifacts store.

        Args:
            key: The key to check for existence.

        Returns:
            True if the key exists, False otherwise.
        """
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over the keys of the artifacts store.
        A static snapshot of keys is returned to avoid issues with concurrent modifications.

        Returns:
            An iterator over the keys of the artifacts store.
        """
        # Return a snapshot copy of keys
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        """
        Return the number of artifacts stored in the context.

        Returns:
            The count of artifacts.
        """
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the keys of the artifacts store.

        Returns:
            An iterator over the keys (snapshot) of the artifacts store.
        """
        return iter(list(self._artifacts.keys()))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the artifact for the given key, returning a default if the key is not present.

        Args:
            key: The key to retrieve.
            default: The default value to return if key is missing.

        Returns:
            The artifact value if found, or the default value.
        """
        return self._artifacts.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts store as a regular dictionary.

        Returns:
            A deep copy of all artifacts stored in the context.
        """
        return copy.deepcopy(self._artifacts)

    def clone(self) -> ContextProtocol:
        """
        Create a deep copy of the entire Context, including both artifacts and configuration.
        This clone is completely independent of the original.

        Returns:
            A new Context instance with deep-copied artifacts and configuration.
        """
        return Context(artifacts=copy.deepcopy(self._artifacts), config=copy.deepcopy(self.config))
