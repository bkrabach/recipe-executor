import logging
import os
from typing import Optional

# Import the Azure OpenAI client from the openai library
try:
    from openai import AsyncAzureOpenAI
except ImportError:
    raise ImportError("The openai package is required. Please install it via pip install openai")

# Import azure-identity components
try:
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
except ImportError:
    raise ImportError("The azure-identity package is required. Please install it via pip install azure-identity")

# Import the PydanticAI models and providers
try:
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
except ImportError:
    raise ImportError("The pydantic-ai package is required. Please install it via pip install pydantic-ai")


def get_azure_openai_model(
    model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance configured for Azure OpenAI.

    This function loads configuration from environment variables and creates an
    Azure OpenAI client using either an API key or managed identity authentication.

    Environment Variables:
        AZURE_OPENAI_ENDPOINT (str): The endpoint URL for Azure OpenAI.
        AZURE_OPENAI_API_VERSION (str): The API version to use (default: "2025-03-01-preview").
        AZURE_OPENAI_DEPLOYMENT_NAME (str): Default deployment name (optional, defaults to model_name).

        For API key authentication:
            AZURE_OPENAI_API_KEY (str): Your Azure OpenAI API key.

        For managed identity authentication:
            AZURE_USE_MANAGED_IDENTITY (str): Set to "true" to use managed identity.
            AZURE_MANAGED_IDENTITY_CLIENT_ID (str): (Optional) Client ID for a user-assigned managed identity.

    Args:
        model_name (str): The underlying model name.
        deployment_name (Optional[str]): The deployment name to use. If not provided, the environment
           variable AZURE_OPENAI_DEPLOYMENT_NAME is used. Defaults to model_name if not set.
        logger (Optional[logging.Logger]): Logger instance; if not provided, a default logger named "RecipeExecutor" is used.

    Returns:
        OpenAIModel: A configured instance of a PydanticAI OpenAIModel using Azure OpenAI.

    Raises:
        EnvironmentError: If required environment variables are missing.
        ImportError: If required packages are not installed.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Load essential environment variables
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise EnvironmentError("AZURE_OPENAI_ENDPOINT environment variable not set")

    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")

    # Determine the deployment name to use
    if deployment_name is None:
        deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", model_name)

    # Logging loaded configuration (masking the api key if present)
    logger.debug(f"Azure OpenAI Endpoint: {azure_endpoint}")
    logger.debug(f"Azure OpenAI API Version: {api_version}")
    logger.debug(f"Azure OpenAI Deployment Name: {deployment_name}")

    # Check if managed identity is to be used
    use_managed = os.environ.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
    if use_managed:
        # Use managed identity authentication
        client_id = os.environ.get("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        if client_id:
            credential = ManagedIdentityCredential(client_id=client_id)
            auth_method = "Managed Identity (Client ID)"
        else:
            credential = DefaultAzureCredential()
            auth_method = "Default Azure Credential"

        # Obtain a token provider for the Azure OpenAI scope
        # The scope for Azure Cognitive Services is "https://cognitiveservices.azure.com/.default"
        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

        # Initialize the AsyncAzureOpenAI client with token provider
        try:
            azure_client = AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                azure_deployment=deployment_name,
                azure_ad_token_provider=token_provider,
            )
        except Exception as e:
            logger.error(f"Error initializing AsyncAzureOpenAI client with managed identity: {e}")
            raise
    else:
        # Use API key authentication
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("AZURE_OPENAI_API_KEY must be set when not using managed identity")
        auth_method = "API Key"
        # Mask API key for logging (show only first and last character)
        if len(api_key) > 2:
            masked_api_key = api_key[0] + "*" * (len(api_key) - 2) + api_key[-1]
        else:
            masked_api_key = api_key
        logger.debug(f"Using API Key: {masked_api_key}")

        try:
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                azure_deployment=deployment_name,
            )
        except Exception as e:
            logger.error(f"Error initializing AsyncAzureOpenAI client with API key: {e}")
            raise

    logger.info(f"Creating Azure OpenAI model '{model_name}' using auth method: {auth_method}")

    # Create the OpenAIProvider wrapping the azure_client
    provider = OpenAIProvider(openai_client=azure_client)

    # Create an instance of the PydanticAI OpenAIModel
    model = OpenAIModel(model_name, provider=provider)
    return model
