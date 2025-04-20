import logging
import os
import time
from typing import List, Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
from recipe_executor.llm_utils.mcp import MCPServer


def get_model(model_id: str, logger: logging.Logger) -> Union[OpenAIModel, AnthropicModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    """
    if not isinstance(model_id, str):
        raise ValueError(
            "model_id must be a string of format 'provider/model_name' or 'provider/model_name/deployment_name'"
        )
    segments = model_id.split("/")
    if len(segments) < 2:
        raise ValueError(
            f"Invalid model_id: '{model_id}'. Expected format 'provider/model_name' or 'provider/model_name/deployment_name'."
        )

    provider: str = segments[0].lower()
    model_name: str = segments[1]
    deployment_name: Optional[str] = segments[2] if len(segments) > 2 else None

    if provider == "openai":
        return OpenAIModel(model_name=model_name)
    if provider == "azure":
        return get_azure_openai_model(logger=logger, model_name=model_name, deployment_name=deployment_name)
    if provider == "anthropic":
        return AnthropicModel(model_name=model_name)
    if provider == "ollama":
        ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        provider_obj: OpenAIProvider = OpenAIProvider(base_url=f"{ollama_base_url}/v1")
        return OpenAIModel(model_name=model_name, provider=provider_obj)

    raise ValueError(f"Unsupported provider: '{provider}'. Must be one of 'openai', 'azure', 'anthropic', 'ollama'.")


class LLM:
    def __init__(
        self,
        logger: logging.Logger,
        model: str = "openai/gpt-4o",
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            model (str): Model identifier.
            mcp_servers (Optional[List[MCPServer]]): MCP servers list.
        """
        self.logger: logging.Logger = logger
        self.model: str = model
        self.mcp_servers: List[MCPServer] = mcp_servers or []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        actual_model_id: str = model if model is not None else self.model
        mcp_servers_to_use: List[MCPServer] = mcp_servers if mcp_servers is not None else self.mcp_servers
        # Info log: provider and model name
        provider = actual_model_id.split("/")[0] if "/" in actual_model_id else actual_model_id
        self.logger.info(f"LLM call with provider='{provider}' model='{actual_model_id}'")
        try:
            model_obj = get_model(actual_model_id, self.logger)
            agent: Agent[None, Union[str, BaseModel]] = Agent(
                model=model_obj,
                mcp_servers=mcp_servers_to_use,
                output_type=output_type,
            )
            self.logger.debug({
                "prompt": prompt,
                "model": actual_model_id,
                "output_type": output_type.__name__ if hasattr(output_type, "__name__") else str(output_type),
                "mcp_servers": [str(s) for s in mcp_servers_to_use],
            })
            start_time = time.monotonic()
            async with agent.run_mcp_servers():
                result = await agent.run(prompt)
            elapsed = time.monotonic() - start_time
            tokens_info = {}
            try:
                usage = result.usage()
                tokens_info = {
                    "requests": getattr(usage, "requests", None),
                    "request_tokens": getattr(usage, "request_tokens", None),
                    "response_tokens": getattr(usage, "response_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                }
            except Exception:
                pass
            self.logger.info({
                "elapsed_seconds": elapsed,
                **tokens_info,
            })
            self.logger.debug({"output": repr(result.output)})
            return result.output
        except Exception as exc:
            self.logger.error(f"LLM call failed: {exc}", exc_info=True)
            raise
