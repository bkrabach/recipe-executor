import logging
import os
import time
from typing import Any, List, Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel

# openai model is used for both OpenAI and Ollama
from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import MCPServerConfig


class LLM:
    def __init__(
        self,
        logger: logging.Logger,
        model: str = "openai/gpt-4o",
        mcp_servers: Optional[List[MCPServerConfig]] = None,
    ):
        self.logger: logging.Logger = logger
        self.model: str = model
        self.mcp_servers: Optional[List[MCPServerConfig]] = mcp_servers

    @staticmethod
    def get_model(
        model_id: Optional[str],
        logger: logging.Logger,
    ) -> Union[OpenAIModel, AnthropicModel]:
        """
        Initialize an LLM model based on a standardized model_id string.
        Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
        Supported providers: openai, azure, anthropic, ollama
        """
        if not model_id:
            model_id = "openai/gpt-4o"
        parts = model_id.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid model_id '{model_id}' (expected 'provider/model_name')")
        provider = parts[0].lower()
        model_name = parts[1]
        deployment_name: Optional[str] = None
        # Azure might have deployment name
        if provider == "azure":
            if len(parts) == 3:
                deployment_name = parts[2]
            return get_azure_openai_model(
                logger=logger,
                model_name=model_name,
                deployment_name=deployment_name,
            )
        elif provider == "openai":
            return OpenAIModel(model_name=model_name)
        elif provider == "anthropic":
            return AnthropicModel(model_name=model_name)
        elif provider == "ollama":
            # OLLAMA_BASE_URL must be in env
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            from pydantic_ai.providers.openai import OpenAIProvider

            return OpenAIModel(model_name=model_name, provider=OpenAIProvider(base_url=f"{ollama_base_url}/v1"))
        else:
            raise ValueError(f"Unsupported model provider '{provider}' in model_id '{model_id}'")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServerConfig]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate a response from the LLM based on the provided prompt.
        See full documentation in usage docs.
        """
        chosen_model_id: str = model or self.model
        chosen_mcp_servers: Optional[List[MCPServerConfig]] = (
            mcp_servers if mcp_servers is not None else self.mcp_servers
        )
        try:
            # -- LOG: info --
            self.logger.info(
                f"LLM call starting, model={chosen_model_id.split('/', 1)[0]}, provider/model={chosen_model_id}"
            )

            # -- LOG: debug: the request payload
            self.logger.debug({
                "prompt": prompt,
                "output_type": getattr(output_type, "__name__", repr(output_type)),
                "model": chosen_model_id,
                "mcp_servers_config": [
                    mcps.dict() if hasattr(mcps, "dict") else str(mcps) for mcps in (chosen_mcp_servers or [])
                ],
            })

            model_instance = self.get_model(chosen_model_id, self.logger)

            # -- Handle MCP servers
            pydantic_mcp_servers: List[Any] = []
            if chosen_mcp_servers:
                for config in chosen_mcp_servers:
                    mcp = get_mcp_server(logger=self.logger, config=config)
                    pydantic_mcp_servers.append(mcp)

            agent = Agent(
                model=model_instance,
                output_type=output_type,
                mcp_servers=pydantic_mcp_servers,
            )

            # measure timing
            start_time = time.time()
            result = await agent.run(prompt)
            elapsed = time.time() - start_time

            output = result.data
            usage = None
            if hasattr(result, "usage"):
                try:
                    usage = result.usage()
                except Exception:
                    usage = None
            # -- LOG: debug: full response payload
            self.logger.debug({"llm_response": getattr(result, "__dict__", str(result))})
            # -- LOG: info: response meta
            tokens_info = f"tokens={getattr(usage, 'total_tokens', None)}" if usage else "tokens=unknown"
            self.logger.info(f"LLM call complete, elapsed={elapsed:.2f}s, {tokens_info}")
            return output
        except Exception as exc:
            self.logger.error(f"LLM error: {exc}")
            raise
