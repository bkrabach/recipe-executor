import logging
import os
from typing import Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model


def get_model(model_id: Optional[str], logger: logging.Logger) -> Union[OpenAIModel, AnthropicModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    Supported:
    - openai
    - azure
    - anthropic
    - ollama

    Raises:
        ValueError for invalid or unsupported model.
    """
    if not model_id:
        model_id = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
    parts = model_id.split("/")
    if not parts or len(parts) < 2:
        raise ValueError(f"Invalid model_id format: {model_id}. Expected 'provider/model_name'.")
    provider, model_name = parts[0].lower(), parts[1]
    # Azure OpenAI
    if provider == "azure":
        deployment_name: Optional[str] = parts[2] if len(parts) > 2 else None
        return get_azure_openai_model(model_name=model_name, logger=logger, deployment_name=deployment_name)
    # OpenAI
    if provider == "openai":
        return OpenAIModel(model_name)
    # Anthropic
    if provider == "anthropic":
        return AnthropicModel(model_name)
    # Ollama
    if provider == "ollama":
        endpoint: str = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        return OpenAIModel(model_name=model_name, provider=OpenAIProvider(base_url=f"{endpoint}/v1"))
    raise ValueError(f"Unsupported LLM provider: {provider} in model_id {model_id}")


class LLM:
    def __init__(self, logger: logging.Logger, model: str = "openai/gpt-4o"):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            model (str): Model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                Default is "openai/gpt-4o".
        """
        self.model: str = model
        self.logger: logging.Logger = logger

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
    ) -> Union[str, BaseModel]:
        """
        Generate a response from the LLM based on the provided prompt.

        Args:
            prompt (str): The prompt string to be sent to the LLM.
            model (Optional[str]): The model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
            output_type (Type[Union[str, BaseModel]]): The requested output type for the LLM response.

        Returns:
            Union[str, BaseModel]: The response from the LLM, either as plain text or structured data.

        Raises:
            Exception: If model value cannot be mapped to valid provider/model_name , LLM call fails, or result validation fails.
        """
        model_id = model or self.model
        try:
            llm_model = get_model(model_id, self.logger)
        except Exception as e:
            self.logger.error(f"Failed to get model for {model_id}: {str(e)}")
            raise

        agent: Agent[None, Union[str, BaseModel]] = Agent(model=llm_model, output_type=output_type)

        self.logger.info(f"LLM call to provider/model: {model_id}")
        self.logger.debug(f"LLM request payload: prompt={prompt!r}, output_type={output_type}")
        import time

        start = time.perf_counter()
        try:
            result = await agent.run(prompt)
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}", exc_info=True)
            raise
        finally:
            elapsed = time.perf_counter() - start
            # tokens used/info may not be available on failure

        self.logger.debug(f"LLM response payload: {getattr(result, 'data', None)!r}")
        usage = None
        tokens_info = ""
        try:
            usage = result.usage()
            tokens_info = (
                f" | requests={usage.requests}, request_tokens={usage.request_tokens}, response_tokens={usage.response_tokens}"
                if usage
                else ""
            )
        except Exception:
            pass
        self.logger.info(f"LLM completed in {elapsed:.2f}s{tokens_info}")
        return result.data
