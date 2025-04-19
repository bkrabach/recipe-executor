import logging
from copy import deepcopy
from typing import Any, Dict, Optional

from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.protocols import ContextProtocol
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
    arguments: Dict[str, Any]
    output_key: str = "tool_result"
    timeout: Optional[int] = None


class McpStep(BaseStep[McpConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, McpConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render templates in all string values of server and tool_name, output_key
        server_config = deepcopy(self.config.server)
        for key, value in server_config.items():
            if isinstance(value, str):
                server_config[key] = render_template(value, context)
        tool_name = render_template(self.config.tool_name, context)
        output_key = render_template(self.config.output_key, context)

        # Render arguments dict with templates
        arguments = {}
        for k, v in self.config.arguments.items():
            if isinstance(v, str):
                arguments[k] = render_template(v, context)
            else:
                arguments[k] = v

        timeout = self.config.timeout

        self.logger.debug(
            f"Connecting to MCP server at {server_config.get('url', '<no url>')} to invoke tool '{tool_name}' "
            f"with arguments {arguments} (timeout={timeout})"
        )

        mcp_server = get_mcp_server(self.logger, server_config)
        try:
            # Call the tool (timeout is not always supported; let errors propagate)
            result = await mcp_server.call_tool(tool_name, arguments)
        except Exception as e:
            raise ValueError(
                f"Failed to call tool '{tool_name}' on MCP service at {server_config.get('url')}: {e}"
            ) from e

        # Store the result in the context (overwrite if exists)
        context[output_key] = result
        self.logger.debug(f"Stored result of tool '{tool_name}' under context key '{output_key}'.")
