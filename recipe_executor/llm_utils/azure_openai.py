import os
import logging
from typing import Optional

from azure.identity import DefaultAzureCredential
# Depending on your Azure Identity version, you can also import get_bearer_token_provider
# from azure.identity import get_bearer_token_provider

try:
    # The AsyncAzureOpenAI client is provided by the OpenAI Python library when using Azure OpenAI endpoints
    from openai import AsyncAzureOpenAI
except ImportError as e:
    raise ImportError("openai package must be installed to use the Azure OpenAI component")

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_openai_model(model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None) -> OpenAIModel:
    """
    Create and return a PydanticAI OpenAIModel instance configured for Azure OpenAI.

    This function reads configuration parameters from environment variables to initialize the Azure OpenAI client.
    Depending on the environment variables, authentication is configured either via an API key or via Azure Managed Identity.

    Environment Variables:
        AZURE_OPENAI_ENDPOINT: The endpoint URL for Azure OpenAI (required).
        AZURE_OPENAI_API_VERSION: The API version for Azure OpenAI (optional, defaults to '2024-07-01-preview').
        AZURE_OPENAI_DEPLOYMENT_NAME: The deployment name for Azure OpenAI (optional; if not set, defaults to the provided model_name or deployment_name parameter).
        AZURE_USE_MANAGED_IDENTITY: If set to 'true' (case-insensitive) or '1', use Azure Identity based authentication.
        AZURE_MANAGED_IDENTITY_CLIENT_ID: (Optional) Managed Identity client ID to use with DefaultAzureCredential.
        AZURE_OPENAI_API_KEY: Required if not using managed identity.

    Args:
        model_name (str): The name of the model (e.g. 'gpt-4o').
        deployment_name (Optional[str]): The Azure deployment name to use; if not provided, fallback to AZURE_OPENAI_DEPLOYMENT_NAME or model_name.
        logger (Optional[logging.Logger]): Logger to use; defaults to 'RecipeExecutor'.

    Returns:
        OpenAIModel: An instance of OpenAIModel configured for Azure OpenAI.

    Raises:
        ValueError: If required environment variables are missing.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise ValueError("Missing required environment variable: AZURE_OPENAI_ENDPOINT")

    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")

    # Determine deployment name
    env_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    final_deployment = deployment_name or env_deployment or model_name

    use_managed_id = os.environ.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ["true", "1"]
    
    if use_managed_id:
        # Use Azure Managed Identity credentials
        client_id = os.environ.get("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        if client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            credential = DefaultAzureCredential()
        
        # get_bearer_token_provider is sometimes used if needed. However, many Azure SDKs accept a credential object directly.
        # For our purpose, AsyncAzureOpenAI supports an azure_ad_token_provider parameter.
        # Here we assume that passing the credential directly wrapped via a lambda is acceptable.
        scope = "https://cognitiveservices.azure.com/.default"

        # Define a simple token provider function which gets a token from the credential
        async def azure_ad_token_provider():
            token = credential.get_token(scope)
            return token.token

        logger.info(f"Initializing Azure OpenAI client using Azure Identity (Managed Identity).")

        try:
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=azure_ad_token_provider,
                azure_endpoint=endpoint,
                api_version=api_version,
                azure_deployment=final_deployment,
            )
        except Exception as e:
            logger.error(f"Failed to initialize AsyncAzureOpenAI client with Managed Identity: {e}")
            raise
    else:
        # Use API key authentication
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing required environment variable: AZURE_OPENAI_API_KEY for API key authentication")
        logger.info(f"Initializing Azure OpenAI client using API key (first and last visible: {api_key[0]}***{api_key[-1]}).")
        try:
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=api_version,
                azure_deployment=final_deployment,
            )
        except Exception as e:
            logger.error(f"Failed to initialize AsyncAzureOpenAI client with API key: {e}")
            raise

    # Use the Azure client to create the OpenAIProvider
    provider = OpenAIProvider(openai_client=azure_client)

    # Create the OpenAIModel with the provided model_name
    model = OpenAIModel(model_name=model_name, provider=provider)
    logger.info(f"Created Azure OpenAI model instance: model_name={model_name}, deployment={final_deployment}, auth_mode={'Managed Identity' if use_managed_id else 'API Key'}.")
    
    return model


if __name__ == "__main__":
    # For testing purpose
    logging.basicConfig(level=logging.INFO)
    try:
        model = get_openai_model("gpt-4o")
        print("Azure OpenAI model created successfully.")
    except Exception as e:
        print(f"Error: {e}")