# Azure OpenAI Integration Guide for Recipe Executor

This document outlines how to configure and use Recipe Executor with Azure OpenAI services.

## Configuration

### Environment Variables

To use Azure OpenAI with Recipe Executor, you need to set the following environment variables in your `.env` file:

```
# Azure OpenAI Configuration
AZURE_OPENAI_BASE_URL=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_USE_MANAGED_IDENTITY=false
```

**Notes:**

- `AZURE_OPENAI_BASE_URL`: Your Azure OpenAI service endpoint URL
- `AZURE_OPENAI_API_VERSION`: The API version to use (default is `2025-03-01-preview`)
- `AZURE_OPENAI_API_KEY`: Your API key (not required if using managed identity)
- `AZURE_USE_MANAGED_IDENTITY`: Set to `true` to use Azure Managed Identity for authentication

### Authentication Methods

Recipe Executor supports two authentication methods for Azure OpenAI:

1. **API Key Authentication**: Default method using the API key provided in the environment variables
2. **Managed Identity Authentication**: Uses Azure Managed Identity for authentication without API keys

## Model Identifiers

When using Azure OpenAI, model identifiers follow this format:

```
azure:model_name:deployment_name
```

For example:

- `azure/gpt-4:deployment-gpt4`
- `azure/o3-mini:deployment-o3-mini`

These model identifiers are used in recipe files and when calling the LLM service directly.

## Deployment-Specific Considerations

### Azure OpenAI Resource Configuration

Ensure your Azure OpenAI resource has the appropriate model deployments:

1. Create deployments in Azure OpenAI Studio for each model you plan to use
2. Name your deployments consistently and use those names in your model identifiers
3. If using Managed Identity, ensure the identity has appropriate permissions on your Azure OpenAI resource

## Troubleshooting

Common issues and solutions:

1. **Authentication Errors**:

   - Ensure your Azure OpenAI API key is correct
   - Check that Managed Identity has proper permissions if used

2. **Deployment Not Found**:

   - Verify the deployment name in your model identifier matches exactly with your Azure OpenAI deployment

3. **Endpoint Connection Issues**:

   - Ensure network connectivity to Azure OpenAI endpoints
   - Verify the correct endpoint URL format
