import logging
import os
import time
from typing import Any, List, Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
from recipe_executor.llm_utils.mcp import MCPServer

# Default model falls back to openai/gpt-4o
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


class LLM:
    model: str
    logger: logging.Logger
    mcp_servers: Optional[List[MCPServer]]

    def __init__(
        self,
        logger: logging.Logger,
        model: str = DEFAULT_MODEL,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> None:
        self.model = model
        self.logger = logger
        self.mcp_servers = mcp_servers

    @staticmethod
    def get_model(model_id: Optional[str], logger: logging.Logger) -> Any:
        """
        Initialize an LLM model based on a standardized model_id string.
        Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
        """
        if not model_id or not isinstance(model_id, str):
            model_id = DEFAULT_MODEL

        parts = model_id.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid model_id '{model_id}'. Expected format 'provider/model_name'.")

        provider = parts[0].lower()
        # Azure: handle deployment name if present
        if provider == "azure":
            model_name = parts[1]
            deployment_name = parts[2] if len(parts) > 2 else None
            return get_azure_openai_model(
                logger=logger,
                model_name=model_name,
                deployment_name=deployment_name,
            )
        elif provider == "openai":
            model_name = parts[1]
            return OpenAIModel(model_name=model_name)
        elif provider == "anthropic":
            model_name = parts[1]
            return AnthropicModel(model_name=model_name)
        elif provider == "ollama":
            model_name = parts[1]
            return OpenAIModel(
                model_name=model_name,
                provider=OpenAIProvider(base_url=f"{OLLAMA_BASE_URL}/v1"),
            )
        else:
            raise ValueError(f"Unsupported provider '{provider}' in model_id '{model_id}'.")

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
        # Determine model id and mcp_servers to use
        model_id = model if model else self.model
        servers = mcp_servers if mcp_servers is not None else self.mcp_servers
        if servers is None:
            servers = []
        else:
            # Defend against mutable default list; always use a copy
            servers = list(servers)

        # Model initialization
        try:
            model_instance = self.get_model(model_id, self.logger)
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
            raise
        # Agent initialization
        agent = Agent(model=model_instance, output_type=output_type, mcp_servers=servers)
        # Logging: request payload
        self.logger.debug({
            "event": "llm_request",
            "prompt": prompt,
            "model": model_id,
            "output_type": str(output_type),
            "mcp_servers": [str(s) for s in servers],
        })
        # Logging: model/provider info
        self.logger.info(f"Requesting LLM (provider/model): {model_id}")
        start_time = time.monotonic()
        try:
            result = await agent.run(prompt)
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}", exc_info=True)
            raise
        duration = time.monotonic() - start_time
        # Log completion info
        usage = None
        try:
            usage = result.usage()
        except Exception:
            usage = None
        self.logger.info(
            f"LLM call finished: provider/model={model_id}, "
            f"duration={duration:.2f}s, "
            f"tokens={getattr(usage, 'total_tokens', '?') if usage else '?'}"
        )
        # Log result payload
        self.logger.debug({"event": "llm_result", "provider/model": model_id, "result": str(result.output)})
        return result.output
