import logging
import os
from typing import Optional

import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def _mask_api_key(api_key: str) -> str:
    """Return a masked version of the API key, showing only the first and last characters."""
    if len(api_key) <= 4:
        return api_key
    return api_key[0] + "*" * (len(api_key) - 2) + api_key[-1]


def get_openai_model(
    model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance configured to use Azure OpenAI.

    This function loads configuration from environment variables. It supports two authentication methods:
    - API key authentication using AZURE_OPENAI_API_KEY
    - Managed Identity authentication if AZURE_USE_MANAGED_IDENTITY is set

    Environment Variables:
    - AZURE_OPENAI_ENDPOINT: URL for the Azure OpenAI service (required)
    - AZURE_OPENAI_API_VERSION: API version (default: "2025-03-01-preview")
    - AZURE_OPENAI_DEPLOYMENT_NAME: Deployment name (optional, defaults to model_name if not provided)
    - AZURE_USE_MANAGED_IDENTITY: If set to true ("true", "1", or "yes"), uses Managed Identity authentication
    - AZURE_MANAGED_IDENTITY_CLIENT_ID: (Optional) Client ID for managed identity
    - AZURE_OPENAI_API_KEY: API key for Azure OpenAI (required if not using managed identity)

    Args:
        model_name (str): The name of the OpenAI model (e.g. "gpt-4o")
        deployment_name (Optional[str]): Optional deployment name; defaults to AZURE_OPENAI_DEPLOYMENT_NAME or model_name
        logger (Optional[logging.Logger]): Logger instance; if not provided, defaults to a logger named "RecipeExecutor"

    Returns:
        OpenAIModel: A configured instance of OpenAIModel using Azure OpenAI

    Raises:
        ValueError: If required environment variables are missing.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Load required environment variables
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise ValueError("Missing required environment variable: AZURE_OPENAI_ENDPOINT")

    azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    deployment = deployment_name or os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", model_name)

    logger.debug(f"Azure OpenAI Endpoint: {azure_endpoint}")
    logger.debug(f"Azure API Version: {azure_api_version}")
    logger.debug(f"Azure Deployment: {deployment}")

    use_managed_identity = os.environ.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("true", "1", "yes")

    if use_managed_identity:
        logger.info("Using Azure Managed Identity for authentication.")
        client_id = os.environ.get("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        if client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            credential = DefaultAzureCredential()
        scope = "https://cognitiveservices.azure.com/.default"
        token_provider = get_bearer_token_provider(credential, scope)

        azure_client = openai.AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version=azure_api_version,
            azure_deployment=deployment,
            azure_ad_token_provider=token_provider,
        )
    else:
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing required environment variable: AZURE_OPENAI_API_KEY when not using managed identity"
            )
        logger.info("Using Azure OpenAI API key for authentication.")
        masked_key = _mask_api_key(api_key)
        logger.debug(f"Azure API Key: {masked_key}")

        azure_client = openai.AsyncAzureOpenAI(
            api_key=api_key, azure_endpoint=azure_endpoint, api_version=azure_api_version, azure_deployment=deployment
        )

    provider = OpenAIProvider(openai_client=azure_client)
    model = OpenAIModel(model_name, provider=provider)

    logger.info(f"Azure OpenAI model '{model_name}' created successfully using deployment '{deployment}'.")
    return model
