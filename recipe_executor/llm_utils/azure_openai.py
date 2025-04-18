import logging
import os
from typing import Optional

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def mask_secret(secret: str) -> str:
    if not secret or len(secret) < 4:
        return "***"
    return f"{secret[:2]}***{secret[-2:]}"


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
    # Load and validate environment variables
    use_managed_identity: bool = os.environ.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() in {"true", "1", "yes"}
    api_key: Optional[str] = os.environ.get("AZURE_OPENAI_API_KEY")
    base_url: Optional[str] = os.environ.get("AZURE_OPENAI_BASE_URL")
    api_version: str = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    deployment_env: Optional[str] = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    client_id: Optional[str] = os.environ.get("AZURE_MANAGED_IDENTITY_CLIENT_ID") or os.environ.get("AZURE_CLIENT_ID")

    # Determine deployment
    deployment: str = deployment_name or deployment_env or model_name

    # Debug logging: show env vars (mask secrets)
    logger.debug(
        f"AZURE_USE_MANAGED_IDENTITY={use_managed_identity}\n"
        f"AZURE_OPENAI_API_KEY={mask_secret(api_key) if api_key else None}\n"
        f"AZURE_OPENAI_BASE_URL={base_url}\n"
        f"AZURE_OPENAI_API_VERSION={api_version}\n"
        f"AZURE_OPENAI_DEPLOYMENT_NAME={deployment}\n"
        f"AZURE_MANAGED_IDENTITY_CLIENT_ID={mask_secret(client_id) if client_id else None}"
    )

    # Validate required variables
    if not base_url:
        logger.error("AZURE_OPENAI_BASE_URL environment variable must be set.")
        raise ValueError("AZURE_OPENAI_BASE_URL environment variable must be set.")

    if use_managed_identity:
        try:
            # Auth: Azure Identity (Managed or Default)
            if client_id:
                credential = DefaultAzureCredential(managed_identity_client_id=client_id)
                logger.debug("Using DefaultAzureCredential with managed_identity_client_id=%s", mask_secret(client_id))
            else:
                credential = DefaultAzureCredential()
                logger.debug("Using DefaultAzureCredential (system-assigned managed identity or developer login)")
            # Create token provider
            token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=base_url,
                api_version=api_version,
                azure_deployment=deployment,
            )
            auth_method = f"Azure Identity (managed{' with client_id' if client_id else ''})"
            logger.info(f"Azure OpenAI model '{model_name}' initialized using Azure Identity.")
        except Exception as e:
            logger.debug(f"Failed to authenticate Azure OpenAI with Azure Identity: {e}")
            raise
    else:
        # Auth: API key
        if not api_key:
            logger.error("AZURE_OPENAI_API_KEY environment variable must be set if not using managed identity.")
            raise ValueError("AZURE_OPENAI_API_KEY environment variable must be set if not using managed identity.")
        try:
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=base_url,
                api_version=api_version,
                azure_deployment=deployment,
            )
            auth_method = "API key"
            logger.info(f"Azure OpenAI model '{model_name}' initialized using API key.")
        except Exception as e:
            logger.debug(f"Failed to initialize AsyncAzureOpenAI with API key: {e}")
            raise

    try:
        provider = OpenAIProvider(openai_client=azure_client)
        openai_model = OpenAIModel(model_name, provider=provider)
        logger.info(f"OpenAIModel for '{model_name}' created with provider={auth_method}, deployment='{deployment}'.")
        return openai_model
    except Exception as e:
        logger.debug(f"Failed to create OpenAIModel: {e}")
        raise
