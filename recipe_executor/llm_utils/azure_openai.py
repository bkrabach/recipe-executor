import os
import logging
from typing import Optional

from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider

# Constants
_DEFAULT_API_VERSION = "2025-03-01-preview"
_AZURE_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


def _mask_api_key(api_key: Optional[str]) -> str:
    if not api_key:
        return ""  # pragma: nocover
    if len(api_key) <= 6:
        return api_key[0] + "***" + api_key[-1]
    return api_key[:2] + "***" + api_key[-2:]


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
    use_managed_identity = env.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
    api_key = env.get("AZURE_OPENAI_API_KEY")
    base_url = env.get("AZURE_OPENAI_BASE_URL") or env.get("AZURE_OPENAI_ENDPOINT")
    version = env.get("AZURE_OPENAI_API_VERSION", _DEFAULT_API_VERSION)
    env_deployment = env.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    managed_identity_client_id = (
        env.get("AZURE_MANAGED_IDENTITY_CLIENT_ID") or env.get("AZURE_CLIENT_ID")
    )

    deployment = deployment_name or env_deployment or model_name

    # Log environment variables with masking
    logger.debug(
        "AZURE_USE_MANAGED_IDENTITY=%r, AZURE_OPENAI_API_KEY=%s, AZURE_OPENAI_BASE_URL=%r, AZURE_OPENAI_API_VERSION=%r, AZURE_OPENAI_DEPLOYMENT_NAME=%r, AZURE_MANAGED_IDENTITY_CLIENT_ID=%r, AZURE_CLIENT_ID=%r",
        use_managed_identity,
        _mask_api_key(api_key),
        base_url,
        version,
        deployment,
        env.get("AZURE_MANAGED_IDENTITY_CLIENT_ID"),
        env.get("AZURE_CLIENT_ID"),
    )

    if not base_url:
        logger.error("AZURE_OPENAI_BASE_URL or AZURE_OPENAI_ENDPOINT must be set.")
        raise RuntimeError("Missing environment variable: AZURE_OPENAI_BASE_URL or AZURE_OPENAI_ENDPOINT.")
    if not deployment:
        logger.error("AZURE_OPENAI_DEPLOYMENT_NAME or model_name must be set.")
        raise RuntimeError("Missing deployment name for Azure OpenAI.")

    try:
        if use_managed_identity:
            logger.info(
                "Creating Azure OpenAI client using Azure Identity (managed identity%s) for deployment '%s' (model '%s').", 
                f' (client_id={managed_identity_client_id})' if managed_identity_client_id else '',
                deployment, model_name
            )
            # Pick which credential to use
            if managed_identity_client_id:
                credential = DefaultAzureCredential(managed_identity_client_id=managed_identity_client_id)
            else:
                credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(credential, _AZURE_COGNITIVE_SCOPE)
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=base_url,
                api_version=version,
                azure_deployment=deployment,
            )
            auth_method = f'managed_identity (client_id={managed_identity_client_id or "default"})'

        else:
            if not api_key:
                logger.error("AZURE_OPENAI_API_KEY must be set for API key authentication.")
                raise RuntimeError("Missing environment variable: AZURE_OPENAI_API_KEY.")
            logger.info(
                "Creating Azure OpenAI client using API key for deployment '%s' (model '%s').",
                deployment, model_name
            )
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=base_url,
                api_version=version,
                azure_deployment=deployment,
            )
            auth_method = 'api_key'

        provider = OpenAIProvider(openai_client=azure_client)
        openai_model = OpenAIModel(model_name, provider=provider)
        logger.info(
            "Azure OpenAIModel created successfully (model='%s', deployment='%s', auth_method='%s').",
            model_name, deployment, auth_method
        )
        return openai_model
    except Exception as exc:
        logger.debug(f"Failed to create Azure OpenAIModel: {exc}", exc_info=True)
        logger.error(f"Could not create Azure OpenAI model ('{model_name}'): {exc}")
        raise
