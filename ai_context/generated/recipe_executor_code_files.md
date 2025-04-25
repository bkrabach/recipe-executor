# AI Context Files
Date: 4/25/2025, 11:27:14 AM
Files: 26

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


=== File: recipe_executor/README.md ===
# Recipe Executor Code Files

**NOTE: THE FILES IN THIS DIRECTORY ARE GENERATED. DO NOT EDIT THEM DIRECTLY.**

These files are generated by running the `make recipe-executor-create` or `make recipe-executor-edit` commands from the repository root. The code is generated from the "recipes" in [../recipes/recipe_executor]. The actual implementation will change more or less on each generation depending up on which model you use and if you choose the `create` or the `edit` option. The intent is to modify the component `spec` and `docs` files and then generate the code files vs editing the code files directly.

To generate a version of these files, run the script from the repository root:

```bash
# Navigate to the repository root
cd /path/to/your/repo

# Run the script to generate the recipe executor code files without any influence from existing code
make recipe-executor-create

# Or to generate the recipe executor code files with some influence from existing code
make recipe-executor-edit
```

These are shortcuts for:

- Create:
  - `recipe-tool --execute recipes/recipe_executor/create.json`
- Edit:
  - `recipe-tool --execute recipes/recipe_executor/edit.json`


=== File: recipe_executor/__init__.py ===


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
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self._config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

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
        return isinstance(key, str) and key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Return iterator over a snapshot of keys to avoid issues during mutation
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

    def clone(self) -> "ContextProtocol":
        """
        Create a deep copy of this Context, including artifacts and config.
        """
        # We deep copy internally via __init__
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
import json
import logging
from pathlib import Path
from typing import Union, Dict, Any

from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
from recipe_executor.models import Recipe
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Concrete implementation of the ExecutorProtocol. Responsible for loading,
    validating, and executing recipes step by step using a shared context.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Load a recipe (from path, JSON string, dict, or Recipe model), validate it,
        and run its steps sequentially using the provided context.
        """
        # Determine source and load into Recipe model
        if isinstance(recipe, Recipe):
            self.logger.debug("Using provided Recipe model instance.")
            recipe_model = recipe
        else:
            # Load from pathlib.Path
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
            # Load from string (file path or raw JSON)
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
            # Load from dict
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
            recipe_summary = recipe_model.model_dump()
        except Exception:
            recipe_summary = {}
        step_count = len(recipe_model.steps)
        self.logger.debug(f"Recipe loaded: {recipe_summary}. Steps count: {step_count}")

        # Execute each step sequentially
        for idx, step in enumerate(recipe_model.steps):
            step_type = step.type
            config = step.config or {}
            self.logger.debug(f"Executing step {idx} of type '{step_type}' with config: {config}")

            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}")

            step_cls = STEP_REGISTRY[step_type]
            step_instance = step_cls(self.logger, config)

            try:
                result = step_instance.execute(context)
                # Support async or sync execute methods
                if hasattr(result, "__await__"):
                    await result  # type: ignore
            except Exception as e:
                msg = f"Error executing step {idx} ('{step_type}'): {e}"
                raise ValueError(msg) from e

            self.logger.debug(f"Step {idx} ('{step_type}') completed successfully.")

        self.logger.debug("All recipe steps completed successfully.")


=== File: recipe_executor/llm_utils/azure_openai.py ===
import os
import logging
from typing import Optional

import openai
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

    # Determine deployment name
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
            # Azure Identity authentication
            logger.info("Using Azure Managed Identity for authentication")
            if azure_client_id:
                cred = ManagedIdentityCredential(client_id=azure_client_id)
            else:
                cred = DefaultAzureCredential()
            # Token provider for OpenAI
            token_provider = get_bearer_token_provider(
                cred, "https://cognitiveservices.azure.com/.default"
            )
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment,
            )
            auth_method = "Azure Managed Identity"
        else:
            # API key authentication
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
    except Exception as e:
        logger.error(f"Failed to create AsyncAzureOpenAI client: {e}")
        raise

    # Wrap client in PydanticAI provider
    logger.info(f"Creating Azure OpenAI model '{model_name}' with {auth_method}")
    provider = OpenAIProvider(openai_client=azure_client)
    try:
        model = OpenAIModel(model_name=model_name, provider=provider)
    except Exception as e:
        logger.error(f"Failed to create OpenAIModel: {e}")
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
from typing import Any, Dict, List, Optional, Union

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio


# Keys considered sensitive for masking
_SENSITIVE_KEYS = ("key", "secret", "token", "password")

def _mask_value(value: Any, key: Optional[str] = None) -> Any:
    """
    Mask sensitive values in a configuration dictionary.
    """
    # If the key indicates sensitive data, replace value
    if key and any(sensitive in key.lower() for sensitive in _SENSITIVE_KEYS):
        return "***"
    # If dict, apply recursively
    if isinstance(value, dict):
        return {k: _mask_value(v, k) for k, v in value.items()}
    # Otherwise, return as is
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

    # Determine server type
    if "url" in config:
        # HTTP transport
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

    # Stdio transport
    if "command" in config:
        command = config.get("command")
        if not isinstance(command, str):
            raise ValueError("MCP stdio configuration requires a string 'command'")
        args = config.get("args")
        if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
            raise ValueError("MCP stdio 'args' must be a list of strings")
        logger.info("Configuring MCPServerStdio with command: %s args: %s", command, args)
        try:
            return MCPServerStdio(command, args=args)
        except Exception as error:
            msg = f"Failed to create stdio MCP server for command {command}: {error}"
            logger.error(msg)
            raise RuntimeError(msg) from error

    # Unrecognized configuration
    raise ValueError(
        "Invalid MCP server configuration: provide either 'url' for HTTP or 'command' for stdio"
    )


=== File: recipe_executor/logger.py ===
import os
import sys
import logging
from typing import Tuple

def init_logger(
    log_dir: str = "logs",
    stdio_log_level: str = "INFO"
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
    # Prepare logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Reset existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Create log directory
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Formatter for all handlers
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handlers configuration
    paths: Tuple[str, str, str] = (
        os.path.join(log_dir, "debug.log"),
        os.path.join(log_dir, "info.log"),
        os.path.join(log_dir, "error.log"),
    )

    levels = (logging.DEBUG, logging.INFO, logging.ERROR)
    names = ("debug", "info", "error")

    for fname, level, name in zip(paths, levels, names):
        try:
            fh = logging.FileHandler(fname, mode="w", encoding="utf-8")
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            raise Exception(f"Failed to set up {name} log file '{fname}': {e}")

    # Console handler
    lvl_name = stdio_log_level.upper()
    if lvl_name == "WARN":
        lvl_name = "WARNING"
    if lvl_name not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        lvl_name = "INFO"
    console_level = getattr(logging, lvl_name)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Initialization logs
    logger.debug("Logger initialized: log_dir='%s', stdio_log_level='%s'", log_dir, lvl_name)
    logger.info("Logger initialized successfully")

    return logger


=== File: recipe_executor/main.py ===
import argparse
import asyncio
import sys
import time
import traceback
from typing import Dict, List

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_kv_list(entries: List[str], arg_name: str) -> Dict[str, str]:
    """
    Parse a list of key=value strings into a dictionary.

    Raises ValueError if any entry is not in key=value format.
    """
    result: Dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Invalid {arg_name} format '{entry}', expected key=value")
        key, value = entry.split("=", 1)
        if not key:
            raise ValueError(f"Invalid {arg_name} format '{entry}', key is empty")
        result[key] = value
    return result


async def run_execution(recipe_path: str, context: Context, logger) -> None:
    """
    Orchestrate the asynchronous execution of a recipe.
    """
    logger.info("Starting Recipe Executor Tool")
    logger.info(f"Executing recipe: {recipe_path}")
    start_time = time.time()
    executor = Executor(logger)
    await executor.execute(recipe_path, context)
    end_time = time.time()
    elapsed = end_time - start_time
    logger.info(f"Recipe executed successfully in {elapsed:.2f} seconds")


def main() -> None:
    """
    Main entry point for the Recipe Executor CLI.
    """
    # Load environment variables from .env, if present
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Recipe Executor: run JSON/YAML recipes with context and configuration."
    )
    parser.add_argument(
        "recipe_path",
        help="Path to the recipe file to execute."
    )
    parser.add_argument(
        "--log-dir",
        dest="log_dir",
        default="logs",
        help="Directory to store log files (default: 'logs')."
    )
    parser.add_argument(
        "--context",
        dest="context",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Context artifact values (can be repeated)."
    )
    parser.add_argument(
        "--config",
        dest="config",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Static config values (can be repeated)."
    )
    args = parser.parse_args()

    # Initialize logger
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: {e}\n")
        sys.exit(1)

    # Parse context and config key/value arguments
    try:
        context_dict = parse_kv_list(args.context, "context")
        config_dict = parse_kv_list(args.config, "config")
    except ValueError as e:
        sys.stderr.write(f"Argument Error: {e}\n")
        sys.exit(1)

    # Debug log of parsed arguments and initial state
    logger.debug(
        f"Parsed arguments: recipe={args.recipe_path}, log_dir={args.log_dir}, "
        f"context={context_dict}, config={config_dict}"
    )

    # Create execution context
    context = Context(artifacts=context_dict, config=config_dict)

    # Run the asynchronous execution
    try:
        asyncio.run(run_execution(args.recipe_path, context, logger))
    except Exception as e:
        # Log and report any execution errors
        logger.error(
            f"An error occurred during recipe execution: {e}",
            exc_info=True
        )
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)

    # Normal exit
    sys.exit(0)


if __name__ == "__main__":
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
        steps: A list containing the steps of the recipe.
    """
    steps: List[RecipeStep]  # List of steps defining the recipe


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
Recipe Executor Steps Package

Registers standard steps in the STEP_REGISTRY on import.
"""
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.llm_generate import LLMGenerateStep
from recipe_executor.steps.loop import LoopStep
from recipe_executor.steps.mcp import MCPStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register built-in steps by type name
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": MCPStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})

__all__ = [
    "STEP_REGISTRY",
    "ExecuteRecipeStep",
    "LLMGenerateStep",
    "LoopStep",
    "MCPStep",
    "ParallelStep",
    "ReadFilesStep",
    "WriteFilesStep",
]


=== File: recipe_executor/steps/base.py ===
"""
Base step component for the Recipe Executor.
Defines a generic BaseStep class and the base Pydantic StepConfig.
"""
from __future__ import annotations

import logging
from typing import Generic, TypeVar

from pydantic import BaseModel

# Avoid circular imports at runtime by importing for type checking if needed
from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for steps.
    Extend this class to add step-specific fields.
    """
    # No common fields; each step should subclass and define its own
    pass

# Generic type for step configuration
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
        self.logger.debug(
            f"Initialized {self.__class__.__name__} with config: {self.config!r}"
        )

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step logic.

        Must be overridden by subclasses.

        Args:
            context: Execution context adhering to ContextProtocol.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the execute method"
        )


=== File: recipe_executor/steps/execute_recipe.py ===
from typing import Dict, Any
import os
import logging

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

        # Validate path exists
        if not os.path.isfile(rendered_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {rendered_path}")

        # Apply context overrides
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
            self.logger.error(f"Error executing sub-recipe {rendered_path}: {e}")
            raise RuntimeError(f"Failed to execute sub-recipe '{rendered_path}': {e}") from e


=== File: recipe_executor/steps/llm_generate.py ===
import logging
from typing import Any, Dict, List, Optional, Type, Union

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
        output_format: The format of the LLM output (text, files, or JSON).
            - text: Plain text output.
            - files: List of files generated by the LLM.
            - object: Object based on the provided JSON schema.
            - list: List of items based on the provided JSON schema.
        output_key: The name under which to store the LLM output in context.
    """

    prompt: str
    model: str = "openai/gpt-4o"
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any], List[Any]]
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):
    files: List[FileSpec]


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        prompt_str: str = render_template(self.config.prompt, context)
        model_str: str = render_template(self.config.model, context) if self.config.model else "openai/gpt-4o"
        output_key: str = render_template(self.config.output_key, context)
        mcp_server_configs: List[Dict[str, Any]] = []
        mcp_servers: Optional[List[Any]] = None

        # Combine mcp_servers from step config and context config
        step_mcp_servers = self.config.mcp_servers if self.config.mcp_servers is not None else []
        context_mcp_servers = context.get_config().get("mcp_servers", [])
        mcp_server_configs = list(step_mcp_servers) + list(context_mcp_servers)

        if mcp_server_configs:
            mcp_servers = [get_mcp_server(logger=self.logger, config=server_cfg) for server_cfg in mcp_server_configs]
        else:
            mcp_servers = None

        output_format = self.config.output_format
        result: Any = None

        try:
            if output_format == "text":
                llm = LLM(self.logger, model=model_str, mcp_servers=mcp_servers)
                self.logger.debug(f"Calling LLM with model: {model_str} (output: text)")
                result = await llm.generate(prompt_str, output_type=str)
                context[output_key] = result
                return
            elif output_format == "files":
                llm = LLM(self.logger, model=model_str, mcp_servers=mcp_servers)
                self.logger.debug(f"Calling LLM with model: {model_str} (output: files)")
                result = await llm.generate(prompt_str, output_type=FileSpecCollection)
                if isinstance(result, FileSpecCollection):
                    context[output_key] = result.files
                else:
                    # Defensive in case the LLM doesn't return the expected model
                    raise RuntimeError(f"LLM did not return a FileSpecCollection: got {type(result)}")
                return
            elif isinstance(output_format, list):
                # Interpret as list of items; wrap as object with `items` root
                object_schema: Dict[str, Any] = {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": output_format[0] if output_format else {}}},
                }
                PydanticModel: Type[BaseModel] = json_object_to_pydantic_model(object_schema, model_name="ListModel")
                llm = LLM(self.logger, model=model_str, mcp_servers=mcp_servers)
                self.logger.debug(f"Calling LLM with model: {model_str} (output: list)")
                model_result = await llm.generate(prompt_str, output_type=PydanticModel)
                items = getattr(model_result, "items", None)
                if items is None and isinstance(model_result, dict):
                    items = model_result.get("items")
                if items is None:
                    raise RuntimeError("LLM did not return an object with 'items' for list output format.")
                context[output_key] = items
                return
            elif isinstance(output_format, dict):
                # Interpret as JSON schema for object format
                PydanticModel: Type[BaseModel] = json_object_to_pydantic_model(output_format, model_name="ObjectModel")
                llm = LLM(self.logger, model=model_str, mcp_servers=mcp_servers)
                self.logger.debug(f"Calling LLM with model: {model_str} (output: object)")
                model_result = await llm.generate(prompt_str, output_type=PydanticModel)
                if isinstance(model_result, BaseModel):
                    context[output_key] = model_result.model_dump()
                elif isinstance(model_result, dict):
                    context[output_key] = model_result
                else:
                    raise RuntimeError("LLM returned unexpected type for object output format.")
                return
            else:
                raise ValueError(f"Unsupported output_format: {output_format}")
        except Exception as e:
            self.logger.error(f"LLM call failed for model '{model_str}' with prompt: {prompt_str}\nError: {e}")
            raise


=== File: recipe_executor/steps/loop.py ===
import logging
from typing import Any, Dict, Iterator, List, Tuple, Union

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Key in the context containing the collection to iterate over.
        item_key: Key to use when storing the current item in each iteration's context.
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error (default: True).
    """

    items: str
    item_key: str
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve the items path via template
        path_str = render_template(self.config.items, context)
        if not path_str:
            raise ValueError(f"LoopStep: items path resolved to empty string from '{self.config.items}'")

        # Traverse context snapshot to get the collection
        data = context.dict()
        current: Any = data
        for part in path_str.split("."):
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"LoopStep: could not resolve part '{part}' in path '{path_str}'")
            current = current[part]
        items_obj = current

        # Determine iteration type and prepare results container
        if isinstance(items_obj, dict):
            iter_items: Iterator[Tuple[Any, Any]] = iter(items_obj.items())
            is_mapping = True
            results: Dict[Any, Any] = {}
            count = len(items_obj)
        elif isinstance(items_obj, (list, tuple)):
            iter_items = enumerate(items_obj)
            is_mapping = False
            results = []  # type: ignore
            count = len(items_obj)
        elif items_obj is None:
            self.logger.info(f"LoopStep: no items found at '{path_str}', storing empty result")
            empty: Union[List[Any], Dict[Any, Any]] = []
            context[self.config.result_key] = empty
            return
        else:
            # Single non-iterable item
            iter_items = enumerate([items_obj])
            is_mapping = False
            results = []  # type: ignore
            count = 1

        self.logger.info(f"LoopStep: processing {count} item(s) from '{path_str}'")
        errors: List[Dict[str, Any]] = []

        from recipe_executor.executor import Executor

        # Iterate and execute substeps in isolated contexts
        for key, item in iter_items:
            label = key if is_mapping else f"index {key}"
            self.logger.debug(f"LoopStep: start processing item {label}")
            sub_ctx = context.clone()
            # Inject current item and index/key
            sub_ctx[self.config.item_key] = item
            if is_mapping:
                sub_ctx["__key"] = key  # type: ignore
            else:
                sub_ctx["__index"] = key  # type: ignore

            # Assemble a small recipe for the substeps
            recipe = {"steps": self.config.substeps}

            executor = Executor(self.logger)
            try:
                await executor.execute(recipe, sub_ctx)
            except Exception as e:
                self.logger.error(f"LoopStep: error processing item {label}: {e}", exc_info=True)
                err_info = {"key": key, "error": str(e)}
                errors.append(err_info)
                if self.config.fail_fast:
                    raise
                # skip adding a result for failed item
                continue

            # Collect the processed item (load from same item_key)
            try:
                result_item = sub_ctx[self.config.item_key]
            except KeyError:
                self.logger.error(f"LoopStep: missing '{self.config.item_key}' after processing item {label}")
                if self.config.fail_fast:
                    raise
                continue

            # Store into results
            if is_mapping:
                results[key] = result_item  # type: ignore
            else:
                results.append(result_item)  # type: ignore
            self.logger.debug(f"LoopStep: finished processing item {label}")

        # Store final results and any errors
        context[self.config.result_key] = results  # type: ignore
        if errors:
            err_key = f"{self.config.result_key}__errors"
            context[err_key] = errors  # type: ignore
            self.logger.info(f"LoopStep: encountered {len(errors)} error(s); stored under '{err_key}'")
        self.logger.info(
            f"LoopStep: completed loop, stored {count - len(errors)} successful result(s) under '{self.config.result_key}'"
        )


=== File: recipe_executor/steps/mcp.py ===
"""
MCPStep component for invoking tools on remote MCP servers and storing results in context.
"""

import logging
from typing import Any, Dict, List, Optional

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
        # Render tool name and arguments
        tool_name: str = render_template(self.config.tool_name, context)
        raw_args: Dict[str, Any] = self.config.arguments or {}
        arguments: Dict[str, Any] = {}
        for key, value in raw_args.items():
            if isinstance(value, str):
                arguments[key] = render_template(value, context)
            else:
                arguments[key] = value

        # Prepare server connection parameters
        server_conf = self.config.server
        client_cm: Any
        service_desc: str

        # Decide on transport: stdio or SSE (HTTP)
        if "command" in server_conf:
            # stdio transport
            cmd: str = render_template(server_conf.get("command", ""), context)
            args_list: List[str] = []
            for arg in server_conf.get("args", []):
                if isinstance(arg, str):
                    args_list.append(render_template(arg, context))
                else:
                    args_list.append(arg)
            env_conf: Optional[Dict[str, str]] = None
            if server_conf.get("env") is not None:
                env_conf = {}
                for k, v in server_conf.get("env", {}).items():
                    env_conf[k] = render_template(v, context) if isinstance(v, str) else str(v)
            cwd: Optional[str] = None
            if server_conf.get("working_dir") is not None:
                cwd = render_template(server_conf.get("working_dir", "."), context)
            server_params = StdioServerParameters(
                command=cmd,
                args=args_list,
                env=env_conf,
                cwd=cwd,
            )
            client_cm = stdio_client(server_params)
            service_desc = f"stdio command '{cmd}'"
        else:
            # SSE/HTTP transport
            url: str = render_template(server_conf.get("url", ""), context)
            headers_conf: Optional[Dict[str, Any]] = None
            if server_conf.get("headers") is not None:
                headers_conf = {}
                for k, v in server_conf.get("headers", {}).items():
                    headers_conf[k] = render_template(v, context) if isinstance(v, str) else v
            client_cm = sse_client(url, headers=headers_conf)
            service_desc = f"SSE server '{url}'"

        # Connect and invoke the tool
        self.logger.debug(f"Connecting to MCP server: {service_desc}")
        try:
            async with client_cm as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    # Initialize the MCP client session
                    await session.initialize()
                    self.logger.debug(f"Invoking tool '{tool_name}' with arguments {arguments}")
                    try:
                        result: CallToolResult = await session.call_tool(
                            name=tool_name,
                            arguments=arguments,
                        )
                    except Exception as e:
                        raise ValueError(f"Tool invocation failed for '{tool_name}' on {service_desc}: {e}") from e
        except ValueError:
            # propagate our ValueError for tool invocation
            raise
        except Exception as e:
            raise ValueError(f"Failed to call tool '{tool_name}' on {service_desc}: {e}") from e

        # Convert result to a dictionary
        try:
            result_dict: Dict[str, Any] = result.__dict__
        except Exception:
            # fallback for non-dataclass-like objects
            result_dict = {k: getattr(result, k) for k in dir(result) if not k.startswith("_")}

        # Store result in context
        context[self.config.result_key] = result_dict


=== File: recipe_executor/steps/parallel.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional

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
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        total = len(self.config.substeps)
        self.logger.info(
            f"Starting ParallelStep: {total} substeps, "
            f"max_concurrency={self.config.max_concurrency}, delay={self.config.delay}"
        )

        if total == 0:
            self.logger.info("ParallelStep has no substeps to execute. Skipping.")
            return

        # Determine concurrency limit
        concurrency = (
            self.config.max_concurrency if self.config.max_concurrency > 0 else total
        )
        semaphore = asyncio.Semaphore(concurrency)

        # Holder for first failure
        failure_holder: Dict[str, Optional[Exception]] = {"exc": None}
        tasks: List[asyncio.Task] = []

        async def run_substep(idx: int, spec: Dict[str, Any]) -> None:
            # Substep isolation and execution
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
                # Execute substep
                await step_instance.execute(sub_context)
                sub_logger.info(f"Substep {idx} completed successfully")

            except Exception as e:
                # Record first exception and log
                if failure_holder["exc"] is None:
                    failure_holder["exc"] = e
                sub_logger.error(
                    f"Substep {idx} failed: {e}", exc_info=True
                )
                # Propagate to allow gather to detect
                raise

            finally:
                # Release the semaphore slot
                semaphore.release()

        # Launch substeps with concurrency control and optional delay
        for idx, spec in enumerate(self.config.substeps):
            # Fail-fast: stop launching if error recorded
            if failure_holder["exc"]:
                self.logger.debug(
                    f"Fail-fast: aborting launch of remaining substeps at index {idx}"
                )
                break

            await semaphore.acquire()
            # Staggered launch
            if self.config.delay > 0:
                await asyncio.sleep(self.config.delay)

            task = asyncio.create_task(run_substep(idx, spec))
            tasks.append(task)

        # Await completion or first failure
        if not tasks:
            self.logger.info("No substeps were launched. Nothing to wait for.")
            return

        # Wait for tasks, fail fast on exception
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_EXCEPTION
        )

        # If any task raised, cancel pending and re-raise
        if failure_holder["exc"]:
            self.logger.error(
                "A substep failed; cancelling remaining tasks and aborting ParallelStep"
            )
            for p in pending:
                p.cancel()
            # Wait for cancellation to finish
            await asyncio.gather(*pending, return_exceptions=True)
            # Shutdown complete; propagate error
            raise RuntimeError(
                "ParallelStep aborted due to substep failure"
            ) from failure_holder["exc"]

        # All succeeded; gather results
        await asyncio.gather(*done)
        success_count = len(done)
        self.logger.info(
            f"Completed ParallelStep: {success_count}/{total} substeps succeeded"
        )


=== File: recipe_executor/steps/read_files.py ===
import json
import logging
import os
from typing import Any, Dict, List, Union

import yaml

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        content_key (str): Name to store the file content in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + content
            - "dict": Store a dictionary with filenames as keys and content as values
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

        # Resolve and normalize paths
        if isinstance(raw_path, str):
            rendered = render_template(raw_path, context)
            # Split comma-separated
            if "," in rendered:
                parts = [p.strip() for p in rendered.split(",") if p.strip()]
                paths = parts
            else:
                paths = [rendered]
        elif isinstance(raw_path, list):
            for p in raw_path:
                if not isinstance(p, str):
                    raise ValueError(f"Invalid path entry: {p!r}")
                rendered = render_template(p, context)
                paths.append(rendered)
        else:
            raise ValueError(f"Invalid type for path: {type(raw_path)}")

        results: List[Any] = []
        result_dict: Dict[str, Any] = {}

        for path in paths:
            self.logger.debug(f"Reading file at path: {path}")
            if not os.path.exists(path):
                msg = f"File not found: {path}"
                if cfg.optional:
                    self.logger.warning(f"Optional file missing, skipping: {path}")
                    continue
                raise FileNotFoundError(msg)

            # Read file content
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            # Attempt deserialization if applicable
            ext = os.path.splitext(path)[1].lower()
            content: Any
            try:
                if ext == ".json":
                    content = json.loads(text)
                elif ext in (".yaml", ".yml"):
                    content = yaml.safe_load(text)
                else:
                    content = text
            except Exception as e:
                self.logger.warning(f"Failed to parse structured data from {path}: {e}")
                content = text

            self.logger.info(f"Successfully read file: {path}")
            results.append(content)
            result_dict[path] = content

        # Merge results
        final_content: Any
        if not results:
            # No files read
            if len(paths) <= 1:
                final_content = ""  # single missing
            elif cfg.merge_mode == "dict":
                final_content = {}
            else:
                final_content = ""
        elif len(results) == 1:
            # Single file
            final_content = results[0]
        else:
            # Multiple files
            if cfg.merge_mode == "dict":
                final_content = result_dict
            else:
                # concat mode
                parts: List[str] = []
                for p in paths:
                    if p in result_dict:
                        raw = result_dict[p]
                        parts.append(f"{p}\n{raw}")
                final_content = "\n".join(parts)

        # Store in context
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
        files_key: Optional[str] - Context key holding a List[FileSpec] or single FileSpec.
        files: Optional[List[Dict[str, Any]]] - Direct list of dicts with 'path' and 'content' (or content_key/path_key).
        root: str - Base path to prepend to all output file paths (default ".").
    """

    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        files_to_write: List[Dict[str, Any]] = []
        root: str = render_template(self.config.root or ".", context)

        # Prefer files param, fallback to files_key in context
        if self.config.files is not None:
            for file_in in self.config.files:
                # Extract path
                if "path" in file_in:
                    raw_path = file_in["path"]
                elif "path_key" in file_in:
                    key = file_in["path_key"]
                    if key not in context:
                        raise KeyError(f"Path key '{key}' not found in context.")
                    raw_path = context[key]
                else:
                    raise ValueError("Each file entry must have either 'path' or 'path_key'.")
                # Render path template
                path = render_template(str(raw_path), context)

                # Extract content
                if "content" in file_in:
                    content_raw = file_in["content"]
                elif "content_key" in file_in:
                    key = file_in["content_key"]
                    if key not in context:
                        raise KeyError(f"Content key '{key}' not found in context.")
                    content_raw = context[key]
                else:
                    raise ValueError("Each file entry must have either 'content' or 'content_key'.")
                # Render content template if string
                content = render_template(content_raw, context) if isinstance(content_raw, str) else content_raw
                files_to_write.append({"path": path, "content": content})
        elif self.config.files_key is not None:
            if self.config.files_key not in context:
                raise KeyError(f"Files key '{self.config.files_key}' not found in context.")
            files_data = context[self.config.files_key]
            # Support single FileSpec or list
            files_raw: Union[FileSpec, Dict[str, Any], List[Any]] = files_data
            if isinstance(files_raw, FileSpec):
                files_raw = [files_raw]
            elif isinstance(files_raw, dict):
                # Could be a dict with path and content
                if "path" in files_raw and "content" in files_raw:
                    files_raw = [files_raw]
                else:
                    raise ValueError(f"Malformed file dict under '{self.config.files_key}'.")

            for file_item in files_raw:
                # Accept FileSpec or dict
                if isinstance(file_item, FileSpec):
                    path = render_template(file_item.path, context)
                    content = file_item.content
                elif isinstance(file_item, dict):
                    if "path" not in file_item or "content" not in file_item:
                        raise ValueError(f"Invalid file entry in list under '{self.config.files_key}': {file_item}")
                    path = render_template(str(file_item["path"]), context)
                    content = file_item["content"]
                else:
                    raise ValueError("Each file entry must be FileSpec or dict with 'path' and 'content'.")

                # Render content template if string
                content = render_template(content, context) if isinstance(content, str) else content
                files_to_write.append({"path": path, "content": content})
        else:
            raise ValueError("Either 'files' or 'files_key' must be provided in WriteFilesConfig.")

        # Write files
        for file_out in files_to_write:
            try:
                final_path = os.path.join(root, file_out["path"]) if root else file_out["path"]
                final_path = os.path.normpath(final_path)
                parent_dir = os.path.dirname(final_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                content = file_out["content"]

                # Always render template on content if it's a string (already done above)

                # Before writing, if content is dict or list, serialize to JSON
                to_write: str
                if isinstance(content, (dict, list)):
                    try:
                        to_write = json.dumps(content, ensure_ascii=False, indent=2)
                    except Exception as err:
                        raise ValueError(f"Failed to serialize content for {final_path}: {err}")
                else:
                    to_write = content
                # Logging before write
                self.logger.debug(f"[WriteFilesStep] Writing file: {final_path}\nContent:\n{to_write}")
                # Write file (UTF-8, overwrite)
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(to_write)
                self.logger.info(f"[WriteFilesStep] Wrote file: {final_path} ({len(to_write.encode('utf-8'))} bytes)")
            except Exception as err:
                self.logger.error(f"[WriteFilesStep] Error writing file '{file_out.get('path', '?')}': {err}")
                raise


=== File: recipe_executor/utils/models.py ===
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, create_model

__all__ = ["json_object_to_pydantic_model"]


def json_object_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]:
    """
    Convert a JSON object dictionary into a dynamic Pydantic model.
    Args:
        schema: A valid JSON-Schema fragment describing an object.
        model_name: Name given to the generated model class.
    Returns:
        A subclass of `pydantic.BaseModel` suitable for validation & serialization.
    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary.")
    if "type" not in schema:
        raise ValueError('Schema missing required "type" property.')
    if schema["type"] != "object":
        raise ValueError('Root schema type must be "object".')

    properties: Dict[str, Any] = schema.get("properties", {})
    required_fields: List[str] = schema.get("required", [])

    if not isinstance(properties, dict):
        raise ValueError('Schema "properties" must be a dictionary if present.')
    if not isinstance(required_fields, list):
        raise ValueError('Schema "required" must be a list if present.')

    # Nested object counter, used for deterministic model naming
    class NestedCounter:
        def __init__(self):
            self.count = 0

        def next(self) -> int:
            self.count += 1
            return self.count

    nested_counter = NestedCounter()

    def parse_schema_field(field_schema: Dict[str, Any], field_name: str, parent_model_name: str) -> Tuple[Any, Any]:
        """
        Returns (type_annotation, default_value)
        """
        # Check for valid 'type'
        field_type = field_schema.get("type")
        if not field_type:
            raise ValueError(f'Schema for field "{field_name}" missing required "type" property.')
        # Primitive types
        if field_type == "string":
            return str, ...
        if field_type == "integer":
            return int, ...
        if field_type == "number":
            return float, ...
        if field_type == "boolean":
            return bool, ...
        if field_type == "object":
            # Recursively create nested model
            next_count = nested_counter.next()
            nested_name = f"{parent_model_name}_{field_name.capitalize()}Obj{next_count}"
            nested_model = _create_model_from_schema(field_schema, nested_name)
            return nested_model, ...
        if field_type in ("array", "list"):
            items_schema = field_schema.get("items")
            if not isinstance(items_schema, dict):
                # items must be present for arrays
                raise ValueError(f'Array field "{field_name}" missing valid "items" schema.')
            item_type, _ = parse_schema_field(items_schema, f"{field_name}_item", parent_model_name)
            return List[item_type], ...
        # Fallback for unsupported/unknown type
        return Any, ...

    def parse_optional_schema_field(
        field_schema: Dict[str, Any], is_required: bool, field_name: str, parent_model_name: str
    ) -> Tuple[Any, Any]:
        # Adjust required/optional
        type_annotation, default_val = parse_schema_field(field_schema, field_name, parent_model_name)
        if not is_required:
            type_annotation = Optional[type_annotation]
            default_val = None
        return type_annotation, default_val

    def _create_model_from_schema(object_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
        if not isinstance(object_schema, dict):
            raise ValueError("Nested schema must be a dictionary.")
        if object_schema.get("type") != "object":
            raise ValueError(f'Nested schema "{name}" type must be "object".')
        object_properties: Dict[str, Any] = object_schema.get("properties", {})
        object_required: List[str] = object_schema.get("required", [])
        if not isinstance(object_properties, dict):
            raise ValueError(f'Nested schema "{name}" "properties" must be a dictionary if present.')
        if not isinstance(object_required, list):
            raise ValueError(f'Nested schema "{name}" "required" must be a list if present.')
        fields: Dict[str, Tuple[Any, Any]] = {}
        for prop_name, prop_schema in object_properties.items():
            is_required = prop_name in object_required
            field_type, default = parse_optional_schema_field(prop_schema, is_required, prop_name, name)
            fields[prop_name] = (field_type, default)
        return create_model(name, **fields)  # type: ignore

    model: Type[BaseModel] = _create_model_from_schema(schema, model_name)
    return model


=== File: recipe_executor/utils/templates.py ===
from typing import Any

import liquid
from liquid.exceptions import LiquidError

from recipe_executor.protocols import ContextProtocol


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
    context_dict: dict[str, Any] = context.dict()
    try:
        template = liquid.Template(text)
        return template.render(**context_dict)
    except LiquidError as exc:
        raise ValueError(f"Template rendering failed: {exc}\nTemplate: {text!r}\nContext: {context_dict!r}") from exc
    except Exception as exc:
        raise ValueError(
            f"Unknown error during template rendering: {exc}\nTemplate: {text!r}\nContext: {context_dict!r}"
        ) from exc


