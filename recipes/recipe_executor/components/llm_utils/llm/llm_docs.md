# LLM Component Usage

## Importing

```python
from recipe_executor.llm_utils.llm import call_llm
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
custom_agent = get_agent(model_id="anthropic:claude-3-7-sonnet-latest")
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
- **anthropic**: Anthropic models (e.g., `claude-3-7-sonnet-latest`)
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
def execute(self, context: ContextProtocol) -> None:
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
