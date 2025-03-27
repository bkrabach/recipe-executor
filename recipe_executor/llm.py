"""
LLM integration module for the Recipe Executor CLI tool.

This module provides a helper function to instantiate a language model
based on the provided model name. It currently supports OpenAI and Anthropic models.
"""

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models import Model

def get_model(model_name: str) -> Model:
    """
    Instantiate and return a language model based on the given model name.

    Supported models:
    - OpenAI: model names prefixed with "openai:" (e.g. "openai:gpt-4.5")
    - Anthropic: model names prefixed with "anthropic:"

    Args:
        model_name: A string that identifies the model along with its provider.

    Returns:
        An instance of a Model configured for the specified provider.

    Raises:
        ValueError: If the model provider is unsupported.
    """
    if model_name.startswith("openai:"):
        return OpenAIModel(model_name.removeprefix("openai:"))
    if model_name.startswith("anthropic:"):
        return AnthropicModel(model_name.removeprefix("anthropic:"))

    raise ValueError(f"Unsupported model provider for model: {model_name}")
