import logging
from typing import Any, Dict

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

MASK_KEYS = {"authorization", "api_key", "secret", "token", "password", "key"}


def _mask_sensitive(val: Any, key: str) -> Any:
    """Mask sensitive values in a dictionary."""
    if any(k in key.lower() for k in MASK_KEYS):
        return "***MASKED***"
    if isinstance(val, dict):
        return {k: _mask_sensitive(v, k) for k, v in val.items()}
    return val


def get_mcp_server(logger: logging.Logger, config: Dict[str, Any]) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.
    """

    if not isinstance(config, dict):
        logger.error("MCP config should be a dictionary")
        raise ValueError("MCP config should be a dictionary")

    # Log config at debug level, masking secrets
    masked_cfg = {k: _mask_sensitive(v, k) for k, v in config.items()}
    logger.debug(f"Creating MCP server with config: {masked_cfg}")

    # Try HTTP first
    if "url" in config:
        url = config["url"]
        if not isinstance(url, str) or not url:
            raise ValueError("MCP HTTP config missing required 'url' (string)")
        headers = config.get("headers")
        if headers is not None and not isinstance(headers, dict):
            raise ValueError("'headers' must be a dictionary if provided")
        logger.info(f"Creating MCPServerHTTP for url={url}")
        return MCPServerHTTP(url=url, headers=headers)
    # Try stdio next
    elif "command" in config or "args" in config:
        command = config.get("command")
        args = config.get("args")
        if not isinstance(command, str) or not command:
            raise ValueError("MCP stdio config requires a non-empty 'command' string")
        if args is not None and not (isinstance(args, list) and all(isinstance(a, str) for a in args)):
            raise ValueError("'args' must be a list of strings if provided")
        logger.info(f"Creating MCPServerStdio for command={command} args={args}")
        return MCPServerStdio(command, args=args or [], env=config.get("env"), cwd=config.get("cwd"))
    else:
        logger.error("MCP config missing required connection information (either 'url' or 'command')")
        raise ValueError("MCP config must specify 'url' for HTTP or 'command' for stdio transport")
