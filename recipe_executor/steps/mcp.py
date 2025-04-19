import logging
from typing import Any, Dict, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template
from recipe_executor.llm_utils.mcp import get_mcp_server


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
    output_key: str = "tool_result"
    timeout: Optional[int] = None
    arguments: Dict[str, Any] = {}


class McpStep(BaseStep[McpConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, McpConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        server_config: Dict[str, Any] = self.config.server or {}
        tool_name: str = self.config.tool_name
        output_key: str = self.config.output_key
        arguments: Dict[str, Any] = self.config.arguments or {}
        timeout: Optional[int] = self.config.timeout

        # Render templates in server config values
        rendered_server_config: Dict[str, Any] = {}
        for key, value in server_config.items():
            if isinstance(value, str):
                rendered_value = render_template(value, context)
            else:
                rendered_value = value
            rendered_server_config[key] = rendered_value

        # Render templates for tool name and output key
        rendered_tool_name: str = render_template(tool_name, context)
        rendered_output_key: str = render_template(output_key, context)
        # Render templates in arguments values
        rendered_arguments: Dict[str, Any] = {}
        for k, v in arguments.items():
            if isinstance(v, str):
                rendered_v = render_template(v, context)
            else:
                rendered_v = v
            rendered_arguments[k] = rendered_v

        self.logger.debug(
            f"Connecting to MCP server: config={rendered_server_config}"
        )
        self.logger.debug(
            f"Invoking tool '{rendered_tool_name}' with arguments {rendered_arguments} (timeout={timeout})"
        )

        try:
            client = get_mcp_server(self.logger, rendered_server_config)
            result = await client.call_tool(rendered_tool_name, rendered_arguments)
        except Exception as exc:
            raise ValueError(
                f"McpStep: Failed to call tool '{rendered_tool_name}' on MCP server ({rendered_server_config.get('url', '<unknown>')}): {exc}"
            ) from exc
        # Store result in context under output_key
        context[rendered_output_key] = result
