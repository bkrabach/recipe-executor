import logging
import os
from typing import Optional

from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Helper to mask API key in logs except first/last char


def _mask_api_key(key: str) -> str:
    if not key or len(key) <= 2:
        return "*" * len(key)
    return key[0] + ("*" * (len(key) - 2)) + key[-1]


def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str] = None,
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from environment variables for Azure OpenAI.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name (str): Model name, such as "gpt-4o" or "o3-mini".
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance created from AsyncAzureOpenAI client.

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
    env = os.environ
    AZURE_USE_MANAGED_IDENTITY = env.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() in {"true", "1", "yes"}
    AZURE_OPENAI_API_KEY = env.get("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_BASE_URL = env.get("AZURE_OPENAI_BASE_URL")
    AZURE_OPENAI_API_VERSION = env.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    AZURE_MANAGED_IDENTITY_CLIENT_ID = env.get("AZURE_MANAGED_IDENTITY_CLIENT_ID")
    AZURE_CLIENT_ID = env.get("AZURE_CLIENT_ID")
    # Keep support for both, prefer explicit AZURE_MANAGED_IDENTITY_CLIENT_ID
    client_id = AZURE_MANAGED_IDENTITY_CLIENT_ID or AZURE_CLIENT_ID

    # Deployment name defaults to model_name if not provided
    azure_deployment = deployment_name or env.get("AZURE_OPENAI_DEPLOYMENT_NAME") or model_name

    # Debug logging with masking
    masked_api_key = _mask_api_key(AZURE_OPENAI_API_KEY or "")
    logger.debug(f"AZURE_USE_MANAGED_IDENTITY={AZURE_USE_MANAGED_IDENTITY}")
    logger.debug(f"AZURE_OPENAI_API_KEY={masked_api_key}")
    logger.debug(f"AZURE_OPENAI_BASE_URL={AZURE_OPENAI_BASE_URL}")
    logger.debug(f"AZURE_OPENAI_API_VERSION={AZURE_OPENAI_API_VERSION}")
    logger.debug(f"AZURE_MANAGED_IDENTITY_CLIENT_ID={client_id}")
    logger.debug(f"AZURE_OPENAI_DEPLOYMENT={azure_deployment}")

    # Validate required config
    if not AZURE_OPENAI_BASE_URL:
        logger.error("AZURE_OPENAI_BASE_URL is required for Azure OpenAI initialization.")
        raise RuntimeError("AZURE_OPENAI_BASE_URL is required.")
    if not azure_deployment:
        logger.error(
            "A deployment name must be specified via deployment_name, AZURE_OPENAI_DEPLOYMENT_NAME, or model_name."
        )
        raise RuntimeError("Azure OpenAI deployment name is required.")

    try:
        if AZURE_USE_MANAGED_IDENTITY:
            # Azure Identity authentication
            if client_id:
                logger.info("Using Azure Managed Identity authentication (user-assigned managed identity)")
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                logger.info("Using Azure DefaultAzureCredential for Azure Identity authentication")
                credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
            azure_client = AsyncAzureOpenAI(
                azure_endpoint=AZURE_OPENAI_BASE_URL,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_deployment=azure_deployment,
                azure_ad_token_provider=token_provider,
            )
            auth_method = "azure_identity"
        else:
            # API key authentication
            if not AZURE_OPENAI_API_KEY:
                logger.error("AZURE_OPENAI_API_KEY is required when not using managed identity.")
                raise RuntimeError("AZURE_OPENAI_API_KEY is required.")
            logger.info("Using API key authentication for Azure OpenAI")
            azure_client = AsyncAzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                azure_endpoint=AZURE_OPENAI_BASE_URL,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_deployment=azure_deployment,
            )
            auth_method = "api_key"
        provider = OpenAIProvider(openai_client=azure_client)
        openai_model = OpenAIModel(model_name, provider=provider)
        logger.info(
            f"Initialized Azure OpenAI OpenAIModel: model_name={model_name} deployment_name={azure_deployment} auth_method={auth_method}"
        )
        return openai_model
    except Exception as exc:
        logger.debug(f"Error during Azure OpenAI model initialization: {exc}", exc_info=True)
        raise
