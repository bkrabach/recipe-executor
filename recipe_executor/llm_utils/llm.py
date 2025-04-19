import logging
import os
import time
from typing import List, Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel

from .azure_openai import get_azure_openai_model
from .mcp import MCPServer


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
            model (str): Model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                Default is "openai/gpt-4o".
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
        """
        self.model: str = model
        self.logger: logging.Logger = logger
        self.mcp_servers: Optional[List[MCPServer]] = mcp_servers

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.

        Args:
            prompt (str): The prompt string to be sent to the LLM.
            model (Optional[str]): The model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                If not provided, the default set during initialization will be used.
            output_type (Type[Union[str, BaseModel]]): The requested type for the LLM output.
                - str: Plain text output (default).
                - BaseModel: Structured output based on the provided JSON schema.
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
                If not provided, the default set during initialization will be used.
        Returns:
            Union[str, BaseModel]: The output from the LLM, either as plain text or structured data.
        Raises:
            Exception: If any of the following occurs:
                - Invalid model ID or format.
                - Unsupported provider.
                - MCP server errors.
                - Network or API errors.
                - JSON schema validation errors.
        """
        use_model: str = model or self.model
        use_mcp_servers: List[MCPServer] = mcp_servers if mcp_servers is not None else (self.mcp_servers or [])
        agent = None
        model_instance = None
        start_time = time.monotonic()
        # Step 1: Get model instance
        try:
            model_instance = get_model(use_model, self.logger)
        except Exception as e:
            self.logger.error(f"LLM: Failed to initialize model: {e}")
            raise
        self.logger.info(f"LLM: Using model '{use_model}'")
        self.logger.debug({
            "provider_model": use_model,
            "prompt": prompt,
            "output_type": output_type.__name__ if hasattr(output_type, "__name__") else str(output_type),
            "mcp_servers": [str(s) for s in use_mcp_servers],
        })
        # Step 2: Build agent
        agent = Agent(model=model_instance, mcp_servers=use_mcp_servers, output_type=output_type)
        # Step 3: Run agent
        try:
            result = await agent.run(prompt)
        except Exception as e:
            self.logger.error(f"LLM: Exception in agent.run: {e}")
            raise
        duration = time.monotonic() - start_time
        usage = None
        try:
            usage = result.usage() if hasattr(result, "usage") and callable(result.usage) else None
        except Exception as e:
            self.logger.debug(f"LLM: Failed to get usage: {e}")
        self.logger.debug({"response": repr(result)})
        if usage:
            self.logger.info(
                f"LLM: Completed call in {duration:.2f}s, tokens used: {getattr(usage, 'total_tokens', '?')}"
            )
        else:
            self.logger.info(f"LLM: Completed call in {duration:.2f}s")
        return result.output


def get_model(model_id: str, logger: logging.Logger):
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    Supported providers:
    - openai
    - azure (for Azure OpenAI, use 'azure/model_name/deployment_name' or 'azure/model_name')
    - anthropic
    - ollama
    Args:
        model_id (str): Model identifier in format 'provider/model_name' (or 'provider/model_name/deployment_name').
        logger (logging.Logger): Logger for error/info/debug logging.
    Returns:
        The model instance for the specified provider and model.
    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
    if not model_id or not isinstance(model_id, str):
        model_id = os.getenv("DEFAULT_MODEL") or "openai/gpt-4o"
    parts = model_id.strip().split("/")
    if len(parts) < 2:
        logger.error(
            f"Model id must have the format 'provider/model_name' or 'provider/model_name/deployment_name', got '{model_id}'."
        )
        raise ValueError(f"Invalid model_id format: '{model_id}'")
    provider = parts[0].lower()
    if provider == "openai":
        # openai/model_name
        return OpenAIModel(parts[1])
    elif provider == "anthropic":
        # anthropic/model_name
        return AnthropicModel(parts[1])
    elif provider == "azure":
        # azure/model_name or azure/model_name/deployment_name
        deployment_name = parts[2] if len(parts) > 2 else None
        return get_azure_openai_model(
            logger=logger,
            model_name=parts[1],
            deployment_name=deployment_name,
        )
    elif provider == "ollama":
        # ollama/model_name
        try:
            from pydantic_ai.providers.openai import OpenAIProvider

            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model_name = parts[1]
            return OpenAIModel(
                model_name=model_name,
                provider=OpenAIProvider(base_url=f"{base_url}/v1"),
            )
        except Exception as e:
            logger.error(f"Error initializing Ollama model: {e}")
            raise RuntimeError(f"Failed to initialize Ollama model: {e}")
    else:
        logger.error(f"Unsupported provider: '{provider}")
        raise ValueError(f"Unsupported provider: '{provider}'")
