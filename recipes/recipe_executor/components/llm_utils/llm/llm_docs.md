# LLM Component Usage

## Importing

```python
from recipe_executor.llm_utils.llm import call_llm
```

## Basic Usage

The LLM component provides one main function:

```python
class LLM:
    def __init__(
            self,
            logger: logging.Logger,
            model: str = "openai/gpt-4o"
        ):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            model (str): Model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                Default is "openai/gpt-4o".
        """
        self.model = model
        self.logger = logger

    async def generate(
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
    ) -> Union[str, BaseModel]:
        """
        Generate a response from the LLM based on the provided prompt.

        Args:
            prompt (str): The prompt string to be sent to the LLM.
            model (Optional[str]): The model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                If not provided, the default model set during initialization will be used.
            output_type (Type[Union[str, BaseModel]]): The requested output type for the LLM response.
                - str: Plain text response (default).
                - BaseModel: Structured response based on the provided JSON schema.

        Returns:
            Union[str, BaseModel]: The response from the LLM, either as plain text or structured data.

        Raises:
            Exception: If model value cannot be mapped to valid provider/model_name , LLM call fails, or result validation fails.
        """
```

Usage example:

```python
llm = LLM(logger=logger)

# Call LLM with default model
result = async llm.generate("What is the capital of France?")

# Call with specific model
result = async llm.generate(
    prompt="What is the capital of France?",
    model="openai/o3-mini"
)

# Call with JSON schema validation
class UserProfile(BaseModel):
    name: str
    age: int
    email: str

result = async llm.generate(
    prompt="Extract the user profile from the following text: {{text}}",
    model="openai/o3-mini",
    output_type=UserProfile
)
```

## Model ID Format

The component uses a standardized model identifier format:

All models: `provider/model_name`
Example: `openai/o3-mini`

Azure OpenAI models with custom deployment name: `azure/model_name/deployment_name`
Example: `azure/gpt-4o/my_deployment_name`
If no deployment name is provided, the model name is used as the deployment name.

### Supported providers:

- **openai**: OpenAI models (e.g., `gpt-4o`, `o3-mini`)
- **azure**: Azure OpenAI models (e.g., `gpt-4o`, `o3-mini`)
- **azure**: Azure OpenAI models with custom deployment name (e.g., `gpt-4o/my_deployment_name`)
- **anthropic**: Anthropic models (e.g., `claude-3-7-sonnet-latest`)
- **ollama**: Ollama models (e.g., `phi4`, `llama3.2`, `qwen2.5-coder:14b`)

## Error Handling

Example of error handling:

```python
try:
    result = async llm.generate(prompt, model_id)
    # Process result
except ValueError as e:
    # Handle invalid model ID or format
    print(f"Invalid model configuration: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"LLM call failed: {e}")
```

## Important Notes

- OpenAI is the default provider if none is specified
- The component logs full request details at debug level
