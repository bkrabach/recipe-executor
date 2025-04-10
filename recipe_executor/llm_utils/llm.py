import logging
import os
from typing import Optional

# Import LLM model classes from pydantic_ai
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel

# Azure OpenAI support - this should be provided via an internal module
from recipe_executor.llm_utils.azure_openai import get_openai_model

# Import structured models from the recipe_executor models module
from recipe_executor.models import FileGenerationResult

# Default model identifier. Falls back to 'openai:gpt-4o' if no environment variable DEFAULT_MODEL is found.
DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL", "openai:gpt-4o")


def get_model(model_id: Optional[str] = None):
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected formats:
      - 'openai:model_name'
      - 'azure:model_name' or 'azure:model_name:deployment_name'
      - 'anthropic:model_name'
      - 'gemini:model_name'

    If model_id is None, defaults to DEFAULT_MODEL_ID.

    Returns:
      An instance of a model interface from pydantic_ai.

    Raises:
      ValueError if the model_id format is invalid or if the provider is unsupported.
    """
    if model_id is None:
        model_id = DEFAULT_MODEL_ID

    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model id format: {model_id}")

    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "azure":
        # For Azure, if a deployment name is provided, use it; otherwise default to model_name
        deployment_name = model_name
        if len(parts) == 3:
            deployment_name = parts[2]
        return get_openai_model(model_name, deployment_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model using a structured output type of FileGenerationResult.

    Args:
      model_id: Model identifier string in the format 'provider:model' or 'provider:model:deployment'.
                If None, defaults to DEFAULT_MODEL_ID.

    Returns:
      An Agent configured for processing file generation requests.
    """
    model = get_model(model_id)
    agent = Agent(model, result_type=FileGenerationResult)
    return agent


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
      prompt: The prompt string to send to the LLM.
      model: The model identifier in the form 'provider:model' (or for Azure, 'azure:model:deployment').
             If None, defaults to DEFAULT_MODEL_ID.
      logger: Logger instance to use; if None, defaults to a logger named "RecipeExecutor".

    Returns:
      FileGenerationResult: The structured result containing generated files and commentary.

    Raises:
      Exception: If the LLM call fails.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    try:
        # Log the full request payload at the debug level
        logger.debug(f"LLM Request - model: {model or DEFAULT_MODEL_ID}, prompt: {prompt}")

        # Log basic model and provider info at info level
        parts = (model or DEFAULT_MODEL_ID).split(":")
        provider = parts[0] if parts else "unknown"
        model_name = parts[1] if len(parts) > 1 else "unknown"
        logger.info(f"Calling LLM with provider: {provider}, model: {model_name}")

        agent = get_agent(model)

        result = agent.run_sync(prompt)

        # Log the full response payload at debug level, including messages
        logger.debug(f"LLM Response Messages: {result.all_messages()}")

        try:
            usage = result.usage()
            logger.info(f"LLM call completed. Usage: {usage}")
        except Exception:
            pass

        # CRITICAL: Return the result's data
        return result.data
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}", exc_info=True)
        raise
