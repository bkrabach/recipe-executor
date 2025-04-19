import copy
import logging
from typing import Any, Dict, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

# Example secrets to mask in logs
SENSITIVE_KEYS = {"authorization", "api_key", "token", "secret", "password", "access_token", "refresh_token"}


def _mask_sensitive(obj: Any) -> Any:
    """
    Recursively mask sensitive values in a dictionary (or lists of dictionaries) for logging.
    Returns a new object with sensitive values replaced.
    """
    if isinstance(obj, dict):
        masked = {}
        for key, value in obj.items():
            if isinstance(key, str) and key.lower() in SENSITIVE_KEYS:
                masked[key] = "***"
            else:
                masked[key] = _mask_sensitive(value)
        return masked
    elif isinstance(obj, list):
        return [_mask_sensitive(item) for item in obj]
    else:
        return obj


def get_mcp_server(
    logger: logging.Logger,
    config: Dict[str, Any],
) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.

    Raises:
        ValueError: If the configuration is invalid or missing required information.
    """
    if not isinstance(config, dict):
        raise ValueError("config must be a dict")

    # Make a shallow copy for debugging/masking
    config_masked: Dict[str, Any] = _mask_sensitive(copy.deepcopy(config))
    logger.debug(f"get_mcp_server called with config: {config_masked}")

    # Determine whether to use HTTP or stdio transport (mutually exclusive)
    if "url" in config:
        url: str = config.get("url", "")
        if not isinstance(url, str) or not url:
            raise ValueError("'url' must be a non-empty string for MCPServerHTTP.")
        headers: Optional[Dict[str, str]] = config.get("headers")
        if headers is not None and not isinstance(headers, dict):
            raise ValueError("'headers' must be a dictionary if provided.")
        # Mask headers for info log
        info_headers = _mask_sensitive(headers) if headers else None
        logger.info(f"Initializing MCPServerHTTP with url={url!r}, headers={info_headers!r}")
        try:
            return MCPServerHTTP(url=url, headers=headers)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MCPServerHTTP: {e}")
    elif "command" in config:
        command = config.get("command")
        if not isinstance(command, str) or not command:
            raise ValueError("'command' must be a non-empty string for MCPServerStdio.")
        args = config.get("args")
        if args is not None and not (isinstance(args, list) and all(isinstance(a, str) for a in args)):
            raise ValueError("'args' must be a list of strings if provided.")
        cwd = config.get("cwd")
        if cwd is not None and not isinstance(cwd, str):
            raise ValueError("'cwd' must be a string if provided.")
        logger.info(f"Initializing MCPServerStdio with command={command!r}, args={args!r}, cwd={cwd!r}")
        try:
            return MCPServerStdio(command, args=args or [], cwd=cwd)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MCPServerStdio: {e}")
    else:
        raise ValueError("Invalid MCP server config: must contain either 'url' for HTTP or 'command' for stdio.")
