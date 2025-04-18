import logging
from typing import Any, Dict, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

from recipe_executor.models import MCPServerConfig, MCPServerHttpConfig, MCPServerStdioConfig


def _mask_value(key: str, value: Any) -> Any:
    """
    Mask sensitive values for logging.
    """
    SENSITIVE_KEYS = {"api_key", "authorization", "password", "token"}
    if isinstance(value, dict):
        return {k: _mask_value(k, v) for k, v in value.items()}
    if key.lower() in SENSITIVE_KEYS and isinstance(value, str):
        return "***MASKED***"
    return value


def _log_config(logger: logging.Logger, config: MCPServerConfig) -> None:
    """
    Log configuration with sensitive values masked.
    """
    from pydantic import BaseModel

    if isinstance(config, BaseModel):
        config_dict = config.model_dump()
    else:
        config_dict = dict(config)
    masked = {_k: _mask_value(_k, _v) for _k, _v in config_dict.items()}
    logger.debug(f"MCPServerConfig: {masked}")


def get_mcp_server(
    logger: logging.Logger,
    config: MCPServerConfig,
) -> MCPServer:
    """
    Create an MCP server client based on the specified URI and server type.

    Args:
        logger (logging.Logger): Logger for logging messages.
        config: (MCPServerConfig): Configuration for the MCP server.

    Returns:
        MCPServer: A configured PydanticAI MCP server client.

    Raises:
        ValueError: If the configuration is invalid.
        RuntimeError: If MCP server initialization fails.
    """
    _log_config(logger, config)

    try:
        if isinstance(config, MCPServerHttpConfig):
            if not getattr(config, "url", None):
                raise ValueError('MCPServerHttpConfig missing required "url"')
            url = str(config.url)
            headers: Optional[Dict[str, Any]] = getattr(config, "headers", None)
            server = MCPServerHTTP(url=url, headers=headers)
            logger.info(f"Initialized MCPServerHTTP (transport=http) to {url}")
            return server
        elif isinstance(config, MCPServerStdioConfig):
            if not getattr(config, "command", None):
                raise ValueError('MCPServerStdioConfig missing required "command"')
            command: str = config.command
            args: list[str] = config.args or []
            env: Optional[Dict[str, str]] = config.env
            cwd = getattr(config, "cwd", None)
            server = MCPServerStdio(command, args=args, env=env, cwd=cwd)
            logger.info(f"Initialized MCPServerStdio (transport=stdio) with command: {command} {' '.join(args)}")
            return server
        else:
            raise ValueError(f"Unknown MCPServerConfig type: {type(config)}")
    except Exception as exc:
        logger.error(f"Failed to initialize MCP server: {exc}")
        raise RuntimeError(f"Failed to initialize MCP server: {exc}") from exc
