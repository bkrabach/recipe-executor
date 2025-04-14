import logging
import os
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# Import model classes from pydantic_ai
from pydantic_ai.models.openai import OpenAIModel

from recipe_executor.models import FileGenerationResult


def get_model(model_id: Optional[str] = None):
    """
    Initialize and return an LLM model instance based on a standardized model identifier.
    Expected formats:
      - provider/model_name
      - provider/model_name/deployment_name  (for Azure OpenAI)
    Supported providers:
      - openai
      - azure (for Azure OpenAI models)
      - anthropic
      - ollama
      - gemini

    Args:
        model_id (Optional[str]): Model identifier. If None, defaults to environment variable DEFAULT_MODEL or 'openai/gpt-4o'.

    Returns:
        An instance of the corresponding model class from pydantic_ai.

    Raises:
        ValueError: If the model_id is invalid or if the provider is unsupported.
    """
    if not model_id:
        model_id = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
    parts = model_id.split("/")
    if len(parts) < 2:
        raise ValueError(
            "Invalid model id. Expected format 'provider/model_name' or 'provider/model_name/deployment_name'."
        )
    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "azure":
        # For Azure, if a third part is provided, it's the deployment name; otherwise, default to model_name
        from recipe_executor.llm_utils.azure_openai import get_azure_openai_model

        deployment_name = parts[2] if len(parts) >= 3 else model_name
        return get_azure_openai_model(model_name, deployment_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "ollama":
        # Ollama uses OpenAIModel with a custom provider; the endpoint is taken from OLLAMA_ENDPOINT env.
        from pydantic_ai.providers.openai import OpenAIProvider

        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        return OpenAIModel(model_name, provider=OpenAIProvider(base_url=f"{ollama_endpoint}/v1"))
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def call_llm(
    prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (Optional[str]): Model identifier in the format 'provider/model_name' or 'provider/model_name/deployment_name'. If None, defaults to 'openai/gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance. Defaults to a logger named 'RecipeExecutor'.

    Returns:
        FileGenerationResult: The structured result from the LLM containing generated files and optional commentary.

    Raises:
        Exception: Propagates any exceptions that occur during the LLM call.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    try:
        model_instance = get_model(model)
    except Exception as e:
        logger.error(f"Error initializing model: {e}")
        raise

    # Log info about model usage
    provider_name = model.split("/")[0] if model else "openai"
    model_name = model.split("/")[1] if model else "gpt-4o"
    logger.info(f"Calling LLM with provider='{provider_name}', model_name='{model_name}'")

    # Log debug payload
    logger.debug(f"LLM Request Payload: {prompt}")

    # Initialize the Agent with the model instance and specify the structured output type
    agent = Agent(model_instance, result_type=FileGenerationResult)

    # Make the asynchronous call
    result = await agent.run(prompt)

    # Log response and usage
    logger.debug(f"LLM Response Payload: {result.data}")
    logger.info(f"LLM call completed. Usage details: {result.usage()}")

    return result.data
