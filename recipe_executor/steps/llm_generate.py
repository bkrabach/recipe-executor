import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.models import json_object_to_pydantic_model
from recipe_executor.utils.templates import render_template


class LLMGenerateConfig(StepConfig):
    """
    Config for LLMGenerateStep.
    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        mcp_servers: List of MCP servers for access to tools.
        output_format: The format of the LLM output (text, files, or JSON/object/list schemas).
        output_key: The name under which to store the LLM output in context.
    """

    prompt: str
    model: str = "openai/gpt-4o"
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any], List[Any]]
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):
    files: List[FileSpec]


def render_template_config(config: Dict[str, Any], context: ContextProtocol) -> Dict[str, Any]:
    rendered: Dict[str, Any] = {}
    for k, v in config.items():
        if isinstance(v, str):
            rendered[k] = render_template(v, context)
        elif isinstance(v, dict):
            rendered[k] = render_template_config(v, context)
        elif isinstance(v, list):
            rendered[k] = [render_template_config(i, context) if isinstance(i, dict) else i for i in v]
        else:
            rendered[k] = v
    return rendered


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        prompt: str = render_template(self.config.prompt, context)
        model_id: str = render_template(self.config.model, context) if self.config.model else "openai/gpt-4o"
        output_key: str = render_template(self.config.output_key, context)

        # Collect MCP server configs from config and context
        mcp_servers_configs: List[Dict[str, Any]] = []
        if self.config.mcp_servers:
            mcp_servers_configs.extend(self.config.mcp_servers)
        context_mcp_servers_cfg = context.get_config().get("mcp_servers", [])
        if context_mcp_servers_cfg:
            mcp_servers_configs.extend(context_mcp_servers_cfg)
        mcp_servers: Optional[List[Any]] = None
        if mcp_servers_configs:
            mcp_servers = [
                get_mcp_server(logger=self.logger, config=render_template_config(cfg, context))
                for cfg in mcp_servers_configs
            ]

        llm = LLM(logger=self.logger, model=model_id, mcp_servers=mcp_servers)
        output_format = self.config.output_format
        result: Any = None
        try:
            self.logger.debug(
                "Calling LLM: model=%s, output_format=%r, mcp_servers=%r", model_id, output_format, mcp_servers
            )
            if output_format == "text":
                result = await llm.generate(prompt, output_type=str)
                context[output_key] = result
            elif output_format == "files":
                result = await llm.generate(prompt, output_type=FileSpecCollection)
                context[output_key] = result.files
            elif isinstance(output_format, dict) and output_format.get("type") == "object":
                schema_model = json_object_to_pydantic_model(output_format, model_name="LLMObject")
                result = await llm.generate(prompt, output_type=schema_model)
                context[output_key] = result.model_dump()
            elif isinstance(output_format, list):
                if len(output_format) != 1 or not isinstance(output_format[0], dict):
                    raise ValueError(
                        "When output_format is a list, it must be a single-item list containing a valid schema object."
                    )
                item_schema = output_format[0]
                object_schema = {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": item_schema}},
                    "required": ["items"],
                }
                schema_model = json_object_to_pydantic_model(object_schema, model_name="LLMListWrapper")
                result = await llm.generate(prompt, output_type=schema_model)
                items = result.model_dump()["items"]
                context[output_key] = items
            else:
                raise ValueError(f"Unsupported output_format: {output_format!r}")
        except Exception as e:
            self.logger.error("LLM generate failed: %r", e, exc_info=True)
            raise
