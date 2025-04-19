# LLM Component Usage

## Importing

```python
from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import create_mcp_server_config
```

## Basic Usage

The LLM component provides one main function:

```python
class LLM:
    def __init__(
            self,
            logger: logging.Logger,
            model: str = "openai/gpt-4o",
            mcp_servers: Optional[List[MCPServer]] = None,
        ):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            model (str): Model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                Default is "openai/gpt-4o".
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
        """
        self.model = model
        self.logger = logger
        self.mcp_servers = mcp_servers

    async def generate(
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.

        Args:
            prompt (str): The prompt string to be sent to the LLM.
            model (Optional[str]): The model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                If not provided, the default set during initialization will be used.
            output_type (Type[Union[str, BaseModel]]): The requested type for the LLM output.
                - str: Plain text output (default).
                - BaseModel: Structured output based on the provided JSON schema.
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
                If not provided, the default set during initialization will be used.

        Returns:
            Union[str, BaseModel]: The output from the LLM, either as plain text or structured data.

        Raises:
            Exception: If any of the following occurs:
                - Invalid model ID or format.
                - Unsupported provider.
                - MCP server errors.
                - Network or API errors.
                - JSON schema validation errors.
        """
```

Usage example:

````python
from recipe_executor.llm_utils.mcp import get_mcp_server

llm = LLM(logger=logger)
# With optional MCP integration:
weather_mcp_server = get_mcp_server(
    logger=logger,
    config={
        "url": "http://localhost:3001/sse",
        "headers": {
            "Authorization": "{{token}}"
        },
    }
)
llm_mcp = LLM(logger=logger, mcp_servers=[weather_mcp_server])

# Call LLM with default model
result = await llm.generate("What is the weather in Redmond, WA today?")

# Call with specific model
result = await llm.generate(
    prompt="What is the capital of France?",
    model="openai/o3-mini"
)

# Call with JSON schema validation
class UserProfile(BaseModel):
    name: str
    age: int
    email: str

result = await llm.generate(
    prompt="Extract the user profile from the following text: {{text}}",
    model="openai/o3-mini",
    output_type=UserProfile
)

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
````

## Important Notes

- OpenAI is the default provider if none is specified
- The component logs full request details at debug level
