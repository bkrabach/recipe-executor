=== File: recipes/recipe_executor/components/context/context_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "context",
        "component_path": "/",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/context/context_docs.md ===
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
```

## Initialization

The Context can be initialized with optional artifacts and configuration:

```python
# Method signature
def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the Context with optional artifacts and configuration.

    Args:
        artifacts: Initial artifacts to store
        config: Configuration values
    """
```

Examples:

```python
# Empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"spec": "specification content"})

# With configuration
context = Context(config={"output_dir": "./output"})

# With both
context = Context(
    artifacts={"spec": "specification content"},
    config={"output_dir": "./output"}
)
```

## Core API

### Storing Values

```python
def __setitem__(self, key: str, value: Any) -> None:
    """Dictionary-like setting of artifacts."""
```

### Retrieving Values

```python
def __getitem__(self, key: str) -> Any:
    """Dictionary-like access to artifacts."""

def get(self, key: str, default: Optional[Any] = None) -> Any:
    """Get an artifact with an optional default value."""

# Usage examples
value = context["key"]  # Raises KeyError if not found
value = context.get("key", default=None)  # Returns default if not found
```

### Checking Keys

```python
def __contains__(self, key: str) -> bool:
    """Check if a key exists in artifacts."""

# Usage example
if "key" in context:
    # Key exists
    pass
```

### Iteration

```python
def __iter__(self) -> Iterator[str]:
    """Iterate over artifact keys."""

def keys(self) -> Iterator[str]:
    """Return an iterator over the keys of artifacts."""

def __len__(self) -> int:
    """Return the number of artifacts."""

# Usage examples
for key in context:
    value = context[key]
    print(f"{key}: {value}")

# Get number of artifacts
num_artifacts = len(context)
```

### Getting All Values

```python
def as_dict(self) -> Dict[str, Any]:
    """Return a copy of the artifacts as a dictionary to ensure immutability."""

# Usage example
all_artifacts = context.as_dict()
```

### Accessing Configuration

```python
# Configuration is accessed via the config attribute
# Type: Dict[str, Any]

# Usage example
output_dir = context.config.get("output_dir", "./default")
```

### Cloning Context

```python
def clone(self) -> Context:
    """Return a deep copy of the current context."""

# Usage example
cloned_context = context.clone()
```

## Integration with Steps

Steps receive the context in their `execute` method:

```python
def execute(self, context: Context) -> None:
    # Read from context
    input_value = context.get("input", "default")

    # Process...
    result = process(input_value)

    # Store in context
    context["output"] = result
```

## Important Notes

- Context is mutable and shared between steps
- Values can be of any type
- Configuration is read-only in typical usage (but not enforced)
- Step authors should document keys they read/write
- Context provides no thread safety - it's designed for sequential execution
- Use `clone` to create a snapshot of the context if needed - for parallel execution


=== File: recipes/recipe_executor/components/context/context_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/context.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/context/context_spec.md ===
# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution.

## Core Requirements

- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Provide a clone() method that returns a deep copy of the context's current artifacts and configuration
- Ensure data isolation between different executions
- Follow minimalist design principles

## Implementation Considerations

- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Implement a clone() method that returns a deep copy of the context's current state
- Provide clear error messages for missing keys
- Convert keys from dict_keys() to a list for iteration
- Return copies of internal data to prevent external modification
- Maintain minimal state with clear separation of concerns

## Logging

- Debug: None
- Info: None

## Dependency Integration Considerations

None

### Internal Components

None

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Raise KeyError with descriptive message when accessing non-existent keys
- No special handling for setting values (all types allowed)

## Output Files

- `context.py`

## Future Considerations

- Namespacing of artifacts
- Support for merging multiple contexts


=== File: recipes/recipe_executor/components/executor/executor_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/registry/registry_docs.md",
      "artifact": "registry_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "executor",
        "component_path": "/",
        "existing_code": "{{existing_code}}",
        "additional_content": "<REGISTRY_DOCS>\n{{registry_docs}}\n</REGISTRY_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/executor/executor_docs.md ===
# Executor Component Usage

## Importing

```python
from recipe_executor.executor import Executor
```

## Basic Usage

The Executor has a single primary method: `execute()`. This method loads and runs a recipe with a given context:

```python
# Method signature
def execute(
    self,
    recipe: str | Dict[str, Any],
    context: Context,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Execute a recipe with the given context.

    Args:
        recipe: Recipe to execute, can be a file path, JSON string, or dictionary
        context: Context instance to use for execution
        logger: Optional logger to use, creates a default one if not provided

    Raises:
        ValueError: If recipe format is invalid or step execution fails
        TypeError: If recipe type is not supported
    """
```

Examples:

```python
# Create context and executor
context = Context()
executor = Executor()

# Execute a recipe from a file
executor.execute("path/to/recipe.json", context)

# Or from a JSON string
json_string = '{"steps": [{"type": "read_file", "path": "example.txt", "artifact": "content"}]}'
executor.execute(json_string, context)

# Or from a dictionary
recipe_dict: Dict[str, List[Dict[str, Any]]] = {
    "steps": [
        {"type": "read_file", "path": "example.txt", "artifact": "content"}
    ]
}
executor.execute(recipe_dict, context)
```

## Recipe Structure

The recipe structure must contain a "steps" key, which is a list of step definitions. Each step must have a "type" field that matches a registered step type. The step type determines how the step is executed.

### Example Recipe

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "input.txt",
      "artifact": "input_content"
    },
    {
      "type": "generate",
      "prompt": "Generate based on: {{input_content}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generation_result"
    }
  ]
}
```

```python
# Example of a recipe as a dictionary
recipe_dict = {
    "steps": [
        {
            "type": "read_file",
            "path": "input.txt",
            "artifact": "input_content"
        },
        {
            "type": "generate",
            "prompt": "Generate based on: {{input_content}}",
            "model": "{{model|default:'openai:o3-mini'}}",
            "artifact": "generation_result"
        }
    ]
}
```

## Custom Logging

You can provide a custom logger to the executor:

```python
import logging

logger = logging.getLogger("my_custom_logger")
logger.setLevel(logging.DEBUG)

executor.execute(recipe, context, logger=logger)
```

## Integration with Steps

The executor uses the Step Registry to instantiate steps based on their type:

```python
# Each step in a recipe must have a "type" field:
step: Dict[str, Any] = {
    "type": "read_file",  # Must match a key in STEP_REGISTRY
    "path": "input.txt",
    "artifact": "content"
}
```

## Important Notes

1. Recipes must contain valid steps with "type" fields
2. All step types must be registered in the STEP_REGISTRY before use
3. Each step receives the same context object
4. Execution is sequential by default


=== File: recipes/recipe_executor/components/executor/executor_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/executor.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/executor/executor_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/executor/executor_spec.md ===
# Executor Component Specification

## Purpose

The Executor component is the central orchestration mechanism for the Recipe Executor system. It loads recipe definitions from various sources and executes their steps sequentially using the provided context.

## Core Requirements

- Load and parse recipes from multiple input formats
- Validate recipe structure and step definitions
- Execute steps sequentially using registered step implementations
- Provide clear error messages for troubleshooting
- Support minimal logging for execution status

## Implementation Considerations

- Parse recipes from file paths, JSON strings, or dictionaries
- Use direct instantiation of step classes from the registry
- Handle errors at both recipe and step levels
- Maintain a simple, stateless design

## Component Dependencies

### Internal Components

- **Context** - (Required) Uses Context for data sharing between steps during recipe execution
- **Step Registry** - (Required) Uses STEP_REGISTRY to look up and instantiate step classes by type

### External Libraries

None

### Configuration Dependencies

None

## Logging

- Debug: Log recipe start, file name, parsed payload, step execution details, and completion
- Info: None

## Error Handling

- Validate recipe format before execution begins
- Check that step types exist in the registry before instantiation
- Verify each step is properly structured before execution
- Provide specific error messages identifying problematic steps
- Include original exceptions for debugging

## Output Files

- `executor.py`

## Future Considerations

- Parallel step execution
- Conditional branching between steps
- Step retry policies
- Progress tracking and reporting


=== File: recipes/recipe_executor/components/llm/llm_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/models/models_docs.md",
      "artifact": "models_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm_utils/azure_openai/azure_openai_docs.md",
      "artifact": "azure_openai_docs"
    },
    {
      "type": "read_file",
      "path": "ai_context/PYDANTIC_AI_DOCS.md",
      "artifact": "pydantic_ai_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "llm",
        "component_path": "/",
        "existing_code": "{{existing_code}}",
        "additional_content": "<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<AZURE_OPENAI_DOCUMENTATION>\n{{azure_openai_docs}}\n</AZURE_OPENAI_DOCUMENTATION>\n<PYDANTIC_AI_DOCUMENTATION>\n{{pydantic_ai_docs}}\n</PYDANTIC_AI_DOCUMENTATION>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm/llm_docs.md ===
# LLM Component Usage

## Importing

```python
from recipe_executor.llm import call_llm
```

## Basic Usage

The LLM component provides one main function:

```python
def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = "RecipeExecutor") -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or 'provider:model_name:deployment_name').
        If None, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"

    Returns:
        FileGenerationResult: The structured result data containing generated files and commentary.

    Raises:
        Exception: If model value cannot be mapped to valid provider/model_name , LLM call fails, or result validation fails.
    """
```

Usage example:

```python
# Call LLM with default model
result = call_llm("Generate a Python utility module for handling dates.")

# Call with specific model
result = call_llm(
    prompt="Create a React component for a user profile page.",
    model="openai:o3-mini"
)
```

```python
def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model using structured output.

    Args:
        model_id (Optional[str]): Model identifier in format 'provider:model_name'.
        If None, defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured Agent ready to process LLM requests and return structured results with files and commentary.
    """
```

Usage example:

```python
# Get default agent (openai:gpt-4o)
default_agent = get_agent()

# Get agent with specific model
custom_agent = get_agent(model_id="anthropic:claude-3.7-sonnet-latest")
results = custom_agent.run_async("Generate a Python utility module for handling dates.")
# Access FileGenerationResult
file_generation_result = results.data

```

## Model ID Format

The component uses a standardized model identifier format:

```
All models:
provider:model_name

Additional option for Azure OpenAI (otherwise assume deployment_name is the same as model_name):
azure:model_name:deployment_name
```

### Supported providers:

- **openai**: OpenAI models (e.g., `gpt-4o`, `o3-mini`)
- **anthropic**: Anthropic models (e.g., `claude-3.7-sonnet-latest`)
- **gemini**: Gemini models (e.g., `gemini-pro`)
- **azure**: Azure OpenAI models (e.g., `azure:gpt-4o`, `azure:o3-mini`)
- **azure**: Azure OpenAI models with custom deployment name (e.g., `azure:gpt-4o:my_deployment_name`)

## Error Handling

Example of error handling:

```python
try:
    result = call_llm(prompt, model_id)
    # Process result
except ValueError as e:
    # Handle invalid model ID or format
    print(f"Invalid model configuration: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"LLM call failed: {e}")
```

## Integration with Steps

The LLM component is primarily used by the GenerateWithLLMStep:

```python
# Example from GenerateWithLLMStep.execute()
def execute(self, context: Context) -> None:
    rendered_prompt = render_template(self.config.prompt, context)
    rendered_model = render_template(self.config.model, context)

    response = call_llm(rendered_prompt, rendered_model)

    artifact_key = render_template(self.config.artifact, context)
    context[artifact_key] = response
```

## Important Notes

- Calling a model incurs API costs with the respective provider
- OpenAI is the default provider if none is specified
- The component logs request details at debug level
- Responses are validated against the FileGenerationResult model


=== File: recipes/recipe_executor/components/llm/llm_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/llm.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm/llm_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm/llm_spec.md ===
# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini (not Vertex))
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI for consistent handling and validation of LLM responses
- Implement basic error handling
- Support structured output format for file generation

## Implementation Considerations

- Use a clear provider:model_name identifier format
- Do not need to pass api keys directly to model classes (do need to provide to AzureProvider)
- Use PydanticAI's provider-specific model classes, passing only the model name
  - pydantic_ai.models.openai.OpenAIModel (used for Azure OpenAI)
  - pydantic_ai.models.anthropic.AnthropicModel
  - pydantic_ai.models.gemini.GeminiModel
- Create a PydanticAI Agent with the model and a structured output type
- Use the `run_sync` method of the Agent to make requests
- CRITICAL: make sure to return the result.data in the call_llm method

## Logging

- Debug: Log full request payload before making call and then full response payload after receiving it
- Info: Log model name and provider before making call (do not include the request payload details) and response times upon completion (do not include the response payload details)

## Component Dependencies

### Internal Components

- **Models** - (Required) Uses FileGenerationResult and FileSpec for structured output validation
- **Azure OpenAI** - (Required for Azure provider) Uses get_azure_openai_model for Azure OpenAI model initialization

### External Libraries

- **pydantic-ai** - (Required) Relies on PydanticAI for model initialization, Agent-based request handling, and structured-output response processing

### Configuration Dependencies

- **DEFAULT_MODEL** - (Optional) Environment variable specifying the default LLM model in format "provider:model_name"
- **OPENAI_API_KEY** - (Required for OpenAI) API key for OpenAI access
- **ANTHROPIC_API_KEY** - (Required for Anthropic) API key for Anthropic access
- **GEMINI_API_KEY** - (Required for Gemini) API key for Google Gemini AI access

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Output Files

- `llm.py`

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning

## Dependency Integration Considerstions

### PydanticAI

Create a PydanticAI model for the LLM provider and model name. This will be used to initialize the model and make requests.

```python
def get_model(model_id: str) -> OpenAIModel | AnthropicModel | GeminiModel:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider:model_name' or 'provider:model_name:deployment_name'.

    Supported providers:
    - openai
    - anthropic
    - gemini
    - azure (for Azure OpenAI, use 'azure:model_name:deployment_name' or 'azure:model_name')

    Args:
        model_id (str): Model identifier in format 'provider:model_name'
            or 'provider:model_name:deployment_name'.
            If None, defaults to 'openai:gpt-4o'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai:o3-mini")
# Uses OpenAIModel('o3-mini')

# Get an Anthropic model
anthropic_model = get_model("anthropic:claude-3.7-sonnet-latest")
# Uses AnthropicModel('claude-3.7-sonnet-latest')

# Get a Gemini model
gemini_model = get_model("gemini:gemini-pro")
# Uses GeminiModel('gemini-pro')
```


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "ai_context/AZURE_IDENTITY_CLIENT_DOCS.md",
      "artifact": "azure_identity_client_docs"
    },
    {
      "type": "read_file",
      "path": "ai_context/PYDANTIC_AI_DOCS.md",
      "artifact": "pydantic_ai_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "azure_openai",
        "component_path": "/llm_utils",
        "existing_code": "{{existing_code}}",
        "additional_content": "<AZURE_IDENTITY_CLIENT_DOCS>\n{{azure_identity_client_docs}}\n</AZURE_IDENTITY_CLIENT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<PYDANTIC_AI_DOCUMENTATION>\n{{pydantic_ai_docs}}\n</PYDANTIC_AI_DOCUMENTATION>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_docs.md ===
# Azure OpenAI Component Usage

## Importing

```python
import recipe_executor.llm_utils.azure_openai
```

## Basic Usage

```python
def get_openai_model(model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = "RecipeExecutor") -> pydantic_ia.models.openai.OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from environment variables for Azure OpenAI.

    Args:
        model_name (str): Model name, such as "gpt-4o" or "o3-mini".
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance for Azure OpenAI.

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python
# Get an OpenAI model using Azure OpenAI
openai_model = azure_openai.get_openai_model("o3-mini")

# Get an OpenAI model using Azure OpenAI with a specific deployment name
openai_model = azure_openai.get_openai_model("o3-mini", "my_deployment_name")
```

## Environment Variables

The component uses environment variables for authentication and configuration. Depending upon the authentication method, set the following environment variables:

### Option 1: Managed Identity with Default Managed Identity

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 2: Managed Identity with Custom Client ID

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_MANAGED_IDENTITY_CLIENT_ID= # Required
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 3: API Key Authentication

```bash
AZURE_OPENAI_API_KEY= # Required
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/llm_utils/azure_openai.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm_utils/azure_openai/azure_openai_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_spec.md ===
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


=== File: recipes/recipe_executor/components/logger/logger_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "logger",
        "component_path": "/",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/logger/logger_docs.md ===
# Logger Component Usage

## Importing

```python
from recipe_executor.logger import init_logger
```

## Initialization

The Logger component provides a single function to initialize a configured logger:

```python
def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
```

Examples:

```python
# Default usage
logger = init_logger()

# With custom log directory
logger = init_logger(log_dir="custom/log/path")
```

## Log Levels

The configured logger supports standard Python logging levels:

```python
# Debug level (to debug.log file and higher level logs)
logger.debug("Detailed information for diagnosing problems")

# Info level (to console, info.log, and error.log)
logger.info("Confirmation that things are working as expected")

# Warning level (to console, info.log, and error.log)
logger.warning("An indication that something unexpected happened")

# Error level (to console, info.log, and error.log)
logger.error("Due to a more serious problem, the software could not perform a function")

# Critical level (to all logs)
logger.critical("A serious error indicating the program itself may be unable to continue running")
```

## Log Files

The logger creates three log files:

1. `debug.log` - All messages (DEBUG and above)
2. `info.log` - INFO messages and above
3. `error.log` - ERROR messages and above

Example:

```
2025-03-30 15:42:38,927 [INFO] Starting Recipe Executor Tool
2025-03-30 15:42:38,928 [DEBUG] Initializing executor
2025-03-30 15:42:38,930 [INFO] Executing recipe: recipes/my_recipe.json
2025-03-30 15:42:38,935 [ERROR] Recipe execution failed: Invalid step type
```

## Console Output

The logger also writes INFO level and above messages to stdout:

```python
# This appears in both console and log files
logger.info("Executing step 1 of 5")

# This appears in log files only
logger.debug("Step config: {'path': 'input.txt', 'artifact': 'content'}")
```

## Integration with Other Components

The logger is typically initialized in the main component and passed to the executor:

```python
from recipe_executor.logger import init_logger
from recipe_executor.executor import Executor

logger = init_logger(log_dir="logs")
executor = Executor()
executor.execute(recipe_path, context, logger=logger)
```

Steps receive the logger in their constructor:

```python
class ReadFileStep(BaseStep):
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("RecipeExecutor")
        # ...
```

## Important Notes

1. Logs are cleared (truncated) on each run
2. Debug logs can get large with detailed information
3. The log directory is created if it doesn't exist
4. The logger name "RecipeExecutor" is consistent across the system


=== File: recipes/recipe_executor/components/logger/logger_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/logger.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/logger/logger_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/logger/logger_spec.md ===
# Logger Component Specification

## Purpose

The Logger component provides a consistent logging interface for the Recipe Executor system. It initializes and configures logging, writes logs to appropriate files, and ensures that all components can log messages at different severity levels.

## Core Requirements

- Initialize a logger that writes to both stdout and log files
- Support different log levels (DEBUG, INFO, ERROR)
- Create separate log files for each level
- For stdout, set the log level to INFO
- Clear existing logs on each run to prevent unbounded growth
- Provide a consistent log format with timestamps and log levels
- Create log directories if they don't exist

## Implementation Considerations

- Use Python's standard logging module directly
- Reset existing handlers to ensure consistent configuration
- Set up separate handlers for console and different log files
- Create the log directory if it doesn't exist
- Use mode="w" for file handlers to clear previous logs

## Logging

- Debug: Log that the logger is being initialized, the log directory being created, and any errors encountered during initialization
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

- **Python stdlib logging** - (Required) Uses Python's standard logging module for core functionality

### Configuration Dependencies

None

## Error Handling

- Catch and report directory creation failures
- Handle file access permission issues
- Provide clear error messages for logging setup failures

## Future Considerations

- Customizable log formats

## Output Files

- `logger.py`


=== File: recipes/recipe_executor/components/main/main_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/executor/executor_docs.md",
      "artifact": "executor_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/logger/logger_docs.md",
      "artifact": "logger_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "main",
        "component_path": "/",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<EXECUTOR_DOCS>\n{{executor_docs}}\n</EXECUTOR_DOCS>\n<LOGGER_DOCS>\n{{logger_docs}}\n</LOGGER_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/main/main_docs.md ===
# Main Component Usage

## Command-Line Interface

The Recipe Executor is used from the command line like this:

```bash
# Basic usage
python -m recipe_executor.main recipes/my_recipe.json

# With custom log directory
python -m recipe_executor.main recipes/my_recipe.json --log-dir custom_logs

# With context values
python -m recipe_executor.main recipes/my_recipe.json --context key1=value1 --context key2=value2
```

## Command-Line Arguments

The Main component supports these arguments:

1. `recipe_path` (required positional): Path to the recipe file to execute
2. `--log-dir` (optional): Directory for log files (default: "logs")
3. `--context` (optional, multiple): Context values as key=value pairs

## Context Parsing

The Main component parses context values from the command line. For example:

```bash
# These arguments:
--context name=John --context age=30 --context active=true

# Will create this context:
{
    "name": "John",
    "age": "30",
    "active": "true"
}
```

## Exit Codes

The Main component uses these exit codes:

- `0`: Successful execution
- `1`: Error during execution (parsing errors, missing files, execution failures)

## Error Messages

Error messages are written to stderr and the log files:

```python
# Context parsing error
sys.stderr.write(f"Context Error: {str(e)}\n")

# Recipe execution error
logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
```

## Important Notes

1. The recipe path must point to a valid recipe file
2. Context values from the command line are stored as strings
3. Logs are written to the specified log directory
4. All steps in the recipe share the same context
5. The executable exits with non-zero status on error


=== File: recipes/recipe_executor/components/main/main_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/main.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/main/main_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/main/main_spec.md ===
# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, executes the specified recipe, and handles top-level error reporting.

## Core Requirements

- Provide a command-line interface for executing recipes
- Load environment variables from .env files using python-dotenv
  - python-dotenv is already installed as a dependency of the project
- Parse arguments for recipe path and context values
- Initialize the logging system
- Create the context with command-line supplied values as artifacts
- Execute the specified recipe with proper error handling
- Follow minimal design with clear user-facing error messages

## Implementation Considerations

- Call load_dotenv() early in the main function before any other initialization to make environment variables available in other components as soon as possible
- Use argparse for command-line argument parsing
- Initialize logging early in execution flow
- Parse context values from key=value pairs
- Create a clean context for recipe execution
- Keep the main function focused on orchestration
- Provide meaningful exit codes and error messages

## Implementation Details

- Import Executor using `from executor import Executor` to avoid circular import issues, despite continuing to use the full `recipe_executor.context`, etc. for other imports to maintain consistency with the rest of the codebase

## Logging

- Debug: Log the start of the main function, including parsed arguments and context values
- Info: Log the initialization of the Recipe Executor Tool and the start of recipe execution, upon completion report the success or failure of the execution along with total time taken

## Component Dependencies

### Internal Components

- **Context** - (Required) Creates the Context object with CLI-supplied values
- **Executor** - (Required) Uses Executor to run the specified recipe
- **Logger** - (Required) Uses init_logger to set up the logging system

### External Libraries

- **python-dotenv** - (Required) Uses load_dotenv to load environment variables from .env files
- **argparse** - (Required) Uses argparse for command-line argument parsing

### Configuration Dependencies

- **.env file** - (Optional) For environment variable configuration

## Error Handling

- Validate command-line arguments
- Provide clear error messages for missing or invalid recipe files
- Handle context parsing errors gracefully
- Log all errors before exiting
- Use appropriate exit codes for different error conditions
- Raise SystemExit with appropriate exit codes for different error conditions
- Employ a global try-except block to catch unhandled exceptions and log them
- Neatly format error messages for user-friendliness, considering use of `traceback.format_exc()` and other techniques for making the error reporting easy to identify main error and still provide useful context
- Use a finally block to ensure proper cleanup and logging of execution time

## Output Files

- `main.py`

## Future Considerations

- Support for environment variable configuration
- Support for directory-based recipes


=== File: recipes/recipe_executor/components/models/models_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "models",
        "component_path": "/",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/models/models_docs.md ===
# Models Component Usage

## Importing

```python
from recipe_executor.models import (
    FileSpec,
    FileGenerationResult,
    RecipeStep,
    Recipe
)
```

## File Generation Models

### FileSpec

Represents a single file to be generated:

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """

    path: str
    content: str
```

Usage example:

```python
file = FileSpec(
    path="src/utils.py",
    content="def hello_world():\n    print('Hello, world!')"
)

# Access properties
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
```

### FileGenerationResult

Contains a collection of generated files and optional commentary:

```python
class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """

    files: List[FileSpec]
    commentary: Optional[str] = None
```

Usage example:

```python
result = FileGenerationResult(
    files=[
        FileSpec(path="src/utils.py", content="def util_function():\n    pass"),
        FileSpec(path="src/main.py", content="from utils import util_function")
    ],
    commentary="Generated utility module and main script"
)

# Iterate through files
for file in result.files:
    print(f"Writing to {file.path}")
    # ... write file.content to file.path
```

## Recipe Models

### RecipeStep

Represents a single step in a recipe:

```python
class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """

    type: str
    config: Dict
```

### Recipe

Represents a complete recipe with multiple steps:

```python
class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]
```

Usage example:

```python
from recipe_executor.models import Recipe, RecipeStep

# Create a recipe with steps
recipe = Recipe(
    steps=[
        RecipeStep(
            type="read_file",
            config={"file_path": "specs/component_spec.md", "store_key": "spec"}
        ),
        RecipeStep(
            type="generate",
            config={
                "prompt": "Generate code for: {{spec}}",
                "model": "{{model|default:'openai:o3-mini'}}",
                "artifact": "code_result"
            }
        ),
        RecipeStep(
            type="write_files",
            config={"artifact": "code_result", "root": "./output"}
        )
    ]
)

# Validate recipe structure
recipe_dict = recipe.dict()
```

## Model Validation

All models inherit from Pydantic's BaseModel, providing automatic validation:

```python
# This will raise a validation error because path is required
try:
    FileSpec(content="File content")
except Exception as e:
    print(f"Validation error: {e}")

# This works correctly
valid_file = FileSpec(path="file.txt", content="File content")
```

## Important Notes

1. Models provide runtime validation in addition to static type checking
2. Default values are provided for common configuration options
3. Models can be converted to dictionaries with `.dict()` method
4. Models can be created from dictionaries with `Model(**dict_data)`


=== File: recipes/recipe_executor/components/models/models_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/models.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/models/models_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/models/models_spec.md ===
# Models Component Specification

## Purpose

The Models component defines the core data structures used throughout the Recipe Executor system. It provides Pydantic models for validating and structuring data, including recipe steps, and file generation results.

## Core Requirements

- Define consistent data structures for file generation results
- Provide configuration models for various step types
- Support recipe structure validation
- Leverage Pydantic for schema validation and documentation
- Include clear type hints and docstrings

## Implementation Considerations

- Use Pydantic models for all data structures
- Keep models focused and minimal
- Provide sensible defaults where appropriate
- Use descriptive field names and docstrings
- Focus on essential fields without over-engineering

## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

- **pydantic** - (Required) Uses Pydantic for schema validation and model definition

### Configuration Dependencies

None

## Output Files

- `models.py`

## Future Considerations

- Extended validation for complex fields


=== File: recipes/recipe_executor/components/steps/base/base_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/models/models_docs.md",
      "artifact": "models_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "base",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/base/base_docs.md ===
# Steps Base Component Usage

## Importing

```python
from recipe_executor.steps.base import BaseStep, StepConfig
```

## Basic Structure

The Steps Base component provides two primary classes:

1. `StepConfig` - Base class for step configuration
2. `BaseStep` - Abstract base class for step implementations

These classes are designed to work together using generics for type safety.

## Step Configuration

All step configurations extend the `StepConfig` base class:

```python
class StepConfig(BaseModel):
    """Base class for all step configs. Extend this in each step."""
    pass

# Type variable for generic configuration types
ConfigType = TypeVar("ConfigType", bound=StepConfig)
```

Example of extending StepConfig:

```python
class ReadFileConfig(StepConfig):
    """Configuration for ReadFileStep"""
    path: str
    artifact: str
    encoding: str = "utf-8"  # With default value
```

## Base Step Class

The BaseStep is an abstract generic class parameterized by the config type:

```python
class BaseStep(Generic[ConfigType]):
    """
    Base class for all steps. Subclasses must implement `execute(context)`.
    Each step receives a config object and a logger.

    Args:
        config (ConfigType): Configuration for the step
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")

    def execute(self, context: Context) -> None:
        """
        Execute the step with the given context.

        Args:
            context (Context): Context for execution

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Each step must implement the `execute()` method.")
```

## Implementing a Step

To implement a concrete step, create a class that:

1. Extends BaseStep with a specific config type
2. Implements the execute method
3. Takes a dictionary of configuration values in the constructor

Example:

```python
class ExampleStep(BaseStep[ExampleConfig]):
    """Example step implementation."""

    def __init__(self, config: dict, logger=None):
        # Convert dict to the appropriate config type
        super().__init__(ExampleConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Implementation specific to this step
        self.logger.info("Executing example step")

        # Access configuration values
        value = self.config.some_field

        # Do something with the context
        context["result"] = f"Processed {value}"
```

## Step Registration

All step implementations should be registered in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY

# Register the step type
STEP_REGISTRY["example_step"] = ExampleStep
```

## Handling Configuration

The base step handles configuration conversion automatically:

```python
# Step configuration in a recipe
step_config = {
    "type": "example_step",
    "some_field": "value",
    "another_field": 42
}

# In the executor
step_class = STEP_REGISTRY[step_config["type"]]
step_instance = step_class(step_config, logger)

# Configuration is validated through Pydantic
# Access in the step through self.config
```

## Logging

All steps receive a logger in their constructor:

```python
def __init__(self, config: dict, logger=None):
    # If logger is None, it defaults to logging.getLogger("RecipeExecutor")
    super().__init__(ExampleConfig(**config), logger)

def execute(self, context: Context) -> None:
    # Use the logger for various levels
    self.logger.debug("Detailed debug information")
    self.logger.info("Step execution started")
    self.logger.warning("Potential issue detected")
    self.logger.error("Error occurred during execution")
```

## Important Notes

1. All step implementations must inherit from BaseStep
2. The execute method must be implemented by all subclasses
3. Steps should validate their configuration using Pydantic models
4. Steps receive and modify a shared Context object
5. Steps should use the logger for appropriate messages


=== File: recipes/recipe_executor/components/steps/base/base_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/base.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/base/base_spec.md ===
# Steps Base Component Specification

## Purpose

The Steps Base component defines the foundational abstract classes and interfaces for all step implementations in the Recipe Executor system. It provides a common structure for steps, ensuring consistent behavior and integration with the rest of the system.

## Core Requirements

- Define an abstract base class for all step implementations
- Provide a base configuration class for step configuration validation
- Establish a consistent interface for step execution
- Support proper type hinting using generics
- Include logging capabilities in all steps

## Implementation Considerations

- Use Python's abstract base classes for proper interface definition
- Leverage generic typing for configuration type safety
- Keep the base step functionality minimal but complete
- Use Pydantic for configuration validation
- Provide sensible defaults where appropriate

## Logging

- Debug: Step component initialized, including configuration details
- Info: None

## Component Dependencies

### Internal Components

- **Context** - (Required) Steps operate on a context object for data sharing
- **Models** - (Required) Uses Pydantic-based models for configuration validation

### External Libraries

- **pydantic** - (Required) Uses Pydantic for configuration class definition and validation
- **typing** - (Required) Uses Python typing for type hints and generics

### Configuration Dependencies

None

## Error Handling

- Define clear error handling responsibilities for steps
- Propagate errors with appropriate context
- Use logger for tracking execution progress and errors

## Output Files

- `steps/base.py`

## Future Considerations

- Lifecycle hooks for pre/post execution
- Asynchronous execution support
- Step validation and dependency checking
- Composition of steps into more complex steps


=== File: recipes/recipe_executor/components/steps/create.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/registry/registry_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/execute_recipe/execute_recipe_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/generate_llm/generate_llm_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/parallel/parallel_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/read_file/read_file_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/write_files/write_files_create.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/edit.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/registry/registry_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/execute_recipe/execute_recipe_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/generate_llm/generate_llm_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/parallel/parallel_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/read_file/read_file_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/write_files/write_files_edit.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/executor/executor_docs.md",
      "artifact": "executor_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "execute_recipe",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<EXECUTOR_DOCS>\n{{executor_docs}}\n</EXECUTOR_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_docs.md ===
# ExecuteRecipeStep Component Usage

## Importing

```python
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep, ExecuteRecipeConfig
```

## Configuration

The ExecuteRecipeStep is configured with an ExecuteRecipeConfig:

```python
class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, str] = {}
```

## Step Registration

The ExecuteRecipeStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep

STEP_REGISTRY["execute_recipe"] = ExecuteRecipeStep
```

## Basic Usage in Recipes

The ExecuteRecipeStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/sub_recipe.json"
    }
  ]
}
```

## Context Overrides

You can override specific context values for the sub-recipe execution:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/generate_component.json",
      "context_overrides": {
        "component_name": "Utils",
        "output_dir": "output/components/utils"
      }
    }
  ]
}
```

## Template-Based Values

Both the recipe path and context overrides can include template variables:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/{{recipe_type}}/{{component_id}}.json",
      "context_overrides": {
        "component_name": "{{component_display_name}}",
        "output_dir": "output/components/{{component_id}}"
      }
    }
  ]
}
```

## Recipe Composition

Sub-recipes can be composed to create more complex workflows:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/project_spec.md",
      "artifact": "project_spec"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/parse_project.json",
      "context_overrides": {
        "spec": "{{project_spec}}"
      }
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/generate_components.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/assemble_project.json"
    }
  ]
}
```

## Implementation Details

The ExecuteRecipeStep works by:

1. Rendering the recipe path with the current context
2. Applying context overrides (also rendered with the current context)
3. Creating a Executor instance
4. Executing the sub-recipe with the modified context

```python
def execute(self, context: Context) -> None:
    # Merge any context overrides into the current context
    if hasattr(self.config, "context_overrides") and self.config.context_overrides:
        for key, value in self.config.context_overrides.items():
            context[key] = render_template(value, context)

    # Render the recipe path
    recipe_path = render_template(self.config.recipe_path, context)

    # Verify recipe exists
    if not os.path.exists(recipe_path):
        raise FileNotFoundError(f"Sub-recipe file not found: {recipe_path}")

    # Log sub-recipe execution
    self.logger.info(f"Executing sub-recipe: {recipe_path}")

    # Execute the sub-recipe
    executor = Executor()
    executor.execute(recipe=recipe_path, context=context, logger=self.logger)

    # Log completion
    self.logger.info(f"Completed sub-recipe: {recipe_path}")
```

## Error Handling

The ExecuteRecipeStep can raise several types of errors:

```python
try:
    execute_recipe_step.execute(context)
except FileNotFoundError as e:
    # Sub-recipe file not found
    print(f"File error: {e}")
except ValueError as e:
    # Recipe format or execution errors
    print(f"Recipe error: {e}")
```

## Common Use Cases

1. **Component Generation**:

   ```json
   {
     "type": "execute_recipe",
     "recipe_path": "recipes/generate_component.json",
     "context_overrides": {
       "component_id": "utils",
       "component_name": "Utils Component"
     }
   }
   ```

2. **Template-Based Recipes**:

   ```json
   {
     "type": "execute_recipe",
     "recipe_path": "recipes/component_template.json",
     "context_overrides": {
       "template_type": "create",
       "component_id": "{{component_id}}"
     }
   }
   ```

3. **Multi-Step Workflows**:
   ```json
   {
     "type": "execute_recipe",
     "recipe_path": "recipes/workflow/{{workflow_name}}.json"
   }
   ```

## Important Notes

1. The sub-recipe receives the same context object as the parent recipe
2. Context overrides are applied before sub-recipe execution
3. Changes made to the context by the sub-recipe persist after it completes
4. Template variables in both recipe_path and context_overrides are resolved before execution
5. Sub-recipes can execute their own sub-recipes (nested execution)


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/execute_recipe.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/execute_recipe/execute_recipe_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_spec.md ===
# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler modules, following the building block inspired approach to recipe construction.

## Core Requirements

- Execute sub-recipes from a specified file path
- Share the current context with sub-recipes
- Support context overrides for sub-recipe execution
- Apply template rendering to recipe paths and context overrides
- Include appropriate logging for sub-recipe execution
- Follow minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Logging

- Debug: None
- Info: Log the path of the sub-recipe being executed at both start and end of execution

## Component Dependencies

### Internal Components

- **Steps Base** - (Required) Extends BaseStep to implement the step interface
- **Context** - (Required) Shares context between main recipe and sub-recipes
- **Executor** - (Required) Uses Executor to run the sub-recipe
- **Utils** - (Required) Uses render_template for dynamic content resolution in paths and context overrides

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include sub-recipe path in error messages for debugging

## Output Files

- `steps/execute_recipe.py`

## Future Considerations

- Support for recipe content passed directly in configuration
- Context isolation options for sub-recipes
- Result mapping from sub-recipes back to parent recipes
- Conditional sub-recipe execution


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm/llm_docs.md",
      "artifact": "llm_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "generate_llm",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<LLM_DOCS>\n{{llm_docs}}\n</LLM_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_docs.md ===
# GenerateWithLLMStep Component Usage

## Importing

```python
from recipe_executor.steps.generate_llm import GenerateWithLLMStep, GenerateLLMConfig
```

## Configuration

The GenerateWithLLMStep is configured with a GenerateLLMConfig:

```python
class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider:model_name format).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str
```

## Step Registration

The GenerateWithLLMStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.generate_llm import GenerateWithLLMStep

STEP_REGISTRY["generate"] = GenerateWithLLMStep
```

## Basic Usage in Recipes

The GenerateWithLLMStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate Python code for a utility that: {{requirements}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generation_result"
    }
  ]
}
```

## Template-Based Prompts

The prompt can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/component_spec.md",
      "artifact": "spec"
    },
    {
      "type": "generate",
      "prompt": "You are an expert Python developer. Based on the following specification, generate code for a component:\n\n{{spec}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Model Selection

The model identifier can also use template variables:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code based on: {{spec}}",
      "model": "{{model_provider|default:'openai'}}:{{model_name|default:'o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Artifact Keys

The artifact key can be templated to create dynamic storage locations:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code for: {{component_name}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "{{component_name}}_result"
    }
  ]
}
```

## Implementation Details

The GenerateWithLLMStep works by:

1. Rendering the prompt with the current context
2. Rendering the model identifier
3. Rendering the artifact key (if it contains templates)
4. Calling the LLM with the rendered prompt and model
5. Storing the result in the context under the artifact key

```python
def execute(self, context: Context) -> None:
    # Process the artifact key using templating if needed
    artifact_key = self.config.artifact
    if "{{" in artifact_key and "}}" in artifact_key:
        artifact_key = render_template(artifact_key, context)

    # Render the prompt and model with the current context
    rendered_prompt = render_template(self.config.prompt, context)
    rendered_model = render_template(self.config.model, context)

    # Call the LLM
    self.logger.info(f"Calling LLM with prompt for artifact: {artifact_key}")
    response = call_llm(rendered_prompt, rendered_model)

    # Store the LLM response in context
    context[artifact_key] = response
    self.logger.debug(f"LLM response stored in context under '{artifact_key}'")
```

## LLM Response Format

The response from call_llm is a FileGenerationResult object:

```python
# FileGenerationResult structure
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)
```

## Error Handling

The GenerateWithLLMStep can raise several types of errors:

```python
try:
    generate_step.execute(context)
except ValueError as e:
    # Template rendering or model format errors
    print(f"Value error: {e}")
except RuntimeError as e:
    # LLM call failures
    print(f"Runtime error: {e}")
```

## Common Use Cases

1. **Code Generation**:

   ```json
   {
     "type": "generate",
     "prompt": "Generate Python code for: {{specification}}",
     "model": "{{model|default:'openai:o3-mini'}}",
     "artifact": "code_result"
   }
   ```

2. **Content Creation**:

   ```json
   {
     "type": "generate",
     "prompt": "Write a blog post about: {{topic}}",
     "model": "anthropic:claude-3-haiku",
     "artifact": "blog_post"
   }
   ```

3. **Analysis and Transformation**:
   ```json
   {
     "type": "generate",
     "prompt": "Analyze this code and suggest improvements:\n\n{{code}}",
     "model": "{{model|default:'openai:o3-mini'}}",
     "artifact": "code_analysis"
   }
   ```

## Important Notes

1. The artifact key can be dynamic using template variables
2. The prompt is rendered using the current context before sending to the LLM
3. The model identifier follows the format "provider:model_name"
4. The LLM response is a FileGenerationResult object with files and commentary
5. LLM calls may incur costs with the respective provider


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/generate_llm.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/generate_llm/generate_llm_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/generate_llm/generate_llm_spec.md ===
# GenerateWithLLMStep Component Specification

## Purpose

The GenerateWithLLMStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, and storing generation results in the context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Call LLMs to generate content
- Store generated results in the context
- Support dynamic artifact key resolution
- Include appropriate logging for LLM operations

## Implementation Considerations

- Use template rendering for dynamic prompt generation
- Support template rendering in model selection
- Allow dynamic artifact key through template rendering
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about LLM requests

## Logging

- Debug: Log that the LLM call is being made (leave the details to the LLM component to log)
- Info: None

## Component Dependencies

### Internal Components

- **Steps Base** - (Required) Extends BaseStep to implement the step interface
- **Context** - (Required) Retrieves input values and stores generation results
- **LLM** - (Required) Uses call_llm function to interact with language models
- **Utils** - (Required) Uses render_template for dynamic content resolution in prompts and model identifiers

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls

## Output Files

- `steps/generate_llm.py`

## Future Considerations

- Additional LLM parameters (temperature, max tokens, etc.)


=== File: recipes/recipe_executor/components/steps/parallel/parallel_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "parallel",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/parallel/parallel_docs.md ===
# ParallelStep Component Usage

## Importing

To use the ParallelStep in your project, import the step class and its configuration class from the recipe executor’s steps module:

```python
from recipe_executor.steps.parallel import ParallelStep, ParallelConfig
```

## Configuration

The ParallelStep is configured with a corresponding `ParallelConfig` class, which defines its parameters:

```python
class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc).
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default = 0 means no explicit limit (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay (all allowed substeps start immediately).
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0
```

In the configuration:

- **`substeps`** (required) is a list of step configurations, where each item is typically an object/dict specifying an `execute_recipe` step (with its `recipe_path`, and optionally `context_overrides`, etc.). This defines which sub-recipes will be run in parallel.
- **`max_concurrency`** (optional) limits how many sub-recipes run at the same time. For example, setting `max_concurrency` to 2 will ensure at most two substeps are executing in parallel; additional substeps will wait until a slot is free. If this value is 0 or not set, the ParallelStep will attempt to run all substeps concurrently (unbounded, which effectively means as many threads as substeps).
- **`delay`** (optional) if provided, introduces a pause between launching each substep. This is useful to stagger execution starts. For instance, a delay of `1.5` means after starting one substep, the ParallelStep will wait 1.5 seconds before starting the next substep. By default this is 0, meaning no deliberate delay between thread launches.

## Step Registration

Like other step types, the ParallelStep must be registered so the Recipe Executor knows about it. This is typically done in the steps registry setup:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.parallel import ParallelStep

STEP_REGISTRY["parallel"] = ParallelStep
```

Registering the `"parallel"` type ensures that when a recipe contains a step with `"type": "parallel"`, the executor will instantiate and use a `ParallelStep` to execute it.

## Basic Usage in Recipes

The ParallelStep is used in recipes to run multiple sub-recipes concurrently. This is ideal when you have several independent tasks that can be executed in parallel to reduce overall runtime. For example, suppose you want to run two separate sub-recipes at the same time — you can define a parallel step as follows:

```json
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "recipes/subtask_a.json",
          "context_overrides": {
            "input_data": "{{shared_input}}"
          }
        },
        {
          "type": "execute_recipe",
          "recipe_path": "recipes/subtask_b.json",
          "context_overrides": {
            "input_data": "{{shared_input}}"
          }
        }
      ],
      "max_concurrency": 2,
      "delay": 1
    }
  ]
}
```

In this JSON snippet:

- The `ParallelStep` is represented by an object with `"type": "parallel"`. It contains a `substeps` array defining two sub-steps, each of which is an `execute_recipe` step running a sub-recipe (`subtask_a.json` and `subtask_b.json`). Both sub-recipes in this example use a context value `shared_input` (passed via context overrides) but they will run in isolation from each other.
- The `max_concurrency` is set to `2`, meaning up to two substeps can run at the same time. Here we have exactly two substeps, so they will indeed run simultaneously. If there were more substeps than the concurrency limit, the extra ones would wait until others finish before starting.
- The `delay` is set to `1` second. This will cause the ParallelStep to wait 1 second after launching the first substep (`subtask_a`) before launching the second substep (`subtask_b`). The delay can help in staggering the workload (for example, to avoid hitting a resource spike by starting many tasks at the exact same moment). In this case, since `max_concurrency` is 2 and we have 2 substeps, both will still run in parallel (just with a 1-second offset in their start times).

When the ParallelStep executes, it will start both **Subtask A** and **Subtask B** almost concurrently (with the specified delay). Each subtask will run in its own cloned context, so any changes they make to context (like artifacts or intermediate data) remain in their sub-recipe’s context. The parent recipe’s context (`shared_input` in this case) is not modified by the sub-recipes, unless you explicitly write results back to it (which by default does not happen in the current design).

## Error Handling

If any sub-recipe within the parallel step fails or throws an error, the ParallelStep will halt and propagate that error immediately (fail-fast). This means you should be prepared to catch exceptions from a ParallelStep execution just as you would for other steps. For example:

```python
try:
    parallel_step.execute(context)
except Exception as e:
    # If any substep fails, an exception will be raised here
    print(f"Parallel step failed: {e}")
```

In practice, the type of exception will depend on the nature of the sub-recipe failure. For instance, if one sub-recipe tries to read a missing file, a `FileNotFoundError` might be raised; if a sub-recipe has an invalid configuration, it could raise a `ValueError` or custom step error. The ParallelStep does not yet define a special exception type for aggregated errors, so it will typically raise the first encountered sub-step exception. The error message should include information to identify which substep failed (e.g., the recipe path or an index) to aid in debugging. All other substeps will be canceled or stopped as soon as an error is detected, so their effects (if any) might be partial or rolled back when the exception is raised.

## Important Notes

1. **Context Isolation:** Each substep runs with its own cloned Context. The ParallelStep uses a deep copy of the parent context for each sub-recipe, meaning substeps do not share state with each other. Any modifications a sub-recipe makes to its context will _not_ appear in the parent or sibling contexts. This prevents race conditions or data leaks between parallel tasks. (The parent context remains unchanged by default through the parallel execution.)
2. **Concurrency Control:** The `max_concurrency` setting governs how many sub-recipes execute simultaneously. If you have more substeps than the `max_concurrency`, the extra substeps will wait in a queue until a running substep finishes. By default (`max_concurrency: 0` meaning unlimited), the ParallelStep will launch all substeps at once, which can maximize parallelism but also increase load on the system. It’s often wise to set a reasonable limit based on your environment (e.g., number of CPU cores or external API rate limits).
3. **Launch Delay:** Using the `delay` parameter, you can stagger the start of each parallel task. In high-load scenarios, a slight delay (even a fraction of a second) between launches can prevent all threads from spiking at exactly the same time. The delay is applied between each substep launch. For example, with `delay: 2`, there will be a 2-second pause before launching each subsequent substep. If `max_concurrency` is also set, the delay still applies as long as additional substeps are being started.
4. **Fail-Fast Behavior:** ParallelStep is designed to fail fast. If any one of the parallel sub-recipes fails, the entire ParallelStep is considered failed immediately. In such a case, no further substeps will be started, and any substeps that are still running may be interrupted or will be awaited to stop. This ensures that you don’t continue a workflow when part of the parallel work has gone wrong. You should design parallel tasks such that they can either all succeed or handle partial failure if that’s acceptable (future enhancements may allow continuing despite one failure, but currently the behavior is to abort on first error).
5. **Limitations:** As of now, the ParallelStep can only execute substeps of type `execute_recipe`. In other words, each parallel subtask must be an entire sub-recipe executed via an ExecuteRecipeStep. You cannot yet list arbitrary step types under `substeps` (e.g., you cannot directly put a `"type": "read_file"` step in substeps for parallel execution at this time). This may be expanded in the future to allow more flexible parallelization of different step kinds.
6. **No Automatic Result Merging:** Results produced by sub-recipes (for example, artifacts or context changes within those sub-recipes) are not automatically merged back into the parent context. Currently, the ParallelStep treats sub-recipes as isolated parallel jobs whose side-effects remain in their own contexts. If you need to use results from sub-recipes, you would have to handle that in the sub-recipes themselves (e.g. writing to a common output or updating an external resource), or a future enhancement of ParallelStep may provide a way to collect outputs. This is an important consideration when designing your recipes – ensure that either the parallel tasks are truly independent or that you implement a mechanism to consolidate their outcomes afterward.


=== File: recipes/recipe_executor/components/steps/parallel/parallel_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/parallel.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/parallel/parallel_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/parallel/parallel_spec.md ===
# ParallelStep Component Specification

## Purpose

The ParallelStep component enables the Recipe Executor to run multiple sub-recipes concurrently within a single step. It improves execution efficiency by parallelizing independent tasks while maintaining isolation between them.

## Core Requirements

- Accept a list of sub-step configurations (each of type `execute_recipe`)
- Clone the current execution context for each sub-step to ensure isolation
- Execute sub-steps concurrently with a configurable maximum concurrency limit
- Support optional delay between launching sub-steps
- Wait for all sub-steps to complete before proceeding
- Implement fail-fast behavior: if any sub-step fails, stop launching new ones and report the error

## Implementation Considerations

- Use a ThreadPoolExecutor to manage parallel execution of sub-steps
- Use Context.clone() to create independent context copies for each sub-step
- Implement configurable launch delay using time.sleep for staggered start times
- Monitor exceptions from each thread and implement fail-fast behavior
- Provide clear logging for sub-step lifecycle events and execution summary
- Manage resources efficiently to prevent memory or thread management issues

## Component Dependencies

### Internal Components

- **Steps Base** - (Required) Inherits from BaseStep for integration with the step execution framework
- **Context** - (Required) Uses Context.clone() to create isolated contexts for each parallel sub-step
- **Step Registry** - (Required) Uses registry to instantiate execute_recipe step for sub-steps
- **Executor** - (Required) Uses Executor to run each sub-recipe in separate threads
- **Utils** - (Optional) Uses template rendering for sub-step configurations

### External Libraries

- **ThreadPoolExecutor** - (Required) Uses concurrent.futures.ThreadPoolExecutor for parallel execution
- **time** - (Optional) Uses time.sleep for implementing launch delays between sub-steps

### Configuration Dependencies

None

## Output Files

- `recipe_executor/steps/parallel/parallel.py` - Implementation of the ParallelStep class

## Logging

- Debug: Log sub-step start/completion events, thread allocation, and configuration details
- Info: Log start/completion with summary of parallel execution including numuber of steps and success/failure counts

## Error Handling

- Implement fail-fast behavior when any sub-step encounters an error
- Cancel pending sub-steps when an error occurs
- Include clear error context identifying which sub-step failed
- Ensure proper thread pool shutdown to prevent orphaned threads
- Propagate the original exception with contextual information about the failure

## Future Considerations

- Support for arbitrary step types beyond just execute_recipe
- Result aggregation from sub-steps back to parent context
- Dynamic concurrency control based on system load
- Timeout and isolation options for sub-steps


=== File: recipes/recipe_executor/components/steps/read_file/read_file_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "read_file",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/read_file/read_file_docs.md ===
# ReadFileStep Component Usage

## Importing

```python
from recipe_executor.steps.read_file import ReadFileStep, ReadFileConfig
```

## Configuration

The ReadFileStep is configured with a ReadFileConfig:

```python
class ReadFileConfig(StepConfig):
    """
    Configuration for ReadFileStep.

    Fields:
        path (str): Path to the file to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if the file is not found.
    """

    path: str
    artifact: str
    optional: bool = False
```

## Step Registration

The ReadFileStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_file import ReadFileStep

STEP_REGISTRY["read_file"] = ReadFileStep
```

## Basic Usage in Recipes

The ReadFileStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/component_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

## Template-Based Paths

The path can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

## Optional Files

You can specify that a file is optional, and execution will continue even if the file doesn't exist:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/optional_file.md",
      "artifact": "optional_content",
      "optional": true
    }
  ]
}
```

If an optional file is not found, an empty string is stored in the context.

## Implementation Details

The ReadFileStep works by:

1. Resolving the path using template rendering
2. Checking if the file exists
3. Reading the file content
4. Storing the content in the context

```python
def execute(self, context: Context) -> None:
    # Render the path using the current context
    path = render_template(self.config.path, context)

    # Check if file exists
    if not os.path.exists(path):
        if self.config.optional:
            self.logger.warning(f"Optional file not found at path: {path}, continuing anyway")
            context[self.config.artifact] = ""  # Set empty string for missing optional file
            return
        else:
            raise FileNotFoundError(f"ReadFileStep: file not found at path: {path}")

    # Read the file
    self.logger.info(f"Reading file from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Store in context
    context[self.config.artifact] = content
    self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")
```

## Error Handling

If a file doesn't exist and is not marked as optional, the step will raise a FileNotFoundError:

```python
try:
    read_file_step.execute(context)
except FileNotFoundError as e:
    print(f"File error: {e}")
    # Handle the error
```

## Common Use Cases

1. **Loading Specifications**:

   ```json
   {
     "type": "read_file",
     "path": "specs/component_spec.md",
     "artifact": "spec"
   }
   ```

2. **Loading Templates**:

   ```json
   {
     "type": "read_file",
     "path": "templates/email_template.txt",
     "artifact": "email_template"
   }
   ```

3. **Dynamic Path Resolution**:
   ```json
   {
     "type": "read_file",
     "path": "docs/{{project}}/{{component}}.md",
     "artifact": "documentation"
   }
   ```

## Important Notes

1. The step uses UTF-8 encoding by default
2. The file content is stored as a string in the context
3. Template variables in the path are resolved before reading the file
4. When a file is optional and missing, an empty string is stored


=== File: recipes/recipe_executor/components/steps/read_file/read_file_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/read_file.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/read_file/read_file_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/read_file/read_file_spec.md ===
# ReadFileStep Component Specification

## Purpose

The ReadFileStep component reads a file from the filesystem and stores its contents in the execution context. It serves as a foundational step for loading data into recipes, such as specifications, templates, and other input files.

## Core Requirements

- Read a file from a specified path
- Support template-based path resolution
- Store file contents in the context under a specified key
- Provide optional file handling for cases when files might not exist
- Include appropriate logging and error messages
- Follow minimal design with clear error handling

## Implementation Considerations

- Use template rendering to support dynamic paths
- Handle missing files explicitly with meaningful error messages
- Use consistent UTF-8 encoding for text files
- Implement optional flag to continue execution if files are missing
- Keep the implementation simple and focused on a single responsibility

## Logging

- Debug: Log the file path attempting to be read prior to reading (in case of failure)
- Info: Log the successful reading of the file (including path) and its storage in the context (including key)

## Component Dependencies

### Internal Components

- **Steps Base** - (Required) Extends BaseStep to implement the step interface
- **Context** - (Required) Stores file contents in the context under specified key
- **Utils** - (Required) Uses render_template for dynamic path resolution

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Raise FileNotFoundError with clear message when files don't exist
- Support optional flag to continue execution with empty content
- Log appropriate warnings and information during execution

## Output Files

- `steps/read_file.py`

## Future Considerations

- Directory reading and file globbing


=== File: recipes/recipe_executor/components/steps/registry/registry_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "registry",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/registry/registry_docs.md ===
# Step Registry Component Usage

## Importing

```python
from recipe_executor.steps.registry import STEP_REGISTRY
```

## Registry Structure

The registry is a simple dictionary that maps step type names to their implementation classes:

```python
# Type definition
from typing import Dict, Type
from recipe_executor.steps.base import BaseStep

# Structure of STEP_REGISTRY
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_file": ReadFileStep,
    "write_files": WriteFilesStep,
}
```

Custom steps can be registered in the same way:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.base import BaseStep
from my_custom_steps import CustomStep

# Register a custom step implementation
STEP_REGISTRY["custom_step"] = CustomStep
```

## Looking Up Steps

The executor uses the registry to look up step classes by type:

```python
# Example of registry usage in executor
from typing import Dict, Any
import logging
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY

def execute_step(step: Dict[str, Any], context: Context, logger: logging.Logger) -> None:
    step_type = step["type"]
    if step_type not in STEP_REGISTRY:
        raise ValueError(f"Unknown step type '{step_type}'")

    step_class = STEP_REGISTRY[step_type]
    step_instance = step_class(step, logger)
    step_instance.execute(context)
```

## Important Notes

1. Step type names must be unique across the entire system
2. Steps must be registered before the executor tries to use them
3. Standard steps are automatically registered when the package is imported
4. Custom steps need to be explicitly registered by the user


=== File: recipes/recipe_executor/components/steps/registry/registry_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/registry.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/registry/registry_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/registry/registry_spec.md ===
# Step Registry Component Specification

## Purpose

The Step Registry component provides a central mechanism for registering and looking up step implementations by their type names. It enables the dynamic discovery of step classes during recipe execution.

## Core Requirements

- Provide a simple mapping between step type names and their implementation classes
- Support registration of step implementations from anywhere in the codebase
- Enable the executor to look up step classes by their type name
- Follow a minimal, dictionary-based approach with no unnecessary complexity

## Implementation Considerations

- Use a single, global dictionary to store all step registrations
- Allow steps to register themselves upon import
- Keep the registry structure simple and stateless
- Avoid unnecessary abstractions or wrapper functions

## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

None

### Configuration Dependencies

None

## Output Files

- `steps/registry.py`
- `steps/__init__.py` (details below)

Create the `__init__.py` file in the `steps` directory to ensure it is treated as a package. Steps are registered in the steps package `__init__.py`:

```python
# In recipe_executor/steps/__init__.py
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register steps by updating the registry
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_file": ReadFileStep,
    "write_files": WriteFilesStep,
})
```

## Future Considerations

- Dynamic loading of external step implementations
- Step metadata and documentation


=== File: recipes/recipe_executor/components/steps/write_files/write_files_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/base/base_docs.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/models/models_docs.md",
      "artifact": "models_docs"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_docs.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "write_files",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/write_files/write_files_docs.md ===
# WriteFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.write_files import WriteFilesStep, WriteFilesConfig
```

## Configuration

The WriteFilesStep is configured with a WriteFilesConfig:

```python
class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        artifact: Name of the context key holding a FileGenerationResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """

    artifact: str
    root: str = "."
```

## Step Registration

The WriteFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

STEP_REGISTRY["write_files"] = WriteFilesStep
```

## Basic Usage in Recipes

The WriteFilesStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "output/project"
    }
  ]
}
```

## Supported Context Values

The WriteFilesStep can work with two types of artifacts in the context:

### 1. FileGenerationResult

```python
from recipe_executor.models import FileGenerationResult, FileSpec

# Example of generating a FileGenerationResult
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)

# Store in context
context["generated_code"] = result
```

### 2. List of FileSpec objects

```python
from recipe_executor.models import FileSpec

# Example of generating a list of FileSpec objects
files = [
    FileSpec(path="src/main.py", content="print('Hello, world!')"),
    FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
]

# Store in context
context["generated_files"] = files
```

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "output/{{project_name}}"
    }
  ]
}
```

File paths within the FileSpec objects can also contain templates:

```python
FileSpec(
    path="{{component_name}}/{{filename}}.py",
    content="# Generated code for {{component_name}}"
)
```

## Implementation Details

The WriteFilesStep works by:

1. Retrieving the artifact from the context
2. Validating it's a FileGenerationResult or list of FileSpec objects
3. Rendering the root path using template rendering
4. For each file:
   - Rendering the file path
   - Creating the necessary directories
   - Writing the file content

```python
def execute(self, context: Context) -> None:
    # Get data from context
    data = context.get(self.config.artifact)

    if data is None:
        raise ValueError(f"No artifact found at key: {self.config.artifact}")

    # Determine file list
    if isinstance(data, FileGenerationResult):
        files = data.files
    elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
        files = data
    else:
        raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

    # Render output root
    output_root = render_template(self.config.root, context)

    # Write each file
    for file in files:
        rel_path = render_template(file.path, context)
        full_path = os.path.join(output_root, rel_path)

        # Create directories
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file.content)

        self.logger.info(f"Wrote file: {full_path}")
```

## Error Handling

The WriteFilesStep can raise several types of errors:

```python
try:
    write_step.execute(context)
except ValueError as e:
    # Missing or invalid artifact
    print(f"Value error: {e}")
except TypeError as e:
    # Unexpected artifact type
    print(f"Type error: {e}")
except IOError as e:
    # File writing errors
    print(f"I/O error: {e}")
```

## Common Use Cases

1. **Writing Generated Code**:

   ```json
   {
     "type": "write_files",
     "artifact": "generated_code",
     "root": "output/src"
   }
   ```

2. **Project-Specific Output**:

   ```json
   {
     "type": "write_files",
     "artifact": "project_files",
     "root": "output/{{project_name}}"
   }
   ```

3. **Component Generation**:
   ```json
   {
     "type": "write_files",
     "artifact": "component_result",
     "root": "output/components"
   }
   ```

## Important Notes

1. Directories are created automatically if they don't exist
2. Files are overwritten without confirmation if they already exist
3. All paths are rendered using template variables from the context
4. File content is written using UTF-8 encoding
5. Both FileGenerationResult and List[FileSpec] formats are supported


=== File: recipes/recipe_executor/components/steps/write_files/write_files_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/steps/write_files.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/write_files/write_files_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/steps/write_files/write_files_spec.md ===
# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both FileGenerationResult and list of FileSpec formats
- Create directories as needed for file paths
- Apply template rendering to file paths
- Provide appropriate logging for file operations
- Follow minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (FileGenerationResult or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Logging

- Debug: Log the file path and content being written before writing (in case of failure)
- Info: Log the successful writing of the file (including path) and its content size

## Component Dependencies

### Internal Components

- **Steps Base** - (Required) Extends BaseStep to implement the step interface
- **Context** - (Required) Retrieves file content from the context
- **Models** - (Required) Uses FileGenerationResult and FileSpec models for content structure
- **Utils** - (Required) Uses render_template for dynamic path resolution

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the artifact exists in context
- Ensure artifact contains a valid FileGenerationResult or list of FileSpec objects
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Output Files

- `steps/write_files.py`

## Future Considerations

- Dry-run mode that logs without writing


=== File: recipes/recipe_executor/components/utils/utils_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_docs.md",
      "artifact": "context_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/utils/build_component.json",
      "context_overrides": {
        "component_id": "utils",
        "component_path": "/",
        "existing_code": "{{existing_code}}",
        "additional_content": "<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/utils/utils_docs.md ===
# Utils Component Usage

## Importing

```python
from recipe_executor.utils import render_template
```

## Template Rendering

The Utils component provides a `render_template` function that renders Liquid templates using values from the Context:

```python
def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

Basic usage example:

```python
from recipe_executor.context import Context
from recipe_executor.utils import render_template

# Create a context with values
context = Context(artifacts={"name": "World", "count": 42})

# Render a template
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Liquid syntax:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains dictionaries)
template = "Author: {{book.author}}"
```

### Conditionals

```python
template = "{% if user_count > 0 %}Users: {{user_count}}{% else %}No users{% endif %}"
```

### Loops

```python
template = "{% for item in items %}Item: {{item}}{% endfor %}"
```

## Type Handling

All values from the context are converted to strings before rendering:

```python
# Context with mixed types
context = Context(artifacts={
    "number": 42,
    "boolean": True,
    "list": [1, 2, 3],
    "dict": {"key": "value"}
})

# All values become strings in templates
template = "Number: {{number}}, Boolean: {{boolean}}, List: {{list}}, Dict: {{dict}}"
# Renders as: "Number: 42, Boolean: True, List: [1, 2, 3], Dict: {'key': 'value'}"
```

## Error Handling

Template rendering errors are wrapped in a ValueError:

```python
try:
    result = render_template("{% invalid syntax %}", context)
except ValueError as e:
    print(f"Template error: {e}")
    # Handle the error
```

## Common Usage Patterns

### In Step Classes

The primary use of template rendering is in step execution:

```python
# Example from ReadFileStep.execute()
def execute(self, context: Context) -> None:
    # Render the path using the current context
    path = render_template(self.config.path, context)

    # Read the file at the rendered path
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Store in context (with rendered artifact key if needed)
    artifact_key = render_template(self.config.artifact, context)
    context[artifact_key] = content
```

### In Recipe Steps

Templates are typically used in recipe step configurations:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    },
    {
      "type": "generate",
      "prompt": "Generate code based on: {{component_spec}}",
      "model": "{{model_id|default:'openai:o3-mini'}}",
      "artifact": "generated_code"
    }
  ]
}
```

## Important Notes

1. All context values are converted to strings, which may affect formatting
2. Template rendering is synchronous and blocking
3. The Context's `as_dict()` method is used to access all artifacts
4. Empty or missing variables will be replaced with an empty string


=== File: recipes/recipe_executor/components/utils/utils_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{% if existing_code_root %}{{existing_code_root}}/{% endif %}recipe_executor/utils.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/components/utils/utils_spec.md ===
# Utils Component Specification

## Purpose

The Utils component provides utility functions for the Recipe Executor system, primarily focusing on template rendering. It enables steps to use dynamic values from the context in their configuration through a simple templating mechanism.

## Core Requirements

- Provide a template rendering function using the Liquid templating engine
- Support substituting values from the Context into templates
- Handle all context values by converting them to strings
- Provide clear error handling for template rendering failures
- Follow minimal design with focused functionality

## Implementation Considerations

- Use the Liquid library directly without unnecessary abstraction
- Convert context values to strings before rendering to prevent type errors
- Handle rendering errors gracefully with clear error messages
- Keep the implementation stateless and focused

## Logging

- Debug: Log the template being rendered and the context keys used
- Info: None

## Component Dependencies

### Internal Components

- **Context** - (Required) Uses the Context class for accessing artifacts during template rendering

### External Libraries

- **Liquid** - (Required) Uses the Liquid templating engine for template rendering (`python-liquid`)
- **json** - (Required) Uses json module for handling dictionary conversions

### Configuration Dependencies

None

## Error Handling

- Wrap template rendering in try/except blocks
- Provide specific error messages that indicate the source of template failures
- Propagate rendering errors with useful context

## Output Files

- `utils.py`

## Future Considerations

- Support for custom template filters or tags
- Support for template partials or includes
- Template validation before rendering


=== File: recipes/recipe_executor/create.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/logger/logger_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/models/models_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm/llm_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm_utils/azure_openai/azure_openai_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/executor/executor_create.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/main/main_create.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/create.json"
    }
  ]
}


=== File: recipes/recipe_executor/edit.json ===
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/context/context_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/logger/logger_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/models/models_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/utils/utils_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm/llm_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/llm_utils/azure_openai/azure_openai_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/executor/executor_edit.json"
        },
        {
          "type": "execute_recipe",
          "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/main/main_edit.json"
        }
      ],
      "max_concurrency": 0,
      "delay": 0
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/recipe_executor/components/steps/edit.json"
    }
  ]
}


=== File: recipes/recipe_executor/utils/build_component.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components{{component_path}}{% if component_path != '/' %}/{% endif %}{{component_id}}/{{component_id}}_spec.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "{{recipe_root|default:'recipes'}}/recipe_executor/components{{component_path}}{% if component_path != '/' %}/{% endif %}{{component_id}}/{{component_id}}_docs.md",
      "artifact": "usage_docs",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "{{recipe_root|default:'recipes'}}/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "{{model|default:'openai:o3-mini'}}",
        "output_root": "{{output_root|default:'output'}}",
        "output_path": "recipe_executor{{component_path}}",
        "language": "{{language|default:'python'}}",
        "spec": "{{spec}}",
        "usage_docs": "{{usage_docs}}",
        "existing_code": "{{existing_code}}",
        "additional_content": "{{additional_content}}"
      }
    }
  ]
}


