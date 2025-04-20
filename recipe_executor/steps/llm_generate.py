import logging
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, create_model

from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class LLMGenerateConfig(StepConfig):
    prompt: str
    model: str = "openai/gpt-4o"
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any]] = "text"
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):
    files: List[FileSpec]


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        prompt: str = render_template(self.config.prompt, context)
        model: str = render_template(self.config.model, context)
        output_key: str = render_template(self.config.output_key, context)
        mcp_servers: List[Any] = []
        mcp_server_configs: List[Dict[str, Any]] = []

        if self.config.mcp_servers is not None:
            mcp_server_configs.extend(self.config.mcp_servers)
        context_config: Dict[str, Any] = context.get_config()
        mcp_servers_from_context: Optional[List[Dict[str, Any]]] = context_config.get("mcp_servers", None)
        if mcp_servers_from_context is not None:
            mcp_server_configs.extend(mcp_servers_from_context)
        if mcp_server_configs:
            for mcp_server_config in mcp_server_configs:
                mcp_servers.append(get_mcp_server(self.logger, mcp_server_config))

        output_format: Union[str, Dict[str, Any]] = self.config.output_format
        rendered_output_format: Union[str, Dict[str, Any]] = output_format
        if isinstance(output_format, str):
            rendered_output_format = render_template(output_format, context)
        elif isinstance(output_format, dict):

            def render_schema(data: Any) -> Any:
                if isinstance(data, str):
                    return render_template(data, context)
                if isinstance(data, dict):
                    return {k: render_schema(v) for k, v in data.items()}
                if isinstance(data, list):
                    return [render_schema(x) for x in data]
                return data

            rendered_output_format = render_schema(output_format)

        output_type: Type[Union[str, BaseModel]] = str
        try:
            if rendered_output_format == "text":
                output_type = str
            elif rendered_output_format == "files":
                output_type = FileSpecCollection
            elif isinstance(rendered_output_format, dict):
                output_type = self._json_schema_to_pydantic_model(rendered_output_format)
            else:
                raise ValueError(f"Invalid output_format: {rendered_output_format}")

            self.logger.debug(
                f"Calling LLM: model={model} output_type={output_type} MCP_servers={'yes' if mcp_servers else 'no'}"
            )
            llm = LLM(
                logger=self.logger,
                model=model,
                mcp_servers=mcp_servers if mcp_servers else None,
            )
            result: Any = await llm.generate(prompt, output_type=output_type)
            if output_type is FileSpecCollection and isinstance(result, FileSpecCollection):
                context[output_key] = result.files
            else:
                context[output_key] = result
        except Exception as e:
            self.logger.error(f"LLM call failed for output_key '{output_key}': {e}", exc_info=True)
            raise

    def _json_schema_to_pydantic_model(self, schema: Dict[str, Any]) -> Type[BaseModel]:
        def build_type(subschema: Dict[str, Any]) -> Any:
            schema_type = subschema.get("type")
            if schema_type == "string":
                return (str, ...)
            if schema_type == "integer":
                return (int, ...)
            if schema_type == "number":
                return (float, ...)
            if schema_type == "boolean":
                return (bool, ...)
            if schema_type == "object":
                props = subschema.get("properties", {})
                required = set(subschema.get("required", []))
                fields = {}
                for pname, pschema in props.items():
                    ptype, _ = build_type(pschema)
                    default = ... if pname in required else None
                    fields[pname] = (ptype, default)
                model = create_model("JsonSchemaObj", **fields)  # type: ignore
                return (model, ...)
            if schema_type == "array" or schema_type == "list":
                items_schema = subschema.get("items", {})
                item_type, _ = build_type(items_schema)
                return (List[item_type], ...)
            return (Any, ...)

        if schema.get("type") == "array" or schema.get("type") == "list":
            item_schema = schema.get("items", {})
            item_type, _ = build_type(item_schema)
            return create_model("RootListModel", __root__=(List[item_type], ...))  # type: ignore
        if schema.get("type") == "object":
            props = schema.get("properties", {})
            required = set(schema.get("required", []))
            fields = {}
            for fname, fschema in props.items():
                ftype, _ = build_type(fschema)
                default = ... if fname in required else None
                fields[fname] = (ftype, default)
            return create_model("RootObjModel", **fields)  # type: ignore
        return create_model("AnyModel", __root__=(Any, ...))
