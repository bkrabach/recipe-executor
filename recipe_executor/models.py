"""
Core data models for the Recipe Executor system.
Defines structures for file specs, recipe steps, and MCP server configs.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyUrl, BaseModel


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file.
    """

    path: str
    content: str


class MCPServerHttpConfig(BaseModel):
    """Configuration for an MCP server HTTP client.

    Attributes:
        url: The URL of the MCP server.
        headers: Optional headers for the HTTP request.
    """

    url: AnyUrl
    headers: Optional[Dict[str, Any]] = None


class MCPServerStdioConfig(BaseModel):
    """Configuration for an MCP server STDIO client.

    Attributes:
        command: The command to run the MCP server.
        args: A list of arguments for the command.
        env: Optional environment variables for the command.
        cwd: Optional working directory for the command.
    """

    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    cwd: Optional[Union[str, Path]] = None


MCPServerConfig = Union[MCPServerHttpConfig, MCPServerStdioConfig]


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """

    type: str
    config: Dict[str, Any]


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]
