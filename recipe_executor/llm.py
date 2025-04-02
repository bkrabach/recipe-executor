import logging
import time
from typing import Optional

# Import the required pydantic-ai models and Agent
from pydantic_ai import Agent

# Import the LLM model classes
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# Import the FileGenerationResult (structured output) model from the models component
# (Assuming it is defined in recipe_executor/models.py)
from recipe_executor.models import FileGenerationResult


# For Azure OpenAI, use the get_openai_model function from our azure utility module
from recipe_executor.llm_utils.azure_openai import get_openai_model


def get_model(model_id: Optional[str] = None):
    """
    Initialize an LLM model instance based on a standardized model_id string.
    Expected format:
      provider:model_name
      For Azure OpenAI, you can additionally supply a deployment name, e.g.,
         azure:model_name:deployment_name
    If model_id is None, it will default to 'openai:gpt-4o'.

    Supported providers:
      - openai
      - anthropic
      - gemini
      - azure

    Returns:
      An instance of the appropriate LLM model class.
    
    Raises:
      ValueError: If the model_id format is invalid or provider is unsupported.
    """
    if not model_id:
        model_id = "openai:gpt-4o"
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model id format: {model_id}")
    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "azure":
        # For Azure, we allow an optional deployment name; if not provided, default to model_name
        deployment = parts[2] if len(parts) >= 3 else model_name
        return get_openai_model(model_name, deployment)
    elif provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Create and return an Agent instance configured with the specified LLM model and structured output type.
    If no model_id is provided, it defaults to 'openai:gpt-4o'.

    Returns:
      Agent with the LLM model and result_type set to FileGenerationResult.
    """
    model = get_model(model_id)
    # Create the agent with the chosen model and specifying FileGenerationResult as the structured output type
    return Agent(model, result_type=FileGenerationResult)


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or 'provider:model_name:deployment_name').
            If not provided, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): A logger instance; if None, one named 'RecipeExecutor' is used.

    Returns:
        FileGenerationResult: The structured result from the LLM call.

    Raises:
        Exception: Propagates exceptions encountered during the LLM call.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    try:
        model_id = model if model else "openai:gpt-4o"
        parts = model_id.split(":")
        provider = parts[0] if parts else "openai"
        logger.info(f"Calling LLM: provider={provider}, model_id={model_id}")
        logger.debug(f"Prompt payload: {prompt}")

        agent = get_agent(model_id)
        start_time = time.time()
        result = agent.run_sync(prompt)
        elapsed = time.time() - start_time
        logger.info(f"LLM call completed in {elapsed:.2f} seconds")
        logger.debug(f"Full response: {result}")
        # Return the data portion of the result
        return result.data
    except Exception as e:
        logger.error("Error calling LLM", exc_info=True)
        raise e
