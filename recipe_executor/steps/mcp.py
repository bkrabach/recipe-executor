import logging
from typing import Any, Dict, Optional

from recipe_executor.context import ContextProtocol
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.protocols import StepProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class McpConfig(StepConfig):
    """
    Configuration for McpStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool.
        output_key: Context key under which to store the tool output.
        timeout: Optional timeout in seconds for the call.
    """

    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any] = {}
    output_key: str = "tool_result"
    timeout: Optional[int] = None


class McpStep(BaseStep[McpConfig], StepProtocol):
    """
    Step for invoking a tool on a remote MCP server and storing the result in the context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, McpConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render configuration values using context (Liquid templates supported)
        server_conf: Dict[str, Any] = {
            k: render_template(str(v), context) if isinstance(v, str) else v for k, v in self.config.server.items()
        }
        tool_name: str = render_template(self.config.tool_name, context)
        output_key: str = render_template(self.config.output_key, context)

        # Render arguments (template only string values)
        arguments: Dict[str, Any] = {}
        for k, v in self.config.arguments.items():
            if isinstance(v, str):
                arguments[k] = render_template(v, context)
            else:
                arguments[k] = v

        # Construct MCP client
        self.logger.debug(f"Connecting to MCP server at '{server_conf.get('url')}' for tool '{tool_name}'")

        try:
            client = get_mcp_server(self.logger, server_conf)
        except Exception as exc:
            raise ValueError(f"Failed to create MCP client: {exc}") from exc

        # Call tool
        try:
            self.logger.debug(f"Calling MCP tool '{tool_name}' with arguments: {arguments}")
            result: Any = await client.call_tool(tool_name, arguments)
        except Exception as exc:
            raise ValueError(
                f"Error calling tool '{tool_name}' on MCP server '{server_conf.get('url') or server_conf}': {exc}"
            ) from exc

        # Store result in context
        context[output_key] = result
        self.logger.debug(f"MCP result stored under key '{output_key}' in context.")
