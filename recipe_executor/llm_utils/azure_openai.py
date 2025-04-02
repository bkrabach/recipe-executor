import os
import logging
from typing import Optional

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key by revealing only the first and last character.
    For example, 'abcd1234' becomes 'a******4'.
    """
    if not api_key:
        return ""
    if len(api_key) <= 4:
        return '*' * len(api_key)
    return api_key[0] + ('*' * (len(api_key) - 2)) + api_key[-1]



def get_openai_model(model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance configured for Azure OpenAI.

    The method determines the authentication method based on environment variables:
      - If AZURE_USE_MANAGED_IDENTITY is set to true (or '1'), it uses Azure Identity for authentication.
      - Otherwise, it uses the AZURE_OPENAI_API_KEY for API key authentication.

    Required Environment Variables:
      - AZURE_OPENAI_ENDPOINT
      - AZURE_OPENAI_API_VERSION (optional, defaults to '2025-03-01-preview')
      - AZURE_OPENAI_DEPLOYMENT_NAME (optional, fallback to model_name if not provided)

    For API key authentication (if not using managed identity):
      - AZURE_OPENAI_API_KEY

    For Managed Identity authentication:
      - AZURE_USE_MANAGED_IDENTITY (set to true or 1)
      - Optionally, AZURE_MANAGED_IDENTITY_CLIENT_ID

    Args:
        model_name (str): Name of the model (e.g., 'gpt-4o').
        deployment_name (Optional[str]): Custom deployment name, defaults to environment var or model_name.
        logger (Optional[logging.Logger]): Logger instance, defaults to a logger named 'RecipeExecutor'.

    Returns:
        OpenAIModel: Configured for Azure OpenAI.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Load required environment variables
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise Exception("Missing required environment variable: AZURE_OPENAI_ENDPOINT")

    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    env_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    deployment = deployment_name or env_deployment or model_name

    # Determine authentication method
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ["true", "1"]

    if use_managed_identity:
        # Use Azure Identity
        try:
            managed_identity_client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
            if managed_identity_client_id:
                credential = ManagedIdentityCredential(client_id=managed_identity_client_id)
                logger.info("Using ManagedIdentityCredential with client id.")
            else:
                credential = DefaultAzureCredential()
                logger.info("Using DefaultAzureCredential for Managed Identity.")
        except Exception as ex:
            logger.error("Failed to create Azure Credential: %s", ex)
            raise

        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

        try:
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment
            )
            logger.info("Initialized Azure OpenAI client with Managed Identity.")
        except Exception as ex:
            logger.error("Error initializing AsyncAzureOpenAI client with Managed Identity: %s", ex)
            raise
    else:
        # Use API key authentication
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not azure_api_key:
            raise Exception("Missing required environment variable: AZURE_OPENAI_API_KEY")
        masked_key = mask_api_key(azure_api_key)
        logger.info("Initializing Azure OpenAI client with API Key: %s", masked_key)

        try:
            azure_client = AsyncAzureOpenAI(
                api_key=azure_api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment
            )
            logger.info("Initialized Azure OpenAI client with API Key.")
        except Exception as ex:
            logger.error("Error initializing AsyncAzureOpenAI client with API key: %s", ex)
            raise

    # Create the provider and model instance
    provider = OpenAIProvider(openai_client=azure_client)
    model_instance = OpenAIModel(model_name, provider=provider)
    logger.info("Created OpenAIModel instance for model '%s' using deployment '%s'", model_name, deployment)
    return model_instance
