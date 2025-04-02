# Azure OpenAI Component Specification

## Purpose

The Azure OpenAI component provides a PydanticAI wrapper for Azure OpenAI models for use with PydanticAI Agents. It handles model initialization and authentication.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIModel instance
- Support choice of api key or Azure Identity for authentication
- Use the `openai` library for Azure OpenAI client
- Implement basic error handling

## Implementation Considerations

- Load api keys and endpoints from environment variables, validating their presence
- If using Azure Identity:
  - AsyncAzureOpenAI client must be created with a token provider function
  - If using a custom client ID, use `ManagedIdentityCredential` with the specified client ID
- Create an `openai.AsyncAzureOpenAI` client with the provided token provider or API key
- Create a `pydantic_ai.providers.openai.OpenAIProvider` with the Azure OpenAI client
- Return a `pydantic_ai.models.openai.OpenAIModel` with the model name and provider

## Implementation Hints

```python
# Option 1: Create AsyncAzureOpenAI client with API key
azure_client = AsyncAzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Option 2: Create AsyncAzureOpenAI client with Azure Identity
azure_client = AsyncAzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Use the client to create the OpenAIProvider
openai_model = OpenAIModel(
    model_name,
    provider=OpenAIProvider(openai_client=azure_client),
)
```

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name and auth method (api key or Azure Identity)

## Component Dependencies

### Internal Components

None

### External Libraries

- **pydantic-ai** - (Required) Uses PydanticAI's OpenAIModel and OpenAIProvider for model management
- **openai** - (Required) Uses AsyncAzureOpenAI client for API communication
- **azure-identity** - (Required for managed identity) Uses DefaultAzureCredential, ManagedIdentityCredential, and get_bearer_token_provider for token provision

### Configuration Dependencies

- **AZURE_USE_MANAGED_IDENTITY** - (Optional) Boolean flag to use Azure Identity for authentication
- **AZURE_OPENAI_API_KEY** - (Required for API key auth) API key for Azure OpenAI authentication
- **AZURE_OPENAI_ENDPOINT** - (Required) Endpoint URL for Azure OpenAI service
- **AZURE_OPENAI_DEPLOYMENT_NAME** - (Required) Deployment name in Azure OpenAI
- **AZURE_OPENAI_API_VERSION** - (Required) API version to use with Azure OpenAI
- **AZURE_CLIENT_ID** - (Optional) Client ID for managed identity authentication

## Error Handling

- Log detailed error information for debugging

## Output Files

- `llm_utils/azure_openai.py`
