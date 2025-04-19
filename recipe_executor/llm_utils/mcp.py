import logging
from copy import deepcopy
from typing import Any, Dict, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

SENSITIVE_KEYS = {"authorization", "api_key", "key", "secret", "token", "password"}


def mask_sensitive(obj: Any) -> Any:
    """
    Recursively mask sensitive keys in a dict, list, or other supported types.
    """
    if isinstance(obj, dict):
        return {k: ("***MASKED***" if k.lower() in SENSITIVE_KEYS else mask_sensitive(v)) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [mask_sensitive(v) for v in obj]
    return obj


def get_mcp_server(logger: logging.Logger, config: Dict[str, Any]) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.
    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.
    Returns:
        A configured PydanticAI MCP server client.
    Raises:
        ValueError: If the configuration is invalid.
        RuntimeError: If an unexpected exception is encountered.
    """
    # Mask and log config for debug
    masked_config = mask_sensitive(deepcopy(config))
    logger.debug(f"MCP config: {masked_config}")

    # Detect server type: HTTP if 'url' key, otherwise stdio if 'command' or 'args'
    if "url" in config:
        url: str = config["url"]
        headers: Optional[Dict[str, str]] = config.get("headers")
        try:
            if not isinstance(url, str) or not url:
                raise ValueError("The 'url' config value must be a non-empty string for MCPServerHTTP.")
            if headers is not None and not isinstance(headers, dict):
                raise ValueError("The 'headers' config value must be a dict if provided.")
            logger.info(f"Creating MCPServerHTTP: url={url}")
            return MCPServerHTTP(url=url, headers=headers)  # type: ignore[arg-type]
        except Exception as exc:
            raise RuntimeError(f"Failed to create MCPServerHTTP: {exc}") from exc

    elif "command" in config or "args" in config:
        command: Optional[str] = config.get("command")
        args: Optional[Any] = config.get("args")
        if command is None:
            # Support args as a list like ["deno", ...]
            if isinstance(args, (list, tuple)) and len(args) >= 1:
                command = args[0]
                args = args[1:]
            else:
                raise ValueError(
                    "Either 'command' (str) or non-empty 'args' (list/tuple) must be provided for MCPServerStdio."
                )
        if not isinstance(command, str) or not command:
            raise ValueError("The 'command' config value must be a non-empty string for MCPServerStdio.")
        if args is not None and not isinstance(args, (list, tuple)):
            raise ValueError("The 'args' config value must be a list or tuple if provided for MCPServerStdio.")
        logger.info(f"Creating MCPServerStdio: command={command} args={args if args else []}")
        try:
            return MCPServerStdio(command, args=list(args) if args is not None else [])
        except Exception as exc:
            raise RuntimeError(f"Failed to create MCPServerStdio: {exc}") from exc

    raise ValueError(
        "Invalid MCP server config: requires either 'url' for HTTP or 'command'/'args' for stdio transport."
    )
