import logging
import time
from typing import Optional

# Import necessary models from pydantic-ai library
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# Import our structured output models
from recipe_executor.models import FileGenerationResult


def get_model(model_id: Optional[str] = None):
    """
    Initialize and return a PydanticAI model instance based on the model_id string.
    Expected format: "provider:model" or "provider:model:deployment".

    Supported providers:
      - openai
      - anthropic
      - gemini
      - azure (which will use the Azure OpenAI model via our azure provider) 

    Args:
        model_id (Optional[str]): A string in the format 'provider:model' or 'provider:model:deployment'.
                                  Defaults to 'openai:gpt-4o' if not provided.

    Returns:
        An instance of the corresponding PydanticAI model.

    Raises:
        ValueError: If the model identifier is invalid or the provider is unsupported.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError("Invalid model id. Expected format 'provider:model' or 'provider:model:deployment'.")
    
    provider = parts[0].lower()
    model_name = parts[1]
    
    if provider == "azure":
        # For Azure, if a deployment name is provided, use it; otherwise default to model name
        deployment = parts[2] if len(parts) >= 3 else model_name
        # Import the Azure OpenAI model initializer from our azure module
        from recipe_executor.llm_utils.azure_openai import get_openai_model as get_azure_openai_model
        return get_azure_openai_model(model_name, deployment)
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
    Initialize an LLM agent with the specified model using structured output.

    Args:
        model_id (Optional[str]): Model identifier in the format 'provider:model' or 'provider:model:deployment'.
                                  Defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: An agent configured to return a FileGenerationResult.
    """
    model = get_model(model_id)
    # Create an agent with the provided model and using FileGenerationResult as the structured result type
    agent = Agent(model, result_type=FileGenerationResult)
    return agent


async def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return the structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to send to the LLM.
        model (Optional[str]): Model identifier in the format 'provider:model' or 'provider:model:deployment'.
                               Defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance. Defaults to a logger named "RecipeExecutor".

    Returns:
        FileGenerationResult: The result data containing generated files and commentary.

    Raises:
        Exception: If the LLM call fails or result validation fails.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")
    
    resolved_model = model if model is not None else "openai:gpt-4o"
    logger.info(f"Calling LLM with model: {resolved_model}")
    logger.debug(f"LLM request payload: {prompt}")
    
    agent = get_agent(model)
    try:
        start_time = time.monotonic()
        result = await agent.run(prompt)
        duration = time.monotonic() - start_time
        usage = result.usage() if hasattr(result, 'usage') else None
        token_info = usage.total_tokens if usage and hasattr(usage, 'total_tokens') else "n/a"
        logger.info(f"LLM responded in {duration:.2f}s. Tokens used: {token_info}")
        return result.data
    except Exception as e:
        logger.error("LLM call failed", exc_info=True)
        raise e
