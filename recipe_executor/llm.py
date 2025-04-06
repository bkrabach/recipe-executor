import logging
import time
from typing import Optional

# Import the required PydanticAI Agent and LLM model classes
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel

# For Azure OpenAI, import our utility function
from recipe_executor.llm_utils.azure_openai import get_openai_model

# Import the structured output model
from recipe_executor.models import FileGenerationResult


def get_model(model_id: Optional[str] = None):
    """
    Initialize an LLM model instance based on a standardized model_id string.
    Expected formats:
      provider:model_name
      For Azure OpenAI, an optional deployment name may be provided:
         azure:model_name:deployment_name

    Supported providers:
      - openai
      - anthropic
      - gemini
      - azure

    Args:
        model_id (Optional[str]): Model identifier, defaults to "openai:gpt-4o" if not provided.

    Returns:
        An instance of the corresponding LLM model class.

    Raises:
        ValueError: If the model identifier format is invalid or provider unsupported.
    """
    if not model_id:
        model_id = "openai:gpt-4o"
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model id format: {model_id}")
    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "azure":
        deployment = parts[2] if len(parts) >= 3 else model_name
        return get_openai_model(model_name, deployment)
    elif provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Create an Agent instance configured with the specified LLM model and structured output type.
    If no model_id is provided, it defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A PydanticAI agent with the correct model and result type.
    """
    model = get_model(model_id)
    return Agent(model, result_type=FileGenerationResult)


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the provided prompt and return a structured FileGenerationResult.

    Logs:
      - At INFO level: model provider and model identifier, response time and usage summary.
      - At DEBUG level: full prompt payload and full response payload.

    Args:
        prompt (str): The text prompt to be sent to the LLM.
        model (Optional[str]): Model identifier in the format 'provider:model_name' (or with deployment for azure).
                              Defaults to 'openai:gpt-4o' if not provided.
        logger (Optional[logging.Logger]): The logger instance; if not provided, a logger named 'RecipeExecutor' is used.

    Returns:
        FileGenerationResult: Structured result as defined in the models component.

    Raises:
        Exception: Propagates exceptions encountered during the LLM call.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    try:
        model_id = model if model else "openai:gpt-4o"
        parts = model_id.split(":")
        provider = parts[0].lower() if parts else "openai"
        logger.info(f"Calling LLM with provider '{provider}' and model_id '{model_id}'")
        logger.debug(f"Prompt payload: {prompt}")

        agent_instance = get_agent(model_id)
        start_time = time.time()
        result = agent_instance.run_sync(prompt)
        elapsed = time.time() - start_time
        usage_info = result.usage() if hasattr(result, "usage") else "N/A"

        logger.info(f"LLM call completed in {elapsed:.2f} seconds. Usage: {usage_info}")
        logger.debug(f"Full response: {result}")

        # Return only the data portion of the result
        return result.data
    except Exception as e:
        logger.error("Error during LLM call", exc_info=True)
        raise e
