"""
Minimal MCP utility for creating MCPServer instances from configurations.
"""
import logging
from typing import Any, Dict, List, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

# Keys considered sensitive for masking
_SENSITIVE_KEYS = ("key", "secret", "token", "password")

def _mask_value(value: Any, key: Optional[str] = None) -> Any:
    """
    Mask sensitive values in a configuration dictionary.
    """
    # Mask entire value if key indicates sensitive data
    if key and any(sensitive in key.lower() for sensitive in _SENSITIVE_KEYS):
        return "***"
    # Recurse into dicts
    if isinstance(value, dict):
        return {k: _mask_value(v, k) for k, v in value.items()}
    return value


def get_mcp_server(
    logger: logging.Logger,
    config: Dict[str, Any]
) -> MCPServer:
    """
    Create an MCPServer instance based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCPServer instance.

    Raises:
        ValueError: If configuration is invalid.
        RuntimeError: If instantiation of the server fails.
    """
    # Mask and log configuration for debugging
    try:
        masked = _mask_value(config)  # type: ignore
        logger.debug("MCP configuration: %s", masked)
    except Exception:
        logger.debug("MCP configuration contains non-serializable values")

    # HTTP transport configuration
    if "url" in config:
        url = config.get("url")
        if not isinstance(url, str):
            raise ValueError("MCP HTTP configuration requires a string 'url'")
        headers = config.get("headers")
        if headers is not None:
            if not isinstance(headers, dict) or not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in headers.items()
            ):
                raise ValueError("MCP HTTP 'headers' must be a dict of string keys and values")
        logger.info("Configuring MCPServerHTTP for URL: %s", url)
        try:
            # Only pass headers if provided
            if headers is not None:
                return MCPServerHTTP(url=url, headers=headers)
            return MCPServerHTTP(url=url)
        except Exception as error:
            msg = f"Failed to create HTTP MCP server for {url}: {error}"
            logger.error(msg)
            raise RuntimeError(msg) from error

    # Stdio transport configuration
    if "command" in config:
        command = config.get("command")
        if not isinstance(command, str):
            raise ValueError("MCP stdio configuration requires a string 'command'")
        args_value = config.get("args")
        if args_value is None:
            args_list: List[str] = []
        else:
            if not isinstance(args_value, list) or not all(isinstance(a, str) for a in args_value):
                raise ValueError("MCP stdio 'args' must be a list of strings")
            args_list = args_value  # type: List[str]
        logger.info(
            "Configuring MCPServerStdio with command: %s args: %s",
            command,
            args_list,
        )
        try:
            return MCPServerStdio(command=command, args=args_list)
        except Exception as error:
            msg = f"Failed to create stdio MCP server for command {command}: {error}"
            logger.error(msg)
            raise RuntimeError(msg) from error

    # If neither HTTP nor stdio config is present
    raise ValueError(
        "Invalid MCP server configuration: provide either 'url' for HTTP or 'command' for stdio"
    )
