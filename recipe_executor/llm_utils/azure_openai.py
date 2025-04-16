import logging
import os
from typing import Optional

from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


# Azure Identity dependencies are only needed if using managed identity
def _get_azure_token_provider(logger: logging.Logger, client_id: Optional[str]):
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider

        # Use managed_identity_client_id if provided, else default logic
        if client_id:
            logger.debug("Using DefaultAzureCredential with managed_identity_client_id=%s", client_id)
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            logger.debug("Using DefaultAzureCredential (no client_id)")
            credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
        return token_provider
    except ImportError as e:
        logger.error("azure-identity is not installed: %s", e)
        raise
    except Exception as exc:
        logger.debug(f"Error setting up Azure Identity token provider: {exc}")
        raise


def _mask_key(key: Optional[str]) -> str:
    if not key or len(key) < 5:
        return "<none>"
    return f"{key[0]}***{key[-1]}"


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
    use_managed_identity: str = os.getenv("AZURE_USE_MANAGED_IDENTITY", "").lower()
    use_identity: bool = use_managed_identity == "true" or use_managed_identity == "1"
    azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    azure_openai_deployment_name: Optional[str] = (
        deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or model_name
    )
    azure_client_id: Optional[str] = os.getenv("AZURE_CLIENT_ID") or os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")

    # Log environment values at debug (mask API key)
    logger.debug(
        "Azure OpenAI env: USE_MANAGED_IDENTITY=%s ENDPOINT=%s API_VERSION=%s DEPLOYMENT_NAME=%s CLIENT_ID=%s API_KEY=%s",
        use_managed_identity,
        azure_openai_endpoint,
        azure_openai_api_version,
        azure_openai_deployment_name,
        azure_client_id,
        _mask_key(azure_openai_api_key),
    )

    # Validate required values
    if not azure_openai_endpoint:
        logger.error("AZURE_OPENAI_ENDPOINT is required.")
        raise RuntimeError("AZURE_OPENAI_ENDPOINT is required")
    if not azure_openai_deployment_name:
        logger.error("Deployment name is required.")
        raise RuntimeError("Azure OpenAI deployment name is required")

    try:
        if use_identity:
            logger.info(
                "Initializing Azure OpenAI model='%s' using Azure Identity (managed identity) (client_id=%s)",
                model_name,
                azure_client_id,
            )
            token_provider = _get_azure_token_provider(logger, azure_client_id)
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=azure_openai_endpoint,
                api_version=azure_openai_api_version,
                azure_deployment=azure_openai_deployment_name,
            )
        else:
            if not azure_openai_api_key:
                logger.error("AZURE_OPENAI_API_KEY is required when not using managed identity.")
                raise RuntimeError("AZURE_OPENAI_API_KEY is required when not using managed identity")
            logger.info(
                "Initializing Azure OpenAI model='%s' using API key (deployment='%s')",
                model_name,
                azure_openai_deployment_name,
            )
            azure_client = AsyncAzureOpenAI(
                api_key=azure_openai_api_key,
                azure_endpoint=azure_openai_endpoint,
                api_version=azure_openai_api_version,
                azure_deployment=azure_openai_deployment_name,
            )

        provider = OpenAIProvider(openai_client=azure_client)
        model = OpenAIModel(model_name, provider=provider)
        logger.info(
            "Azure OpenAI OpenAIModel initialized for model=%s deployment=%s", model_name, azure_openai_deployment_name
        )
        return model
    except Exception as exc:
        logger.debug(f"Failed to create Azure OpenAI model: {exc}")
        raise
