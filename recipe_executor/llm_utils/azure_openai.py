import logging
import os
from typing import Optional

from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


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
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("1", "true", "yes")
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_base_url = os.getenv("AZURE_OPENAI_BASE_URL")
    azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    azure_openai_deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or model_name
    azure_client_id = os.getenv("AZURE_CLIENT_ID") or os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")

    # --- Mask API key for logging debug
    def mask(s: Optional[str]) -> str:
        if not s:
            return "(not set)"
        return s[0] + "*" * (len(s) - 2) + s[-1] if len(s) > 2 else "**"

    # Debug: log env vars used (masking key)
    logger.debug(
        "Azure OpenAI config: use_managed_identity=%s, api_key=%s, endpoint=%s, api_version=%s, deployment_name=%s, client_id=%s",
        use_managed_identity,
        mask(azure_openai_api_key),
        azure_openai_base_url,
        azure_openai_api_version,
        azure_openai_deployment_name,
        mask(azure_client_id),
    )

    if not azure_openai_base_url:
        logger.error("AZURE_OPENAI_BASE_URL is required.")
        raise RuntimeError("AZURE_OPENAI_BASE_URL environment variable is required.")

    if not azure_openai_deployment_name:
        logger.error("AZURE_OPENAI_DEPLOYMENT_NAME is required or must be provided as deployment_name arg.")
        raise RuntimeError("AZURE_OPENAI_DEPLOYMENT_NAME environment variable or deployment_name arg is required.")

    try:
        if use_managed_identity:
            logger.info("Using Azure Identity authentication for Azure OpenAI.")
            try:
                from azure.identity import DefaultAzureCredential, get_bearer_token_provider
            except ImportError as err:
                logger.error("azure-identity library not installed or missing: %s", err)
                raise

            # If using a custom client id, pass it; else default
            credential_kwargs = {}
            if azure_client_id:
                credential_kwargs["managed_identity_client_id"] = azure_client_id
                logger.debug("Using managed identity client_id: %s", mask(azure_client_id))
            credential = DefaultAzureCredential(**credential_kwargs)
            token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
            azure_client = AsyncAzureOpenAI(
                azure_endpoint=azure_openai_base_url,
                api_version=azure_openai_api_version,
                azure_ad_token_provider=token_provider,
                azure_deployment=azure_openai_deployment_name,
            )
            logger.info(
                "Azure OpenAI Async client initialized with managed identity (deployment: %s)",
                azure_openai_deployment_name,
            )
        else:
            # Use API Key
            if not azure_openai_api_key:
                logger.error("AZURE_OPENAI_API_KEY environment variable is required when not using managed identity.")
                raise RuntimeError(
                    "AZURE_OPENAI_API_KEY environment variable is required when not using managed identity."
                )
            azure_client = AsyncAzureOpenAI(
                azure_endpoint=azure_openai_base_url,
                api_version=azure_openai_api_version,
                api_key=azure_openai_api_key,
                azure_deployment=azure_openai_deployment_name,
            )
            logger.info(
                "Azure OpenAI Async client initialized with API key (deployment: %s)",
                azure_openai_deployment_name,
            )

        provider = OpenAIProvider(openai_client=azure_client)
        openai_model = OpenAIModel(model_name=model_name, provider=provider)
        logger.info(
            "OpenAIModel instance created: model_name=%s, deployment_name=%s, auth_method=%s",
            model_name,
            azure_openai_deployment_name,
            "Azure Identity" if use_managed_identity else "API key",
        )
        return openai_model
    except Exception as e:
        logger.error("Failed to initialize Azure OpenAIModel: %s", e, exc_info=True)
        raise  # re-raise for caller to handle
