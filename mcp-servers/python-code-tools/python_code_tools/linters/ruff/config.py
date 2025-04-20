from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import tomli

default_config = {
    "select": "E,F,W,I",
    "ignore": [],
    "line-length": 100,
}


async def get_config(user_config: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
    """Get the preferred configuration for Ruff.

    Args:
        user_config: Optional user-provided configuration

    Returns:
        Tuple of (configuration settings, source description)
    """
    print(f"Getting Ruff configuration. User config provided: {user_config is not None}")

    # Priority order:
    # 1. User-provided configuration
    # 2. Project configuration from .ruff.toml
    # 3. Project configuration from pyproject.toml
    # 4. Default configuration

    if user_config:
        # User config has highest priority - use ONLY this
        print("Using user-provided configuration")
        return user_config, "user"
    else:
        # Project config has second priority - use ONLY this
        project_config, source = await read_project_config(Path.cwd())
        if project_config:
            print(f"Using project configuration from {source}")
            return project_config, source
        else:
            # Default config has lowest priority - use ONLY this
            print("No project configuration found, using default configuration")
            return default_config, "default"


async def read_project_config(path: Path) -> Tuple[Dict[str, Any], str]:
    """Read Ruff configuration from files within the project directory.

    Args:
        path: Project directory path

    Returns:
        Tuple of (configuration settings, source description)
    """
    config = {}
    source = "none"

    print(f"Looking for Ruff configuration files in {path}")

    # Check for .ruff.toml (highest priority)
    ruff_toml_path = path / ".ruff.toml"
    if ruff_toml_path.exists():
        print(f"Found .ruff.toml at {ruff_toml_path}")
        try:
            with open(ruff_toml_path, "rb") as f:
                ruff_config = tomli.load(f)
                if "lint" in ruff_config:
                    config.update(ruff_config["lint"])
                else:
                    config.update(ruff_config)
                # Return immediately since this is highest priority
                return config, ".ruff.toml"
        except Exception as e:
            print(f"Error reading .ruff.toml: {e}")

    # Check for pyproject.toml (lower priority)
    pyproject_path = path / "pyproject.toml"
    if pyproject_path.exists():
        print(f"Found pyproject.toml at {pyproject_path}")
        try:
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)
                # Extract Ruff configuration
                if "tool" in pyproject_data and "ruff" in pyproject_data["tool"]:
                    ruff_config = pyproject_data["tool"]["ruff"]
                    if "lint" in ruff_config:
                        config.update(ruff_config["lint"])
                    else:
                        config.update(ruff_config)
                    return config, "pyproject.toml"
        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")

    return config, source
