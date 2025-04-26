# AI Context Files
Date: 4/26/2025, 12:07:48 AM
Files: 25

=== File: .env.example ===
# Optional for the project
#LOG_LEVEL=DEBUG

# Required for the project
OPENAI_API_KEY=

# Additional APIs
#ANTHROPIC_API_KEY=
#GEMINI_API_KEY=

# Azure OpenAI
#AZURE_OPENAI_BASE_URL=
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_USE_MANAGED_IDENTITY=false
#AZURE_OPENAI_API_KEY=

#(Optional) The client ID of the specific managed identity to use.
#  If not provided, DefaultAzureCredential will be used.
#AZURE_MANAGED_IDENTITY_CLIENT_ID=


=== File: README.md ===
# Recipe Tools

A tool for executing recipe-like natural language instructions to create complex workflows. This project includes a recipe executor and a recipe creator, both of which can be used to automate tasks and generate new recipes.

## Overview

This project is designed to help you automate tasks and generate new recipes using a flexible orchestration system. It consists of two main components: the Recipe Executor and the Recipe Creator.

### Recipe Executor

The Recipe Executor is a tool for executing recipes defined in JSON format. It can perform various tasks, including file reading/writing, LLM generation, and sub-recipe execution. The executor uses a context system to manage shared state and data between steps.

### Recipe Creator

The Recipe Creator is a tool for generating new recipes based on a recipe idea. It uses the Recipe Executor to create JSON recipe files that can be executed later. The creator can also take additional files as input to provide context for the recipe generation.

## Key Components

- **Recipe Executor**: Executes recipes defined in JSON format.
- **Recipe Creator**: Generates new recipes based on a recipe idea.
- **Recipe Format**: JSON-based recipe definitions with steps
- **Context Management**: Manages shared state and data between steps in a recipe.
- **Step Types**: Various operations including file reading/writing, LLM generation, and sub-recipe execution
  - **LLM Integration**: Supports various LLMs for generating content and executing tasks.
  - **File Management**: Reads and writes files as part of the recipe execution process.
  - **Sub-Recipe Execution**: Allows for executing other recipes as part of a larger recipe.
- **Logging**: Provides logging for debugging and tracking recipe execution.
- **Template Rendering**: Liquid templates for dynamic content generation

## Setup and Installation

### Prerequisites

Recommended installers:

- Linux: apt or your distribution's package manager
- macOS: [brew](https://brew.sh/)
- Windows: [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

#### Azure CLI for Azure OpenAI using Managed Identity

If you plan on using Azure OpenAI with Managed Identity, you need to install the Azure CLI. Follow the instructions for your platform:

- **Windows**: [Install the Azure CLI on Windows](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
- **Linux**: [Install the Azure CLI on Linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux)
- **macOS**: [Install the Azure CLI on macOS](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-macos)

Execute the following command to log in:

```bash
az login
```

This command will open a browser window for you to log in. If you are using Managed Identity, ensure that your Azure CLI is configured to use the correct identity.

#### Development tools

The core dependencies you need to install are:

- `make` - for scripting installation steps of the various projects within this repo
- `uv` - for managing installed versions of `python` - for installing python dependencies

Linux:

    # make is installed by default on linux
    sudo apt update && sudo apt install pipx
    pipx ensurepath
    pipx install uv

macOS:

    brew install make
    brew install uv

Windows:

    winget install ezwinports.make -e
    winget install astral-sh.uv  -e

### Setup Steps

1. Clone this repository
2. Copy the environment file and configure your API keys:
   ```bash
   cp .env.example .env
   # Edit .env to add your OPENAI_API_KEY and other optional API keys
   ```
3. Run the setup command to create a virtual environment and install dependencies:
   ```bash
   make
   ```
4. Activate the virtual environment:
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .\.venv\Scripts\activate
     ```
5. Test the installation by running the example recipe:
   ```bash
   make recipe-executor-create
   ```

## Using the Makefile

The project includes several useful make commands:

- **`make`**: Sets up the virtual environment and installs all dependencies
- **`make ai-context-files`**: Builds AI context files for recipe executor development
- **`make recipe-executor-create`**: Generates recipe executor code from scratch using the recipe itself
- **`make recipe-executor-edit`**: Revises existing recipe executor code using recipes

## Running Recipes via Command Line

Execute a recipe using the command line interface:

```bash
recipe-tool --execute path/to/your/recipe.json
```

You can also pass context variables:

```bash
recipe-tool --execute path/to/your/recipe.json context_key=value context_key2=value2
```

Example:

```bash
recipe-tool --execute recipes/example_simple/test_recipe.json model=azure/o3-mini
```

## Creating New Recipes from a Recipe Idea

Create a new recipe using the command line interface:

```bash
recipe-tool --create path/to/your/recipe_idea.txt
```

This will generate a new recipe file based on the provided idea.
You can also pass additional files for context:

```bash
recipe-tool --create path/to/your/recipe_idea.txt files=path/to/other_file.txt,path/to/another_file.txt
```

Example:

```bash
recipe-tool --create recipes/recipe_creator/prompts/sample_recipe_idea.md

# Test it out
recipe-tool --execute output/analyze_codebase.json input=ai_context/generated/recipe_executor_code_files.md,ai_context/generated/recipe_executor_recipe_files.md
```

## Project Structure

The project contains:

- **`recipe_tool.py`**: The main entry point for the command line interface for both recipe execution and creation
- **`recipe_executor/`**: Core implementation with modules for execution, context management, and steps
- **`recipes/`**: Recipe definition files that can be executed

## Building from Recipes

One of the more interesting aspects of this project is that it can _generate its own code using recipes_:

1. To generate the code from scratch:

   ```bash
   make recipe-executor-create
   ```

2. To edit/revise existing code:
   ```bash
   make recipe-executor-edit
   ```

This demonstrates the power of the Recipe Executor for code generation and maintenance tasks.

## Contributing & Development

We have a doc just for that... [dev_guidance.md](docs/dev_guidance.md)


=== File: pyproject.toml ===
[project]
name = "recipe-executor"
version = "0.1.0"
description = "A tool for executing natural language recipe-like instructions"
authors = [{ name = "Brian Krabach" }]
license = "MIT"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "azure-identity>=1.21.0",
    "dotenv>=0.9.9",
    "jsonschema>=4.23.0",
    "pydantic-ai-slim[anthropic,openai,mcp]>=0.1.3",
    "pydantic-settings>=2.8.1",
    "python-code-tools>=0.1.0",
    "python-dotenv>=1.1.0",
    "python-liquid>=2.0.1",
    "pyyaml>=6.0.2",
]

[dependency-groups]
dev = [
    "debugpy>=1.8.14",
    "pyright>=1.1.389",
    "pytest>=8.3.5",
    "pytest-cov>=6.1.1",
    "pytest-mock>=3.14.0",
    "ruff>=0.11.2",
]

[project.scripts]
recipe-executor = "recipe_executor.main:main"
recipe-tool = "recipe_tool:main"
python-code-tools = "python_code_tools.cli:main"

[tool.uv]
package = true

[tool.uv.sources]
python-code-tools = { path = "mcp-servers/python-code-tools", editable = true }

[tool.hatch.build.targets.wheel]
packages = ["recipe_executor"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"


=== File: recipe_executor/context.py ===
from typing import Any, Dict, Iterator, Optional
import copy
import json

from recipe_executor.protocols import ContextProtocol

__all__ = ["Context"]


class Context(ContextProtocol):
    """
    Context is a shared state container for the Recipe Executor system.
    It provides a dictionary-like interface for runtime artifacts and
    holds a separate configuration store.
    """

    def __init__(
        self,
        artifacts: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        # Deep copy initial data to avoid side effects from external modifications
        self._artifacts: Dict[str, Any] = (
            copy.deepcopy(artifacts) if artifacts is not None else {}
        )
        self._config: Dict[str, Any] = (
            copy.deepcopy(config) if config is not None else {}
        )

    def __getitem__(self, key: str) -> Any:
        try:
            return self._artifacts[key]
        except KeyError:
            raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        # Let KeyError propagate naturally if key is missing
        del self._artifacts[key]

    def __contains__(self, key: object) -> bool:
        # Only string keys are valid artifact keys
        return isinstance(key, str) and key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Iterate over a snapshot of keys to prevent issues during mutation
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.
        """
        return self.__iter__()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the value for key if present, otherwise return default.
        """
        return self._artifacts.get(key, default)

    def clone(self) -> ContextProtocol:
        """
        Create a deep copy of this Context, including artifacts and config.
        """
        # __init__ will deep-copy the provided dicts
        return Context(artifacts=self._artifacts, config=self._config)

    def dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts as a standard dict.
        """
        return copy.deepcopy(self._artifacts)

    def json(self) -> str:
        """
        Return a JSON string representation of the artifacts.
        """
        return json.dumps(self.dict())

    def get_config(self) -> Dict[str, Any]:
        """
        Return a deep copy of the configuration store.
        """
        return copy.deepcopy(self._config)

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Replace the configuration store with a deep copy of the provided dict.
        """
        self._config = copy.deepcopy(config)


=== File: recipe_executor/executor.py ===
import os
import logging
import inspect
from pathlib import Path
from typing import Union, Dict, Any

from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
from recipe_executor.models import Recipe
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Concrete implementation of ExecutorProtocol. Loads, validates, and executes
    recipes step by step using a shared context. Stateless between runs.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Load a recipe (from file path, JSON string, dict, or Recipe model),
        validate it, and execute its steps sequentially using the provided context.
        """
        # Load or use provided Recipe model
        if isinstance(recipe, Recipe):
            self.logger.debug("Using provided Recipe model instance.")
            recipe_model = recipe
        else:
            # Path input
            if isinstance(recipe, Path):
                path_str = str(recipe)
                if not recipe.exists():
                    raise ValueError(f"Recipe file not found: {path_str}")
                self.logger.debug(f"Loading recipe from file path: {path_str}")
                try:
                    content = recipe.read_text(encoding="utf-8")
                except Exception as e:
                    raise ValueError(f"Failed to read recipe file {path_str}: {e}") from e
                try:
                    recipe_model = Recipe.model_validate_json(content)
                except Exception as e:
                    raise ValueError(f"Failed to parse recipe JSON from file {path_str}: {e}") from e
            # String input: file path or JSON
            elif isinstance(recipe, str):
                if os.path.isfile(recipe):
                    self.logger.debug(f"Loading recipe from file path: {recipe}")
                    try:
                        content = Path(recipe).read_text(encoding="utf-8")
                    except Exception as e:
                        raise ValueError(f"Failed to read recipe file {recipe}: {e}") from e
                    try:
                        recipe_model = Recipe.model_validate_json(content)
                    except Exception as e:
                        raise ValueError(f"Failed to parse recipe JSON from file {recipe}: {e}") from e
                else:
                    self.logger.debug("Loading recipe from JSON string.")
                    try:
                        recipe_model = Recipe.model_validate_json(recipe)
                    except Exception as e:
                        raise ValueError(f"Failed to parse recipe JSON string: {e}") from e
            # Dict input
            elif isinstance(recipe, dict):
                self.logger.debug("Loading recipe from dict.")
                try:
                    recipe_model = Recipe.model_validate(recipe)
                except Exception as e:
                    raise ValueError(f"Invalid recipe structure: {e}") from e
            else:
                raise TypeError(f"Unsupported recipe type: {type(recipe)}")

        # Log recipe summary
        try:
            summary = recipe_model.model_dump()
        except Exception:
            summary = {}
        step_count = len(getattr(recipe_model, 'steps', []))
        self.logger.debug(f"Recipe loaded: {summary}. Steps count: {step_count}")

        # Execute each step sequentially
        for idx, step in enumerate(recipe_model.steps):  # type: ignore
            step_type = step.type
            config = step.config or {}
            self.logger.debug(
                f"Executing step {idx} of type '{step_type}' with config: {config}"
            )

            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}")

            step_cls = STEP_REGISTRY[step_type]
            step_instance = step_cls(self.logger, config)

            try:
                result = step_instance.execute(context)
                if inspect.isawaitable(result):  # type: ignore
                    await result
            except Exception as e:
                msg = f"Error executing step {idx} ('{step_type}'): {e}"
                raise ValueError(msg) from e

            self.logger.debug(f"Step {idx} ('{step_type}') completed successfully.")

        self.logger.debug("All recipe steps completed successfully.")


=== File: recipe_executor/llm_utils/azure_openai.py ===
import os
import logging
from typing import Optional

from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel


def _mask_secret(secret: Optional[str]) -> str:
    """
    Mask a secret, showing only the first and last character.
    """
    if not secret:
        return "<None>"
    if len(secret) <= 2:
        return "**"
    return f"{secret[0]}***{secret[-1]}"


def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str] = None,
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance for Azure OpenAI.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name (str): Model name, such as "gpt-4o" or "o3-mini".
        deployment_name (Optional[str]): Azure deployment name; defaults to model_name.

    Returns:
        OpenAIModel: Configured PydanticAI OpenAIModel instance.

    Raises:
        Exception: If required environment variables are missing or client creation fails.
    """
    # Load configuration from environment
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("1", "true", "yes")
    azure_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    env_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_client_id = os.getenv("AZURE_CLIENT_ID")

    if not azure_endpoint:
        logger.error("Environment variable AZURE_OPENAI_BASE_URL is required")
        raise Exception("Missing AZURE_OPENAI_BASE_URL")

    # Determine deployment identifier
    deployment = deployment_name or env_deployment or model_name

    # Log loaded configuration (mask secrets)
    logger.debug(
        f"Azure OpenAI config: endpoint={azure_endpoint}, api_version={azure_api_version}, "
        f"deployment={deployment}, use_managed_identity={use_managed_identity}, "
        f"client_id={azure_client_id or '<None>'}, "
        f"api_key={_mask_secret(os.getenv('AZURE_OPENAI_API_KEY'))}"
    )

    # Create Azure OpenAI client
    try:
        if use_managed_identity:
            logger.info("Using Azure Managed Identity for authentication")
            if azure_client_id:
                credential = ManagedIdentityCredential(client_id=azure_client_id)
            else:
                credential = DefaultAzureCredential()

            token_provider = get_bearer_token_provider(
                credential,
                "https://cognitiveservices.azure.com/.default"
            )
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment,
            )
            auth_method = "Azure Managed Identity"
        else:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                logger.error("Environment variable AZURE_OPENAI_API_KEY is required for API key authentication")
                raise Exception("Missing AZURE_OPENAI_API_KEY")
            logger.info("Using API key authentication for Azure OpenAI")
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment,
            )
            auth_method = "API Key"
    except Exception as error:
        logger.error(f"Failed to create AsyncAzureOpenAI client: {error}")
        raise

    # Wrap client in PydanticAI provider and model
    logger.info(f"Creating Azure OpenAI model '{model_name}' with {auth_method}")
    provider = OpenAIProvider(openai_client=azure_client)
    try:
        model = OpenAIModel(model_name=model_name, provider=provider)
    except Exception as error:
        logger.error(f"Failed to create OpenAIModel: {error}")
        raise

    return model


=== File: recipe_executor/llm_utils/llm.py ===
import logging
import os
import time
from typing import List, Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServer
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model

__all__ = ["LLM"]

# env var for default model
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def _get_model(logger: logging.Logger, model_id: Optional[str]) -> Union[OpenAIModel, AnthropicModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    """
    if not model_id:
        model_id = DEFAULT_MODEL
    parts = model_id.split("/", 2)
    if len(parts) < 2:
        raise ValueError(f"Invalid model identifier '{model_id}', expected 'provider/model_name'")
    provider = parts[0].lower()
    model_name = parts[1]
    # azure may include a deployment name
    if provider == "azure":
        deployment_name: Optional[str] = parts[2] if len(parts) == 3 else None
        try:
            return get_azure_openai_model(
                logger=logger,
                model_name=model_name,
                deployment_name=deployment_name,
            )
        except Exception:
            logger.error(f"Failed to initialize Azure OpenAI model '{model_id}'", exc_info=True)
            raise
    if provider == "openai":
        # OpenAIModel will pick up OPENAI_API_KEY from env
        return OpenAIModel(model_name)
    if provider == "anthropic":
        return AnthropicModel(model_name)
    if provider == "ollama":
        # Ollama endpoint via OpenAIProvider
        base_url = OLLAMA_BASE_URL.rstrip("/") + "/v1"
        provider_client = OpenAIProvider(base_url=base_url)
        return OpenAIModel(model_name, provider=provider_client)
    raise ValueError(f"Unsupported LLM provider '{provider}' in model identifier '{model_id}'")


class LLM:
    """
    Unified interface for interacting with LLM providers and optional MCP servers.
    """

    def __init__(
        self,
        logger: logging.Logger,
        model: str = DEFAULT_MODEL,
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        self.logger: logging.Logger = logger
        self.model: str = model
        # store list or empty list
        self.mcp_servers: List[MCPServer] = mcp_servers if mcp_servers is not None else []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        # Determine model identifier and servers
        model_id = model or self.model
        servers = mcp_servers if mcp_servers is not None else self.mcp_servers

        # Initialize model
        try:
            llm_model = _get_model(self.logger, model_id)
        except Exception:
            raise

        model_name = getattr(llm_model, "model_name", str(llm_model))

        # Create agent
        agent = Agent(
            model=llm_model,
            output_type=output_type,
            mcp_servers=servers or [],
        )
        # Logging before call
        self.logger.info(f"LLM request: model={model_name}")
        self.logger.debug(f"LLM request payload: prompt={prompt!r}, output_type={output_type}, mcp_servers={servers}")

        start_time = time.monotonic()
        try:
            # open MCP sessions if any
            async with agent.run_mcp_servers():
                result = await agent.run(prompt)
        except Exception:
            self.logger.error(f"LLM call failed for model {model_id}", exc_info=True)
            raise
        end_time = time.monotonic()

        # Logging after call
        duration = end_time - start_time
        usage = None
        try:
            usage = result.usage()
        except Exception:
            pass
        # debug full result
        self.logger.debug(f"LLM result payload: {result!r}")
        # info summary
        if usage:
            tokens = f"total={usage.total_tokens}, request={usage.request_tokens}, response={usage.response_tokens}"
        else:
            tokens = "unknown"
        self.logger.info(f"LLM completed in {duration:.2f}s, tokens used: {tokens}")

        # Return only the output
        return result.output


=== File: recipe_executor/llm_utils/mcp.py ===
"""
Minimal MCP utility for creating MCPServer instances from configurations.
"""
import logging
from typing import Any, Dict, List, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

# Keys considered sensitive for masking
_SENSITIVE_KEYS = ("key", "secret", "token", "password")

def _mask_value(value: Any, key: Optional[str] = None) -> Any:
    """
    Mask sensitive values in a configuration dictionary.
    """
    # Mask entire value if key indicates sensitive data
    if key and any(sensitive in key.lower() for sensitive in _SENSITIVE_KEYS):
        return "***"
    # Recurse into dicts
    if isinstance(value, dict):
        return {k: _mask_value(v, k) for k, v in value.items()}
    return value


def get_mcp_server(
    logger: logging.Logger,
    config: Dict[str, Any]
) -> MCPServer:
    """
    Create an MCPServer instance based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCPServer instance.

    Raises:
        ValueError: If configuration is invalid.
        RuntimeError: If instantiation of the server fails.
    """
    # Mask and log configuration for debugging
    try:
        masked = _mask_value(config)  # type: ignore
        logger.debug("MCP configuration: %s", masked)
    except Exception:
        logger.debug("MCP configuration contains non-serializable values")

    # HTTP transport configuration
    if "url" in config:
        url = config.get("url")
        if not isinstance(url, str):
            raise ValueError("MCP HTTP configuration requires a string 'url'")
        headers = config.get("headers")
        if headers is not None:
            if not isinstance(headers, dict) or not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in headers.items()
            ):
                raise ValueError("MCP HTTP 'headers' must be a dict of string keys and values")
        logger.info("Configuring MCPServerHTTP for URL: %s", url)
        try:
            # Only pass headers if provided
            if headers is not None:
                return MCPServerHTTP(url=url, headers=headers)
            return MCPServerHTTP(url=url)
        except Exception as error:
            msg = f"Failed to create HTTP MCP server for {url}: {error}"
            logger.error(msg)
            raise RuntimeError(msg) from error

    # Stdio transport configuration
    if "command" in config:
        command = config.get("command")
        if not isinstance(command, str):
            raise ValueError("MCP stdio configuration requires a string 'command'")
        args_value = config.get("args")
        if args_value is None:
            args_list: List[str] = []
        else:
            if not isinstance(args_value, list) or not all(isinstance(a, str) for a in args_value):
                raise ValueError("MCP stdio 'args' must be a list of strings")
            args_list = args_value  # type: List[str]
        logger.info(
            "Configuring MCPServerStdio with command: %s args: %s",
            command,
            args_list,
        )
        try:
            return MCPServerStdio(command=command, args=args_list)
        except Exception as error:
            msg = f"Failed to create stdio MCP server for command {command}: {error}"
            logger.error(msg)
            raise RuntimeError(msg) from error

    # If neither HTTP nor stdio config is present
    raise ValueError(
        "Invalid MCP server configuration: provide either 'url' for HTTP or 'command' for stdio"
    )


=== File: recipe_executor/logger.py ===
import os
import sys
import logging
from typing import Any

def init_logger(
    log_dir: str = "logs", stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR" (case-insensitive).

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    # Get root logger and set lowest level
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Create log directory
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as exc:
        raise Exception(f"Failed to create log directory '{log_dir}': {exc}")

    # Define formatter for all handlers
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set up file handlers: debug.log, info.log, error.log
    level_map = [
        ("debug", logging.DEBUG),
        ("info", logging.INFO),
        ("error", logging.ERROR),
    ]
    for name, level in level_map:
        path = os.path.join(log_dir, f"{name}.log")
        try:
            file_handler = logging.FileHandler(path, mode="w", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as exc:
            raise Exception(f"Failed to set up {name} log file '{path}': {exc}")

    # Configure console (stdout) handler
    level_name = stdio_log_level.upper()
    if level_name == "WARN":
        level_name = "WARNING"
    if level_name not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        level_name = "INFO"
    console_level: Any = getattr(logging, level_name, logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Initialization logs
    logger.debug("Logger initialized: log_dir='%s', stdio_log_level='%s'", log_dir, level_name)
    logger.info("Logger initialized successfully")

    return logger


=== File: recipe_executor/main.py ===
import argparse
import asyncio
import logging
import os
import sys
import time
import traceback
from typing import Dict, List

from dotenv import load_dotenv

from .context import Context
from .executor import Executor
from .logger import init_logger


def parse_key_value_pairs(pairs: List[str]) -> Dict[str, str]:
    """
    Parse a list of strings in the form key=value into a dictionary.
    Raises ValueError on malformed entries.
    """
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid key=value format '{pair}'")
        key, value = pair.split("=", 1)
        if not key:
            raise ValueError(f"Invalid key in pair '{pair}'")
        result[key] = value
    return result


async def main_async() -> None:
    # Load environment variables from .env
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Recipe Executor CLI")
    parser.add_argument(
        "recipe_path",
        type=str,
        help="Path to the recipe file to execute"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for log files"
    )
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Context artifact values as key=value pairs"
    )
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        help="Static configuration values as key=value pairs"
    )
    args = parser.parse_args()

    # Ensure log directory exists
    try:
        os.makedirs(args.log_dir, exist_ok=True)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: cannot create log directory '{args.log_dir}': {e}\n")
        raise SystemExit(1)

    # Initialize logging
    try:
        logger: logging.Logger = init_logger(args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: {e}\n")
        raise SystemExit(1)

    logger.debug("Starting Recipe Executor Tool")
    logger.debug("Parsed arguments: %s", args)

    # Parse context and config key=value pairs
    try:
        artifacts = parse_key_value_pairs(args.context)
        config = parse_key_value_pairs(args.config)
    except ValueError as ve:
        # Invalid context/config formatting
        raise ve

    logger.debug("Initial context artifacts: %s", artifacts)

    # Create execution context
    context = Context(artifacts=artifacts, config=config)

    # Create and run executor
    executor = Executor(logger)
    logger.info("Executing recipe: %s", args.recipe_path)

    start_time = time.time()
    try:
        await executor.execute(args.recipe_path, context)
    except Exception as exec_err:
        logger.error(
            "An error occurred during recipe execution: %s", exec_err,
            exc_info=True
        )
        raise
    duration = time.time() - start_time

    logger.info(
        "Recipe execution completed successfully in %.2f seconds",
        duration
    )


def main() -> None:
    try:
        asyncio.run(main_async())
    except ValueError as ve:
        sys.stderr.write(f"Context Error: {ve}\n")
        sys.exit(1)
    except SystemExit as se:
        # Preserve explicit exit codes
        sys.exit(se.code)
    except Exception:
        # Unexpected errors: print traceback
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()


=== File: recipe_executor/models.py ===
"""
Models for Recipe Executor system.

Defines Pydantic models for file specifications and recipe structures.
"""
from typing import Any, Dict, List, Union

from pydantic import BaseModel


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file, which can be a string,
                 a mapping, or a list of mappings for structured outputs.
    """
    path: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """
    type: str
    config: Dict[str, Any]


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps: A list of steps defining the recipe.
    """
    steps: List[RecipeStep]

=== File: recipe_executor/protocols.py ===
"""
Protocols definitions for the Recipe Executor system.

This module provides structural interfaces (Protocols) for core components:
- ContextProtocol
- StepProtocol
- ExecutorProtocol

These serve as the single source of truth for component contracts, enabling loose coupling
and clear type annotations without introducing direct dependencies on concrete implementations.
"""
from typing import Protocol, runtime_checkable, Any, Dict, Iterator, Union
from pathlib import Path
from logging import Logger

from recipe_executor.models import Recipe


@runtime_checkable
class ContextProtocol(Protocol):
    """
    Defines a dict-like context for sharing data across steps and executors.

    Methods mirror built-in dict behaviors plus cloning and serialization.
    """

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __contains__(self, key: str) -> bool:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def clone(self) -> "ContextProtocol":
        ...

    def dict(self) -> Dict[str, Any]:
        ...

    def json(self) -> str:
        ...

    def keys(self) -> Iterator[str]:
        ...

    def get_config(self) -> Dict[str, Any]:
        ...

    def set_config(self, config: Dict[str, Any]) -> None:
        ...


@runtime_checkable
class StepProtocol(Protocol):
    """
    Defines the interface for a recipe step implementation.

    Each step is initialized with a logger and configuration, and
    exposes an asynchronous execute method.
    """

    def __init__(self, logger: Logger, config: Dict[str, Any]) -> None:
        ...

    async def execute(self, context: ContextProtocol) -> None:
        ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    """
    Defines the interface for an executor implementation.

    The executor runs a recipe given its definition and a context.
    """

    def __init__(self, logger: Logger) -> None:
        ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None:
        ...


=== File: recipe_executor/steps/__init__.py ===
"""
Package-level imports and registration for standard recipe steps.
"""

__all__ = [
    "STEP_REGISTRY",
    "ConditionalStep",
    "ExecuteRecipeStep",
    "LLMGenerateStep",
    "LoopStep",
    "MCPStep",
    "ParallelStep",
    "ReadFilesStep",
    "WriteFilesStep",
]

from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.conditional import ConditionalStep
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.llm_generate import LLMGenerateStep
from recipe_executor.steps.loop import LoopStep
from recipe_executor.steps.mcp import MCPStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register standard steps by updating the global registry
STEP_REGISTRY.update({
    "conditional": ConditionalStep,
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": MCPStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})


=== File: recipe_executor/steps/base.py ===
"""
Base step component for the Recipe Executor.
Defines a generic BaseStep class and the base Pydantic StepConfig.
"""

from __future__ import annotations

import logging
from typing import Generic, TypeVar

from pydantic import BaseModel

from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for steps.
    Extend this class to add step-specific fields.
    """

    # No common fields; each step should subclass and define its own
    pass


StepConfigType = TypeVar("StepConfigType", bound=StepConfig)


class BaseStep(Generic[StepConfigType]):
    """
    Base class for all steps in the recipe executor.

    Each step must implement the async execute method.
    Subclasses should call super().__init__ in their constructor,
    passing a logger and an instance of a StepConfig subclass.
    """

    def __init__(self, logger: logging.Logger, config: StepConfigType) -> None:
        """
        Initialize a step with a logger and validated configuration.

        Args:
            logger: Logger instance for the step.
            config: Pydantic-validated configuration for the step.
        """
        self.logger: logging.Logger = logger
        self.config: StepConfigType = config
        # Log initialization with debug-level detail
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config!r}")

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step logic. Must be overridden by subclasses.

        Args:
            context: Execution context adhering to ContextProtocol.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement the execute method")


=== File: recipe_executor/steps/conditional.py ===
import logging
import os
import re
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.utils.templates import render_template


class ConditionalConfig(StepConfig):
    """
    Configuration for ConditionalStep.

    Fields:
        condition: Expression string to evaluate against the context.
        if_true: Optional steps to execute when the condition evaluates to true.
        if_false: Optional steps to execute when the condition evaluates to false.
    """

    condition: str
    if_true: Optional[Dict[str, Any]] = None
    if_false: Optional[Dict[str, Any]] = None


# Utility functions for condition evaluation


def file_exists(path: Any) -> bool:
    """Check if a given path exists on the filesystem."""
    try:
        return isinstance(path, str) and os.path.exists(path)
    except Exception:
        return False


def all_files_exist(paths: Any) -> bool:
    """Check if all paths in a list or tuple exist."""
    try:
        if not isinstance(paths, (list, tuple)):
            return False
        return all(isinstance(p, str) and os.path.exists(p) for p in paths)
    except Exception:
        return False


def file_is_newer(src: Any, dst: Any) -> bool:
    """Check if src file is newer than dst file."""
    try:
        if not (isinstance(src, str) and isinstance(dst, str)):
            return False
        if not (os.path.exists(src) and os.path.exists(dst)):
            return False
        return os.path.getmtime(src) > os.path.getmtime(dst)
    except Exception:
        return False


def and_(*args: Any) -> bool:
    """Logical AND over all arguments."""
    return all(bool(a) for a in args)


def or_(*args: Any) -> bool:
    """Logical OR over all arguments."""
    return any(bool(a) for a in args)


def not_(val: Any) -> bool:
    """Logical NOT of the value."""
    return not bool(val)


def evaluate_condition(expr: str, context: ContextProtocol, logger: logging.Logger) -> bool:
    """
    Render and evaluate a condition expression against the context.
    Supports file checks, comparisons, and function-like logical operations.
    Raises ValueError on render or eval errors.
    """
    try:
        rendered = render_template(expr, context)
    except Exception as err:
        raise ValueError(f"Error rendering condition '{expr}': {err}")

    logger.debug(f"Rendered condition '{expr}': '{rendered}'")
    trimmed = rendered.strip()
    lowered = trimmed.lower()

    # Direct boolean literal
    if lowered in ("true", "false"):
        result = lowered == "true"
        logger.debug(f"Interpreted boolean literal '{trimmed}' as {result}")
        return result

    # Replace logical function names to avoid Python keyword conflicts
    expr_transformed = re.sub(r"\band\(", "and_(", trimmed)
    expr_transformed = re.sub(r"\bor\(", "or_(", expr_transformed)
    expr_transformed = re.sub(r"\bnot\(", "not_(", expr_transformed)
    logger.debug(f"Transformed expression for eval: '{expr_transformed}'")

    safe_globals: Dict[str, Any] = {
        "__builtins__": {},
        # file utilities
        "file_exists": file_exists,
        "all_files_exist": all_files_exist,
        "file_is_newer": file_is_newer,
        # logical helpers
        "and_": and_,
        "or_": or_,
        "not_": not_,
        # boolean literals
        "true": True,
        "false": False,
    }

    try:
        eval_result = eval(expr_transformed, safe_globals, {})  # noqa: P204
    except Exception as err:
        raise ValueError(f"Invalid condition expression '{expr_transformed}': {err}")

    result_bool = bool(eval_result)
    logger.debug(f"Condition '{expr_transformed}' evaluated to {result_bool}")
    return result_bool


class ConditionalStep(BaseStep[ConditionalConfig]):
    """
    Step that branches execution based on a boolean condition.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ConditionalConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        expr = self.config.condition
        self.logger.debug(f"Evaluating conditional expression: '{expr}'")
        try:
            result = evaluate_condition(expr, context, self.logger)
        except ValueError as err:
            raise RuntimeError(f"Condition evaluation error: {err}")

        if result:
            self.logger.debug(f"Condition '{expr}' is True, executing 'if_true' branch")
            branch = self.config.if_true
        else:
            self.logger.debug(f"Condition '{expr}' is False, executing 'if_false' branch")
            branch = self.config.if_false

        if branch and isinstance(branch, dict):
            await self._execute_branch(branch, context)
        else:
            self.logger.debug("No branch to execute for this condition result")

    async def _execute_branch(self, branch: Dict[str, Any], context: ContextProtocol) -> None:
        steps: List[Any] = branch.get("steps", []) or []
        if not isinstance(steps, list):
            self.logger.debug("Branch 'steps' is not a list, skipping execution")
            return

        for step_def in steps:
            if not isinstance(step_def, dict):
                continue

            step_type = step_def.get("type")
            step_conf = step_def.get("config", {}) or {}
            if not step_type:
                self.logger.debug("Step definition missing 'type', skipping")
                continue

            step_cls = STEP_REGISTRY.get(step_type)
            if not step_cls:
                raise RuntimeError(f"Unknown step type in conditional branch: {step_type}")

            self.logger.debug(f"Executing step '{step_type}' in conditional branch")
            step = step_cls(self.logger, step_conf)
            await step.execute(context)


# Register this step in the global registry
STEP_REGISTRY["conditional"] = ConditionalStep


=== File: recipe_executor/steps/execute_recipe.py ===
import os
import logging
from typing import Any, Dict

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """
    recipe_path: str
    context_overrides: Dict[str, str] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    """Step to execute a sub-recipe with shared context and optional overrides."""

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ExecuteRecipeConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render the recipe path template
        rendered_path: str = render_template(self.config.recipe_path, context)

        # Validate that the sub-recipe file exists
        if not os.path.isfile(rendered_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {rendered_path}")

        # Apply context overrides before execution
        for key, template_value in self.config.context_overrides.items():
            rendered_value: str = render_template(template_value, context)
            context[key] = rendered_value

        # Execute the sub-recipe
        try:
            # Import here to avoid circular dependencies
            from recipe_executor.executor import Executor

            self.logger.info(f"Starting sub-recipe execution: {rendered_path}")
            executor = Executor(self.logger)
            await executor.execute(rendered_path, context)
            self.logger.info(f"Completed sub-recipe execution: {rendered_path}")
        except Exception as e:
            # Log and propagate with context
            self.logger.error(f"Error executing sub-recipe '{rendered_path}': {e}")
            raise RuntimeError(f"Failed to execute sub-recipe '{rendered_path}': {e}") from e


=== File: recipe_executor/steps/llm_generate.py ===
import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.models import json_object_to_pydantic_model
from recipe_executor.utils.templates import render_template


class LLMGenerateConfig(StepConfig):
    """
    Config for LLMGenerateStep.
    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        mcp_servers: List of MCP servers for access to tools.
        output_format: The format of the LLM output (text, files, or JSON/object/list schemas).
        output_key: The name under which to store the LLM output in context.
    """

    prompt: str
    model: str = "openai/gpt-4o"
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any], List[Any]]
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):
    files: List[FileSpec]


def render_template_config(config: Dict[str, Any], context: ContextProtocol) -> Dict[str, Any]:
    rendered: Dict[str, Any] = {}
    for k, v in config.items():
        if isinstance(v, str):
            rendered[k] = render_template(v, context)
        elif isinstance(v, dict):
            rendered[k] = render_template_config(v, context)
        elif isinstance(v, list):
            rendered[k] = [render_template_config(i, context) if isinstance(i, dict) else i for i in v]
        else:
            rendered[k] = v
    return rendered


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        prompt: str = render_template(self.config.prompt, context)
        model_id: str = render_template(self.config.model, context) if self.config.model else "openai/gpt-4o"
        output_key: str = render_template(self.config.output_key, context)

        # Collect MCP server configs from config and context
        mcp_servers_configs: List[Dict[str, Any]] = []
        if self.config.mcp_servers:
            mcp_servers_configs.extend(self.config.mcp_servers)
        context_mcp_servers_cfg = context.get_config().get("mcp_servers", [])
        if context_mcp_servers_cfg:
            mcp_servers_configs.extend(context_mcp_servers_cfg)
        mcp_servers: Optional[List[Any]] = None
        if mcp_servers_configs:
            mcp_servers = [
                get_mcp_server(logger=self.logger, config=render_template_config(cfg, context))
                for cfg in mcp_servers_configs
            ]

        llm = LLM(logger=self.logger, model=model_id, mcp_servers=mcp_servers)
        output_format = self.config.output_format
        result: Any = None
        try:
            self.logger.debug(
                "Calling LLM: model=%s, output_format=%r, mcp_servers=%r", model_id, output_format, mcp_servers
            )
            if output_format == "text":
                result = await llm.generate(prompt, output_type=str)
                context[output_key] = result
            elif output_format == "files":
                result = await llm.generate(prompt, output_type=FileSpecCollection)
                context[output_key] = result.files
            elif isinstance(output_format, dict) and output_format.get("type") == "object":
                schema_model = json_object_to_pydantic_model(output_format, model_name="LLMObject")
                result = await llm.generate(prompt, output_type=schema_model)
                context[output_key] = result.model_dump()
            elif isinstance(output_format, list):
                if len(output_format) != 1 or not isinstance(output_format[0], dict):
                    raise ValueError(
                        "When output_format is a list, it must be a single-item list containing a valid schema object."
                    )
                item_schema = output_format[0]
                object_schema = {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": item_schema}},
                    "required": ["items"],
                }
                schema_model = json_object_to_pydantic_model(object_schema, model_name="LLMListWrapper")
                result = await llm.generate(prompt, output_type=schema_model)
                items = result.model_dump()["items"]
                context[output_key] = items
            else:
                raise ValueError(f"Unsupported output_format: {output_format!r}")
        except Exception as e:
            self.logger.error("LLM generate failed: %r", e, exc_info=True)
            raise


=== File: recipe_executor/steps/loop.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template

__all__ = ["LoopStep", "LoopStepConfig"]


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.
    """
    items: str
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    """
    LoopStep: iterate over a collection, execute substeps per item.
    """
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # dynamic import to avoid circular dependencies
        from recipe_executor.executor import Executor  # type: ignore

        # resolve items path
        items_path: str = render_template(self.config.items, context)
        items_obj: Any = _resolve_path(items_path, context)

        if items_obj is None:
            raise ValueError(f"LoopStep: Items collection '{items_path}' not found in context.")
        if not isinstance(items_obj, (list, dict)):
            raise ValueError(
                f"LoopStep: Items collection '{items_path}' must be a list or dict, got {type(items_obj).__name__}"
            )

        # build list of (key/index, value)
        items_list: List[Tuple[Any, Any]] = []
        if isinstance(items_obj, list):
            for idx, value in enumerate(items_obj):
                items_list.append((idx, value))
        else:
            for key, value in items_obj.items():
                items_list.append((key, value))
        total_items: int = len(items_list)

        self.logger.info(
            f"LoopStep: Processing {total_items} items with max_concurrency={self.config.max_concurrency}."
        )

        # handle empty collection
        if total_items == 0:
            empty: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
            context[self.config.result_key] = empty
            self.logger.info("LoopStep: No items to process.")
            return

        # prepare result and error containers
        results: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
        errors: Union[List[Dict[str, Any]], Dict[Any, Dict[str, Any]]] = [] if isinstance(items_obj, list) else {}

        # concurrency control
        semaphore: Optional[asyncio.Semaphore] = None
        if self.config.max_concurrency and self.config.max_concurrency > 0:
            semaphore = asyncio.Semaphore(self.config.max_concurrency)

        # executor for substeps
        step_executor: ExecutorProtocol = Executor(self.logger)
        substeps_recipe: Dict[str, Any] = {"steps": self.config.substeps}

        fail_fast_triggered: bool = False
        tasks: List[asyncio.Task] = []
        completed_count: int = 0

        async def process_single_item(idx_or_key: Any, item: Any) -> Tuple[Any, Any, Optional[str]]:
            # isolate context
            item_context: ContextProtocol = context.clone()
            item_context[self.config.item_key] = item
            # index or key in context
            if isinstance(items_obj, list):
                item_context["__index"] = idx_or_key
            else:
                item_context["__key"] = idx_or_key
            try:
                self.logger.debug(f"LoopStep: Starting item {idx_or_key}.")
                await step_executor.execute(substeps_recipe, item_context)
                # extract result
                result = item_context.get(self.config.item_key, item)
                self.logger.debug(f"LoopStep: Finished item {idx_or_key}.")
                return idx_or_key, result, None
            except Exception as exc:
                self.logger.error(f"LoopStep: Error processing item {idx_or_key}: {exc}")
                return idx_or_key, None, str(exc)

        async def run_sequential() -> None:
            nonlocal fail_fast_triggered, completed_count
            for idx_or_key, item in items_list:
                if fail_fast_triggered:
                    break
                idx, res, err = await process_single_item(idx_or_key, item)
                if err:
                    # record error
                    if isinstance(errors, list):
                        errors.append({"index": idx, "error": err})
                    else:
                        errors[idx] = {"error": err}
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break
                else:
                    # record success
                    if isinstance(results, list):
                        results.append(res)
                    else:
                        results[idx] = res
                completed_count += 1

        async def run_parallel() -> None:
            nonlocal fail_fast_triggered, completed_count

            async def worker(key: Any, value: Any) -> Tuple[Any, Any, Optional[str]]:
                if semaphore is not None:
                    async with semaphore:
                        return await process_single_item(key, value)
                return await process_single_item(key, value)

            # launch tasks
            for idx, (key, value) in enumerate(items_list):
                if fail_fast_triggered:
                    break
                task = asyncio.create_task(worker(key, value))
                tasks.append(task)
                if self.config.delay and self.config.delay > 0 and idx < total_items - 1:
                    await asyncio.sleep(self.config.delay)
            # collect results
            for fut in asyncio.as_completed(tasks):
                if fail_fast_triggered:
                    break
                try:
                    idx, res, err = await fut
                    if err:
                        if isinstance(errors, list):
                            errors.append({"index": idx, "error": err})
                        else:
                            errors[idx] = {"error": err}
                        if self.config.fail_fast:
                            fail_fast_triggered = True
                            continue
                    else:
                        if isinstance(results, list):
                            results.append(res)
                        else:
                            results[idx] = res
                    completed_count += 1
                except Exception as exc:
                    self.logger.error(f"LoopStep: Unexpected exception: {exc}")
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        continue

        # choose execution mode
        if self.config.max_concurrency == 1:
            await run_sequential()
        else:
            await run_parallel()

        # store results
        context[self.config.result_key] = results
        # store errors if any
        has_errors = (isinstance(errors, list) and bool(errors)) or (isinstance(errors, dict) and bool(errors))
        if has_errors:
            context[f"{self.config.result_key}__errors"] = errors
        self.logger.info(
            f"LoopStep: Processed {completed_count} items. Errors: {len(errors) if has_errors else 0}."
        )


def _resolve_path(path: str, context: ContextProtocol) -> Any:
    """
    Resolve a dot-notated path against the context or nested dicts.
    """
    current: Any = context
    for part in path.split('.'):
        if isinstance(current, ContextProtocol):
            current = current.get(part, None)
        elif isinstance(current, dict):
            current = current.get(part, None)
        else:
            return None
        if current is None:
            return None
    return current


=== File: recipe_executor/steps/mcp.py ===
"""
MCPStep component for invoking tools on remote MCP servers and storing results in context.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult

from recipe_executor.steps.base import BaseStep, ContextProtocol, StepConfig
from recipe_executor.utils.templates import render_template


class MCPConfig(StepConfig):
    """
    Configuration for MCPStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key under which to store the tool result as a dictionary.
    """

    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = "tool_result"


class MCPStep(BaseStep[MCPConfig]):
    """
    Step that connects to an MCP server, invokes a tool, and stores the result in the context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, MCPConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render tool name
        tool_name: str = render_template(self.config.tool_name, context)

        # Render arguments
        raw_args: Dict[str, Any] = self.config.arguments or {}
        arguments: Dict[str, Any] = {}
        for key, value in raw_args.items():
            if isinstance(value, str):
                arguments[key] = render_template(value, context)
            else:
                arguments[key] = value

        # Prepare server config
        server_conf: Dict[str, Any] = self.config.server
        client_cm: Any
        service_desc: str

        # Choose transport
        if "command" in server_conf:
            # stdio transport
            cmd: str = render_template(server_conf.get("command", ""), context)
            args_list: List[str] = []
            for arg in server_conf.get("args", []):
                if isinstance(arg, str):
                    args_list.append(render_template(arg, context))
                else:
                    args_list.append(str(arg))

            env_conf: Optional[Dict[str, str]] = None
            if server_conf.get("env") is not None:
                env_conf = {}
                for k, v in server_conf.get("env", {}).items():
                    if isinstance(v, str):
                        env_conf[k] = render_template(v, context)
                    else:
                        env_conf[k] = str(v)

            cwd: Optional[str] = None
            if server_conf.get("working_dir") is not None:
                cwd = render_template(server_conf.get("working_dir", ""), context)

            server_params = StdioServerParameters(
                command=cmd,
                args=args_list,
                env=env_conf,
                cwd=cwd,
            )
            client_cm = stdio_client(server_params)
            service_desc = f"stdio command '{cmd}'"
        else:
            # SSE transport
            url: str = render_template(server_conf.get("url", ""), context)
            headers_conf: Optional[Dict[str, Any]] = None
            if server_conf.get("headers") is not None:
                headers_conf = {}
                for k, v in server_conf.get("headers", {}).items():
                    if isinstance(v, str):
                        headers_conf[k] = render_template(v, context)
                    else:
                        headers_conf[k] = v

            client_cm = sse_client(url, headers=headers_conf)
            service_desc = f"SSE server '{url}'"

        # Connect and invoke tool
        self.logger.debug(f"Connecting to MCP server: {service_desc}")
        try:
            async with client_cm as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    self.logger.debug(f"Invoking tool '{tool_name}' with arguments {arguments}")
                    try:
                        result: CallToolResult = await session.call_tool(
                            name=tool_name,
                            arguments=arguments,
                        )
                    except Exception as e:
                        msg = (
                            f"Tool invocation failed for '{tool_name}' "
                            f"on {service_desc}: {e}"
                        )
                        raise ValueError(msg) from e
        except ValueError:
            # Propagate invocation errors
            raise
        except Exception as e:
            msg = f"Failed to call tool '{tool_name}' on {service_desc}: {e}"
            raise ValueError(msg) from e

        # Convert result to dictionary
        try:
            result_dict: Dict[str, Any] = result.__dict__  # type: ignore
        except Exception:
            result_dict = {
                attr: getattr(result, attr)
                for attr in dir(result)
                if not attr.startswith("_")
            }

        # Store in context
        context[self.config.result_key] = result_dict


=== File: recipe_executor/steps/parallel.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.protocols import ContextProtocol, StepProtocol


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step definitions, each a dict with 'type' and 'config'.
        max_concurrency: Maximum number of substeps to run concurrently. 0 means unlimited.
        delay: Optional delay (in seconds) between launching each substep.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """Step to execute multiple sub-steps in parallel."""

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        substeps: List[Dict[str, Any]] = self.config.substeps or []
        total: int = len(substeps)
        max_conc: int = self.config.max_concurrency
        delay: float = self.config.delay

        self.logger.info(
            f"Starting ParallelStep: {total} substeps, "
            f"max_concurrency={max_conc}, delay={delay}"
        )

        if total == 0:
            self.logger.info("ParallelStep has no substeps to execute. Skipping.")
            return

        # Determine concurrency limit
        concurrency: int = max_conc if max_conc > 0 else total
        semaphore: asyncio.Semaphore = asyncio.Semaphore(concurrency)

        # Holder for first failure
        failure: Dict[str, Optional[Any]] = {"exc": None, "idx": None}
        tasks: List[asyncio.Task] = []

        async def run_substep(idx: int, spec: Dict[str, Any]) -> None:
            sub_logger = self.logger.getChild(f"substep_{idx}")
            try:
                sub_logger.debug(
                    f"Cloning context and preparing substep {idx} ({spec.get('type')})"
                )
                sub_context = context.clone()

                step_type = spec.get("type")
                step_cfg = spec.get("config", {})
                if not step_type or step_type not in STEP_REGISTRY:
                    raise RuntimeError(
                        f"Unknown or missing step type '{step_type}' for substep {idx}"
                    )
                StepClass = STEP_REGISTRY[step_type]
                step_instance: StepProtocol = StepClass(sub_logger, step_cfg)

                sub_logger.info(f"Launching substep {idx} of type '{step_type}'")
                await step_instance.execute(sub_context)
                sub_logger.info(f"Substep {idx} completed successfully")

            except Exception as exc:
                # Record first exception
                if failure["exc"] is None:
                    failure["exc"] = exc
                    failure["idx"] = idx
                sub_logger.error(
                    f"Substep {idx} failed: {exc}", exc_info=True
                )
                raise

            finally:
                semaphore.release()

        # Launch substeps with concurrency control and optional delay
        for idx, spec in enumerate(substeps):
            if failure["exc"]:
                self.logger.debug(
                    f"Fail-fast: aborting launch of remaining substeps at index {idx}"
                )
                break

            await semaphore.acquire()
            if delay > 0:
                await asyncio.sleep(delay)

            task = asyncio.create_task(run_substep(idx, spec))
            tasks.append(task)

        if not tasks:
            self.logger.info("No substeps were launched. Nothing to wait for.")
            return

        # Wait for first exception or all to finish
        done: Set[asyncio.Task] = set()
        pending: Set[asyncio.Task] = set()
        try:
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_EXCEPTION
            )
        except Exception:
            # Should not happen; tasks errors handled below
            pass

        if failure["exc"]:
            failed_idx: Optional[int] = failure.get("idx")
            self.logger.error(
                f"A substep failed at index {failed_idx}; cancelling remaining tasks"
            )
            for p in pending:
                p.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            raise RuntimeError(
                f"ParallelStep aborted due to failure in substep {failed_idx}"
            ) from failure["exc"]

        # All succeeded; ensure finalization
        await asyncio.gather(*done)
        success_count: int = len(done)
        self.logger.info(
            f"Completed ParallelStep: {success_count}/{total} substeps succeeded"
        )


=== File: recipe_executor/steps/read_files.py ===
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import yaml

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        content_key (str): Name under which to store file content in the context.
        optional (bool): Whether to continue if a file is not found (default: False).
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filename headers + content
            - "dict": Store a dictionary with file paths as keys and content as values
    """
    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    Step that reads one or more files from disk and stores their content in the execution context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        cfg = self.config
        raw_path = cfg.path
        paths: List[str] = []

        # Resolve and normalize paths (with template rendering)
        if isinstance(raw_path, str):
            rendered = render_template(raw_path, context)
            # Split comma-separated string into list
            if "," in rendered:
                parts = [p.strip() for p in rendered.split(",") if p.strip()]
                paths.extend(parts)
            else:
                paths.append(rendered)
        elif isinstance(raw_path, list):
            for entry in raw_path:
                if not isinstance(entry, str):
                    raise ValueError(f"Invalid path entry type: {entry!r}")
                rendered = render_template(entry, context)
                paths.append(rendered)
        else:
            raise ValueError(f"Invalid type for path: {type(raw_path)}")

        results: List[Any] = []
        result_map: Dict[str, Any] = {}

        for path in paths:
            self.logger.debug(f"Reading file at path: {path}")
            if not os.path.exists(path):
                msg = f"File not found: {path}"
                if cfg.optional:
                    self.logger.warning(f"Optional file missing, skipping: {path}")
                    continue
                raise FileNotFoundError(msg)

            # Read file content as UTF-8 text
            with open(path, mode="r", encoding="utf-8") as f:
                text = f.read()

            # Attempt to deserialize structured formats
            ext = os.path.splitext(path)[1].lower()
            content: Any = text
            try:
                if ext == ".json":
                    content = json.loads(text)
                elif ext in (".yaml", ".yml"):
                    content = yaml.safe_load(text)
            except Exception as exc:
                self.logger.warning(f"Failed to parse structured data from {path}: {exc}")
                content = text

            self.logger.info(f"Successfully read file: {path}")
            results.append(content)
            result_map[path] = content

        # Merge results according to merge_mode
        final_content: Any
        if not results:
            # No file was read
            if len(paths) <= 1:
                final_content = ""  # Single (missing) file yields empty string
            elif cfg.merge_mode == "dict":
                final_content = {}  # Dict of zero entries
            else:
                final_content = ""  # Concat yields empty string
        elif len(results) == 1:
            # Only one file read => return its content directly
            final_content = results[0]
        else:
            # Multiple files read
            if cfg.merge_mode == "dict":
                final_content = result_map
            else:
                # Default: concat mode, include header with filename
                segments: List[str] = []
                for p in paths:
                    if p in result_map:
                        raw = result_map[p]
                        # Convert raw back to text if it was structured
                        segment = raw if isinstance(raw, str) else json.dumps(raw)
                        segments.append(f"{p}\n{segment}")
                final_content = "\n".join(segments)

        # Store the merged content in context
        context[cfg.content_key] = final_content
        self.logger.info(f"Stored file content under key '{cfg.content_key}'")


=== File: recipe_executor/steps/registry.py ===
"""
Registry for mapping step type names to their implementation classes.

This registry is a simple global dictionary. Steps register themselves by
updating this mapping, allowing dynamic lookup based on the step type name.
"""
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global registry mapping step type names to their implementation classes.
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        files_key: Optional context key holding FileSpec or list of FileSpec.
        files: Optional direct list of dicts with 'path' and 'content' (or keys).
        root: Base path for output files.
    """
    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes files to disk based on FileSpec or dict inputs.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        files_to_write: List[Dict[str, Any]] = []
        # Render root path template
        root: str = render_template(self.config.root or ".", context)

        # Direct files list takes precedence
        if self.config.files is not None:
            for entry in self.config.files:
                # Path extraction
                if "path" in entry:
                    raw_path = entry["path"]
                elif "path_key" in entry:
                    key = entry["path_key"]
                    if key not in context:
                        raise KeyError(f"Path key '{key}' not found in context.")
                    raw_path = context[key]
                else:
                    raise ValueError("Each file entry must have 'path' or 'path_key'.")
                path = render_template(str(raw_path), context)

                # Content extraction
                if "content" in entry:
                    raw_content = entry["content"]
                elif "content_key" in entry:
                    key = entry["content_key"]
                    if key not in context:
                        raise KeyError(f"Content key '{key}' not found in context.")
                    raw_content = context[key]
                else:
                    raise ValueError("Each file entry must have 'content' or 'content_key'.")

                content: Any
                if isinstance(raw_content, str):
                    content = render_template(raw_content, context)
                else:
                    content = raw_content

                files_to_write.append({"path": path, "content": content})

        elif self.config.files_key is not None:
            key = self.config.files_key
            if key not in context:
                raise KeyError(f"Files key '{key}' not found in context.")
            raw = context[key]
            # Normalize to list of specs or dicts
            if isinstance(raw, FileSpec):
                items = [raw]
            elif isinstance(raw, dict):
                if "path" in raw and "content" in raw:
                    items = [raw]
                else:
                    raise ValueError(f"Malformed file dict under '{key}'.")
            elif isinstance(raw, list):  # type: ignore
                items = raw  # type: ignore
            else:
                raise ValueError(f"Unsupported type for files_key '{key}': {type(raw)}")

            for file_item in items:
                if isinstance(file_item, FileSpec):
                    path = render_template(file_item.path, context)
                    content_raw = file_item.content
                elif isinstance(file_item, dict):
                    if "path" not in file_item or "content" not in file_item:
                        raise ValueError(f"Invalid file entry under '{key}': {file_item}")
                    path = render_template(str(file_item["path"]), context)
                    content_raw = file_item["content"]
                else:
                    raise ValueError("Each file entry must be FileSpec or dict with 'path' and 'content'.")

                if isinstance(content_raw, str):
                    content = render_template(content_raw, context)
                else:
                    content = content_raw

                files_to_write.append({"path": path, "content": content})

        else:
            raise ValueError("Either 'files' or 'files_key' must be provided in WriteFilesConfig.")

        # Write out each file
        for file_entry in files_to_write:
            try:
                relative_path = file_entry.get("path", "")
                final_path = os.path.normpath(os.path.join(root, relative_path)) if root else os.path.normpath(relative_path)
                parent = os.path.dirname(final_path)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)

                content = file_entry.get("content")
                # Serialize dict or list to JSON
                if isinstance(content, (dict, list)):
                    try:
                        to_write = json.dumps(content, ensure_ascii=False, indent=2)
                    except Exception as err:
                        raise ValueError(f"Failed to serialize content for '{final_path}': {err}")
                else:
                    to_write = content  # type: ignore

                # Debug log before write
                self.logger.debug(f"[WriteFilesStep] Writing file: {final_path}\nContent:\n{to_write}")
                # Write file
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(to_write)

                size = len(to_write.encode("utf-8")) if isinstance(to_write, str) else 0
                self.logger.info(f"[WriteFilesStep] Wrote file: {final_path} ({size} bytes)")

            except Exception as exc:
                self.logger.error(f"[WriteFilesStep] Error writing file '{file_entry.get('path', '?')}': {exc}")
                raise


=== File: recipe_executor/utils/models.py ===
"""
Utility functions for generating Pydantic models from JSON-Schema object definitions.
"""
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, create_model

__all__ = ["json_object_to_pydantic_model"]


def json_object_to_pydantic_model(
    schema: Dict[str, Any], model_name: str = "SchemaModel"
) -> Type[BaseModel]:
    """
    Convert a JSON-Schema object fragment into a Pydantic BaseModel subclass.

    Args:
        schema: A JSON-Schema fragment describing an object (type must be "object").
        model_name: Name for the generated Pydantic model class.

    Returns:
        A subclass of pydantic.BaseModel corresponding to the schema.

    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
    # Validate top-level schema
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary.")
    if "type" not in schema:
        raise ValueError('Schema missing required "type" property.')
    if schema["type"] != "object":
        raise ValueError('Root schema type must be "object".')

    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    if not isinstance(properties, dict):
        raise ValueError('Schema "properties" must be a dictionary if present.')
    if not isinstance(required_fields, list):
        raise ValueError('Schema "required" must be a list if present.')

    # Counter for naming nested models deterministically
    class _Counter:
        def __init__(self) -> None:
            self._cnt = 0

        def next(self) -> int:
            self._cnt += 1
            return self._cnt

    counter = _Counter()

    def _parse_field(
        field_schema: Dict[str, Any], field_name: str, parent_name: str
    ) -> Tuple[Any, Any]:
        # Ensure valid schema fragment
        if not isinstance(field_schema, dict):
            raise ValueError(f"Schema for field '{field_name}' must be a dictionary.")
        if "type" not in field_schema:
            raise ValueError(f"Schema for field '{field_name}' missing required 'type'.")

        ftype = field_schema["type"]
        # Primitive types
        if ftype == "string":
            return str, ...
        if ftype == "integer":
            return int, ...
        if ftype == "number":
            return float, ...
        if ftype == "boolean":
            return bool, ...
        # Nested object
        if ftype == "object":
            nested_name = f"{parent_name}_{field_name.capitalize()}Obj{counter.next()}"
            nested_model = _build_model(field_schema, nested_name)
            return nested_model, ...
        # Array / list
        if ftype in ("array", "list"):
            items = field_schema.get("items")
            if not isinstance(items, dict):
                raise ValueError(
                    f"Array field '{field_name}' missing valid 'items' schema."
                )
            item_type, _ = _parse_field(items, f"{field_name}_item", parent_name)
            return List[item_type], ...
        # Fallback
        return Any, ...

    def _wrap_optional(
        field_schema: Dict[str, Any], is_required: bool, field_name: str, parent_name: str
    ) -> Tuple[Any, Any]:
        type_hint, default = _parse_field(field_schema, field_name, parent_name)
        if not is_required:
            type_hint = Optional[type_hint]  # type: ignore
            default = None
        return type_hint, default

    def _build_model(obj_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
        # Validate object schema
        if not isinstance(obj_schema, dict):
            raise ValueError(f"Nested schema '{name}' must be a dictionary.")
        if obj_schema.get("type") != "object":
            raise ValueError(f"Nested schema '{name}' type must be 'object'.")

        props = obj_schema.get("properties", {})
        req = obj_schema.get("required", [])
        if not isinstance(props, dict):
            raise ValueError(f"Nested schema '{name}' properties must be a dictionary.")
        if not isinstance(req, list):
            raise ValueError(f"Nested schema '{name}' required must be a list.")

        fields: Dict[str, Tuple[Any, Any]] = {}
        for prop, subschema in props.items():
            is_req = prop in req
            hint, default = _wrap_optional(subschema, is_req, prop, name)
            fields[prop] = (hint, default)

        return create_model(name, **fields)  # type: ignore

    # Build and return the top-level model
    return _build_model(schema, model_name)


=== File: recipe_executor/utils/templates.py ===
"""
Template Utility Component

Provides a simple function to render Liquid templates
using values from a ContextProtocol.
"""
from typing import Any, Dict

import liquid
from liquid.exceptions import LiquidError

from recipe_executor.protocols import ContextProtocol

__all__ = ["render_template"]

def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are passed as-is to the template.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    context_dict: Dict[str, Any] = context.dict()
    try:
        template = liquid.Template(text)
        return template.render(**context_dict)
    except LiquidError as exc:
        raise ValueError(
            f"Template rendering failed: {exc}\n"
            f"Template: {text!r}\n"
            f"Context: {context_dict!r}"
        ) from exc
    except Exception as exc:
        raise ValueError(
            f"Unknown error during template rendering: {exc}\n"
            f"Template: {text!r}\n"
            f"Context: {context_dict!r}"
        ) from exc


