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


# MCP integration
def _get_default_ollama_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_model(model_id: Optional[str], logger: Optional[logging.Logger] = None) -> Any:
    """
    Initialize an LLM model based on a standardized model_id string.
    Format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    """
    if not model_id or not isinstance(model_id, str):
        model_id = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")

    if "/" not in model_id:
        raise ValueError(f"Invalid model_id format: '{model_id}'. Expected 'provider/model_name'.")

    parts = model_id.split("/")
    provider = parts[0].strip().lower()
    if provider == "openai":
        if len(parts) != 2:
            raise ValueError(f"Invalid openai model_id: '{model_id}'. Format is 'openai/model_name'.")
        model_name = parts[1]
        return OpenAIModel(model_name)
    elif provider == "azure":
        if len(parts) == 2:
            model_name = parts[1]
            deployment_name = None
        elif len(parts) == 3:
            model_name, deployment_name = parts[1], parts[2]
        else:
            raise ValueError(
                f"Invalid azure model_id: '{model_id}'. Format is 'azure/model_name' or 'azure/model_name/deployment_name'."
            )
        if logger is None:
            import logging as _logging

            logger = _logging.getLogger("llm")
        return get_azure_openai_model(logger=logger, model_name=model_name, deployment_name=deployment_name)
    elif provider == "anthropic":
        if len(parts) != 2:
            raise ValueError(f"Invalid anthropic model_id: '{model_id}'. Format is 'anthropic/model_name'.")
        model_name = parts[1]
        return AnthropicModel(model_name)
    elif provider == "ollama":
        if len(parts) != 2:
            raise ValueError(f"Invalid ollama model_id: '{model_id}'. Format is 'ollama/model_name'.")
        model_name = parts[1]
        endpoint = _get_default_ollama_url()
        return OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(base_url=f"{endpoint}/v1"),
        )
    else:
        raise ValueError(f"Unsupported provider: '{provider}'. Allowed: openai, azure, anthropic, ollama.")


class LLM:
    def __init__(
        self,
        logger: logging.Logger,
        model: str = "openai/gpt-4o",
        mcp_servers: Optional[List[Any]] = None,
    ):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            model (str): Model identifier.
            mcp_servers (Optional[List[MCPServer]]): List of MCP servers.
        """
        self.logger: logging.Logger = logger
        self.model: str = model
        self.mcp_servers: Optional[List[Any]] = mcp_servers if mcp_servers is not None else []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[Any]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        # Determine model_id and mcp_servers
        model_id: str = model if model is not None else self.model
        servers: List[Any] = mcp_servers if mcp_servers is not None else self.mcp_servers or []
        logger = self.logger
        # Prepare model and agent
        try:
            start_time = time.time()
            mdl = get_model(model_id, logger=logger)
            logger.info(f"LLM Call - provider/model: {model_id}")
            logger.debug(
                f"LLM request payload: prompt={repr(prompt)}, mcp_servers={[str(s) for s in servers]}, output_type={output_type}"
            )
            agent = Agent(
                model=mdl,
                output_type=output_type,
                mcp_servers=servers,
            )
            result = await agent.run(prompt)
            elapsed = time.time() - start_time
            # Try to fetch usage if possible
            usage = None
            tokens_used = None
            try:
                if hasattr(result, "usage"):
                    usage = result.usage()
                    if usage:
                        tokens_used = usage.total_tokens if hasattr(usage, "total_tokens") else None
            except Exception:
                tokens_used = None
            logger.info(
                f"LLM call finished (model: {model_id}) in {elapsed:.2f}s"
                + (f", tokens used: {tokens_used}" if tokens_used is not None else "")
            )
            logger.debug(f"LLM result payload: {result}")
            return result.output
        except Exception as exc:
            logger.error(f"LLM call failed with error: {str(exc)}", exc_info=True)
            raise
