=== File: .env.example ===
# Optional for the project
#LOG_LEVEL=DEBUG

# Required for the project
OPENAI_API_KEY=

# Additional APIs
#ANTHROPIC_API_KEY=
#GEMINI_API_KEY=

# Azure OpenAI
#AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_USE_MANAGED_IDENTITY=false
#AZURE_OPENAI_API_KEY=

#(Optional) The client ID of the specific managed identity to use.
#  If not provided, DefaultAzureCredential will be used.
#AZURE_MANAGED_IDENTITY_CLIENT_ID=


=== File: README.md ===
# Recipe Executor

A tool for executing recipe-like natural language instructions to generate and manipulate code and other files.

## Overview

The Recipe Executor is a flexible orchestration system that executes "recipes" - JSON-based definitions of sequential steps to perform tasks such as file reading, LLM-based content generation, and file writing. This project allows you to define complex workflows through simple recipe files.

## Key Components

- **Recipe Format**: JSON-based recipe definitions with steps
- **Step Types**: Various operations including file reading/writing, LLM generation, and sub-recipe execution
- **Context System**: Shared state for passing data between steps
- **Template Rendering**: Liquid templates for dynamic content generation

## Setup and Installation

### Prerequisites

Recommended installers:

- Linux: apt or your distribution's package manager
- macOS: [brew](https://brew.sh/)
- Windows: [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

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
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```
5. Test the installation by running the example recipe:
   ```bash
   make recipe-executor-create
   ```

## Using the Makefile

The project includes several useful make commands:

- **`make`**: Sets up the virtual environment and installs all dependencies
- **`make recipe-executor-context`**: Builds AI context files for recipe executor development
- **`make recipe-executor-create`**: Generates recipe executor code from scratch using the recipe itself
- **`make recipe-executor-edit`**: Revises existing recipe executor code using recipes

## Running Recipes

Execute a recipe using the command line interface:

```bash
python recipe_executor/main.py path/to/your/recipe.json
```

You can also pass context variables:

```bash
python recipe_executor/main.py path/to/your/recipe.json --context key=value
```

## Project Structure

The project contains:

- **`recipe_executor/`**: Core implementation with modules for execution, context management, and steps
- **`recipes/`**: Recipe definition files that can be executed

## Building from Recipes

One of the most interesting aspects of this project is that it can generate its own code using recipes:

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
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "azure-identity>=1.21.0",
    "dotenv>=0.9.9",
    "pydantic-ai>=0.0.55",
    "pydantic-settings>=2.8.1",
    "python-dotenv>=1.1.0",
    "python-liquid>=2.0.1",
]

[dependency-groups]
dev = [
    "pyright>=1.1.389",
    "pytest>=8.3.5",
    "pytest-cov>=6.1.1",
    "pytest-mock>=3.14.0",
    "ruff>=0.11.2",
]

[tool.uv]
package = true

[project.scripts]
recipe-executor = "recipe_executor.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["recipe_executor"]


=== File: recipe_executor/context.py ===
import copy
from typing import Any, Dict, Iterator, Optional

from recipe_executor.protocols import ContextProtocol


class Context(ContextProtocol):
    """
    Context is the shared state container for the Recipe Executor system.
    It maintains a store for artifacts (dynamic data) and a separate store for configuration values.

    Artifacts are accessed via a dictionary-like interface.
    Configuration can be accessed through the 'config' attribute.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize a new Context instance with optional artifacts and configuration.
        Both artifacts and configuration dictionaries are deep-copied to avoid side effects.

        Args:
            artifacts: Optional initial artifacts (dynamic data).
            config: Optional configuration values.
        """
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        """
        Retrieve the artifact associated with the given key.

        Args:
            key: The key to look up in the artifacts store.

        Returns:
            The artifact corresponding to the key.

        Raises:
            KeyError: If the key is not found in the artifacts store.
        """
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set the artifact for the given key to the specified value.

        Args:
            key: The key to set in the artifacts store.
            value: The value to associate with the key.
        """
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        """
        Delete the artifact associated with the given key.

        Args:
            key: The key to delete from the artifacts store.

        Raises:
            KeyError: If the key is not found in the artifacts store.
        """
        if key in self._artifacts:
            del self._artifacts[key]
        else:
            raise KeyError(f"Key '{key}' not found in Context.")

    def __contains__(self, key: object) -> bool:
        """
        Check if a key exists in the artifacts store.

        Args:
            key: The key to check for existence.

        Returns:
            True if the key exists, False otherwise.
        """
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over the keys of the artifacts store.
        A static snapshot of keys is returned to avoid issues with concurrent modifications.

        Returns:
            An iterator over the keys of the artifacts store.
        """
        # Return a snapshot copy of keys
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        """
        Return the number of artifacts stored in the context.

        Returns:
            The count of artifacts.
        """
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the keys of the artifacts store.

        Returns:
            An iterator over the keys (snapshot) of the artifacts store.
        """
        return iter(list(self._artifacts.keys()))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the artifact for the given key, returning a default if the key is not present.

        Args:
            key: The key to retrieve.
            default: The default value to return if key is missing.

        Returns:
            The artifact value if found, or the default value.
        """
        return self._artifacts.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts store as a regular dictionary.

        Returns:
            A deep copy of all artifacts stored in the context.
        """
        return copy.deepcopy(self._artifacts)

    def clone(self) -> ContextProtocol:
        """
        Create a deep copy of the entire Context, including both artifacts and configuration.
        This clone is completely independent of the original.

        Returns:
            A new Context instance with deep-copied artifacts and configuration.
        """
        return Context(artifacts=copy.deepcopy(self._artifacts), config=copy.deepcopy(self.config))


=== File: recipe_executor/executor.py ===
import os
import json
import logging
from typing import Any, Dict, Union, Optional

from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """Executor implements the ExecutorProtocol interface.

    It loads a recipe from a file path, raw JSON, or pre-parsed dictionary, validates it, and sequentially executes its steps
    using a shared context. Any errors during execution are raised as ValueError with context about which step failed.
    """

    async def execute(self, recipe: Union[str, Dict[str, Any]], context: ContextProtocol, 
                      logger: Optional[logging.Logger] = None) -> None:
        
        # Setup logger if not provided
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        logger.debug("Starting recipe execution.")
        
        # Load or parse recipe into a dictionary form
        recipe_dict: Dict[str, Any]

        # if recipe is already a dictionary, use it directly
        if isinstance(recipe, dict):
            recipe_dict = recipe
            logger.debug("Loaded recipe from pre-parsed dictionary.")

        # if recipe is a string, determine if it is a file path or a raw JSON string
        elif isinstance(recipe, str):
            if os.path.exists(recipe):
                try:
                    with open(recipe, 'r', encoding='utf-8') as file:
                        recipe_dict = json.load(file)
                    logger.debug(f"Loaded recipe from file path: {recipe}")
                except Exception as e:
                    logger.error(f"Failed reading or parsing the recipe file: {recipe}. Error: {e}")
                    raise ValueError(f"Failed to load recipe from file: {recipe}. Error: {e}") from e
            else:
                try:
                    recipe_dict = json.loads(recipe)
                    logger.debug("Loaded recipe from raw JSON string.")
                except Exception as e:
                    logger.error(f"Failed parsing the recipe JSON string. Error: {e}")
                    raise ValueError(f"Invalid JSON recipe string. Error: {e}") from e
        else:
            raise TypeError(f"Recipe must be a dict or str, got {type(recipe)}")

        # Validate that recipe_dict is indeed a dict
        if not isinstance(recipe_dict, dict):
            logger.error("The loaded recipe is not a dictionary.")
            raise ValueError("The recipe must be a dictionary.")
        
        # Validate that there is a 'steps' key mapping to a list
        steps = recipe_dict.get("steps")
        if not isinstance(steps, list):
            logger.error("Recipe must contain a 'steps' key mapping to a list.")
            raise ValueError("Recipe must contain a 'steps' key mapping to a list.")
        
        logger.debug(f"Recipe loaded with {len(steps)} steps.")

        # Sequentially execute each step
        for index, step in enumerate(steps):
            logger.debug(f"Processing step {index}: {step}")
            
            # Validate that each step is a dictionary and contains a 'type' key
            if not isinstance(step, dict):
                logger.error(f"Step at index {index} is not a dictionary.")
                raise ValueError(f"Each step must be a dictionary. Invalid step at index {index}.")
            
            step_type = step.get("type")
            if not step_type:
                logger.error(f"Step at index {index} missing 'type' key.")
                raise ValueError(f"Each step must have a 'type' key. Missing in step at index {index}.")
            
            # Retrieve the step class from STEP_REGISTRY
            step_class = STEP_REGISTRY.get(step_type)
            if step_class is None:
                logger.error(f"Unknown step type '{step_type}' at index {index}.")
                raise ValueError(f"Unknown step type '{step_type}' at index {index}.")
            
            try:
                logger.debug(f"Instantiating step {index} of type '{step_type}'.")
                step_instance = step_class(step, logger)
                logger.debug(f"Executing step {index} of type '{step_type}'.")
                await step_instance.execute(context)
                logger.debug(f"Finished executing step {index} of type '{step_type}'.")
            except Exception as e:
                logger.error(f"Step {index} (type: '{step_type}') failed. Error: {e}")
                raise ValueError(f"Step {index} (type: '{step_type}') failed to execute: {e}") from e
        
        logger.debug("All steps executed successfully.")


=== File: recipe_executor/llm_utils/azure_openai.py ===
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


=== File: recipe_executor/llm_utils/llm.py ===
import logging
import os
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# Import model classes from pydantic_ai
from pydantic_ai.models.openai import OpenAIModel

from recipe_executor.models import FileGenerationResult


def get_model(model_id: Optional[str] = None):
    """
    Initialize and return an LLM model instance based on a standardized model identifier.
    Expected formats:
      - provider/model_name
      - provider/model_name/deployment_name  (for Azure OpenAI)
    Supported providers:
      - openai
      - azure (for Azure OpenAI models)
      - anthropic
      - ollama
      - gemini

    Args:
        model_id (Optional[str]): Model identifier. If None, defaults to environment variable DEFAULT_MODEL or 'openai/gpt-4o'.

    Returns:
        An instance of the corresponding model class from pydantic_ai.

    Raises:
        ValueError: If the model_id is invalid or if the provider is unsupported.
    """
    if not model_id:
        model_id = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
    parts = model_id.split("/")
    if len(parts) < 2:
        raise ValueError(
            "Invalid model id. Expected format 'provider/model_name' or 'provider/model_name/deployment_name'."
        )
    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "azure":
        # For Azure, if a third part is provided, it's the deployment name; otherwise, default to model_name
        from recipe_executor.llm_utils.azure_openai import get_azure_openai_model

        deployment_name = parts[2] if len(parts) >= 3 else model_name
        return get_azure_openai_model(model_name, deployment_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "ollama":
        # Ollama uses OpenAIModel with a custom provider; the endpoint is taken from OLLAMA_ENDPOINT env.
        from pydantic_ai.providers.openai import OpenAIProvider

        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        return OpenAIModel(model_name, provider=OpenAIProvider(base_url=f"{ollama_endpoint}/v1"))
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def call_llm(
    prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (Optional[str]): Model identifier in the format 'provider/model_name' or 'provider/model_name/deployment_name'. If None, defaults to 'openai/gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance. Defaults to a logger named 'RecipeExecutor'.

    Returns:
        FileGenerationResult: The structured result from the LLM containing generated files and optional commentary.

    Raises:
        Exception: Propagates any exceptions that occur during the LLM call.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    try:
        model_instance = get_model(model)
    except Exception as e:
        logger.error(f"Error initializing model: {e}")
        raise

    # Log info about model usage
    provider_name = model.split("/")[0] if model else "openai"
    model_name = model.split("/")[1] if model else "gpt-4o"
    logger.info(f"Calling LLM with provider='{provider_name}', model_name='{model_name}'")

    # Log debug payload
    logger.debug(f"LLM Request Payload: {prompt}")

    # Initialize the Agent with the model instance and specify the structured output type
    agent = Agent(model_instance, result_type=FileGenerationResult)

    # Make the asynchronous call
    result = await agent.run(prompt)

    # Log response and usage
    logger.debug(f"LLM Response Payload: {result.data}")
    logger.info(f"LLM call completed. Usage details: {result.usage()}")

    return result.data


=== File: recipe_executor/logger.py ===
import logging
import os
import sys
from typing import Optional


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
    # Create log directory if it doesn’t exist
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        error_message = f"Failed to create log directory '{log_dir}': {e}"
        print(error_message, file=sys.stderr)
        raise Exception(error_message) from e

    # Create or get the logger for RecipeExecutor
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Capture all messages
    logger.propagate = False  # Avoid duplicate logs if root logger is configured

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define log format
    log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # File handler for DEBUG level (all messages)
    try:
        debug_handler = logging.FileHandler(os.path.join(log_dir, "debug.log"), mode='w')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(log_format)
        logger.addHandler(debug_handler)
    except Exception as e:
        error_message = f"Failed to create debug log file: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

    # File handler for INFO level and above
    try:
        info_handler = logging.FileHandler(os.path.join(log_dir, "info.log"), mode='w')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(log_format)
        logger.addHandler(info_handler)
    except Exception as e:
        error_message = f"Failed to create info log file: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

    # File handler for ERROR level and above
    try:
        error_handler = logging.FileHandler(os.path.join(log_dir, "error.log"), mode='w')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(log_format)
        logger.addHandler(error_handler)
    except Exception as e:
        error_message = f"Failed to create error log file: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

    # Console handler for INFO level and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Log debug message indicating initialization
    logger.debug("Initializing RecipeExecutor logger with log directory: '%s'", log_dir)

    return logger


=== File: recipe_executor/main.py ===
import argparse
import asyncio
import sys
import time
import traceback

from dotenv import load_dotenv

from recipe_executor.logger import init_logger
from recipe_executor.context import Context
from recipe_executor.executor import Executor


def parse_context(context_args: list[str]) -> dict[str, str]:
    """Parse a list of context key=value strings into a dictionary."""
    context_data: dict[str, str] = {}
    for item in context_args:
        if '=' not in item:
            raise ValueError(f"Invalid context format: '{item}'. Expected format is key=value.")
        key, value = item.split('=', 1)
        context_data[key] = value
    return context_data


async def main_async() -> None:
    # Load environment variables from .env file
    load_dotenv()

    # Setup argument parsing
    parser = argparse.ArgumentParser(description="Recipe Executor Tool")
    parser.add_argument("recipe_path", help="Path to the recipe file to execute")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", default=[], help="Context key=value pairs. Can be repeated.")

    args = parser.parse_args()

    # Parse context values
    try:
        context_data = parse_context(args.context)
    except ValueError as ve:
        sys.stderr.write(f"Context Error: {ve}\n")
        sys.exit(1)

    # Initialize logger
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger initialization failed: {e}\n")
        sys.exit(1)

    logger.info("Starting Recipe Executor Tool")
    logger.debug(f"Parsed arguments: {args}")
    logger.debug(f"Initial context data: {context_data}")

    # Create Context and Executor instances
    context = Context(artifacts=context_data)  
    executor = Executor()

    start_time = time.time()
    try:
        logger.info(f"Executing recipe: {args.recipe_path}")
        # Await the execution of the recipe
        await executor.execute(args.recipe_path, context, logger=logger)
        elapsed = time.time() - start_time
        logger.info(f"Recipe executed successfully in {elapsed:.2f} seconds")
    except Exception as e:
        error_message = f"An error occurred during recipe execution: {e}"
        logger.error(error_message, exc_info=True)
        sys.stderr.write(f"{error_message}\n{traceback.format_exc()}\n")
        sys.exit(1)


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        sys.stderr.write("Execution interrupted by user.\n")
        sys.exit(1)


if __name__ == '__main__':
    main()


=== File: recipe_executor/models.py ===
from typing import List, Dict, Optional
from pydantic import BaseModel


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """

    path: str
    content: str


class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """

    files: List[FileSpec]
    commentary: Optional[str] = None


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """

    type: str
    config: Dict


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]


=== File: recipe_executor/protocols.py ===
from typing import Protocol, runtime_checkable, Any, Optional, Iterator, Dict, Union
import logging


@runtime_checkable
class ContextProtocol(Protocol):
    """Interface for context objects holding shared state with dictionary-like access."""

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def as_dict(self) -> Dict[str, Any]:
        """Return a copy of the internal state as a dictionary."""
        ...

    def clone(self) -> 'ContextProtocol':
        """Return a deep copy of the context."""
        ...


@runtime_checkable
class StepProtocol(Protocol):
    """Interface for executable steps in the recipe."""

    async def execute(self, context: ContextProtocol) -> None:
        """Execute the step using the provided context."""
        ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    """Interface for recipe executors that run recipes using a given context and optional logger."""

    async def execute(
        self,
        recipe: Union[str, Dict[str, Any]],
        context: ContextProtocol,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Execute a recipe represented as a file path, JSON string, or dictionary using the context.

        Raises:
            Exception: When execution fails.
        """
        ...


=== File: recipe_executor/steps/__init__.py ===
from recipe_executor.steps.registry import STEP_REGISTRY

from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register steps in the global registry
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})

__all__ = [
    "STEP_REGISTRY",
    "ExecuteRecipeStep",
    "GenerateWithLLMStep",
    "ParallelStep",
    "ReadFilesStep",
    "WriteFilesStep",
]


=== File: recipe_executor/steps/base.py ===
import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

# Import the ContextProtocol from the protocols component
from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for step implementations.

    This class is intentionally left minimal and should be extended by concrete step configurations.
    """
    pass


# Create a type variable that must be a subclass of StepConfig
ConfigType = TypeVar('ConfigType', bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """
    Abstract base class for all steps in the Recipe Executor system.

    Attributes:
        config (ConfigType): The configuration instance for the step.
        logger (logging.Logger): Logger to record operations, defaults to a module logger named 'RecipeExecutor'.
    """
    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger: logging.Logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"{self.__class__.__name__} initialized with config: {self.config}")

    @abstractmethod
    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step with the provided context.

        Args:
            context (ContextProtocol): Execution context conforming to the ContextProtocol interface.

        Raises:
            NotImplementedError: If a subclass does not implement the execute method.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")


=== File: recipe_executor/steps/execute_recipe.py ===
import logging
import os
from typing import Any, Dict, Optional, Union

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, str] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    def __init__(
        self, config: Union[Dict[str, Any], ExecuteRecipeConfig], logger: Optional[logging.Logger] = None
    ) -> None:
        # Ensure config is an ExecuteRecipeConfig object, not a raw dict
        if not isinstance(config, ExecuteRecipeConfig):
            config = ExecuteRecipeConfig(**config)
        super().__init__(config, logger)

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute a sub-recipe by rendering its path and applying any context overrides.

        Args:
            context (ContextProtocol): The shared execution context.

        Raises:
            ValueError: If the sub-recipe file does not exist.
            RuntimeError: If an error occurs during sub-recipe execution.
        """
        # Import Executor within execute to avoid circular dependencies
        from recipe_executor.executor import Executor

        # Render the sub-recipe path template using the current context
        rendered_recipe_path = render_template(self.config.recipe_path, context)

        # Apply context overrides with template rendering
        for key, value in self.config.context_overrides.items():
            rendered_value = render_template(value, context)
            context[key] = rendered_value

        # Validate that the sub-recipe file exists
        if not os.path.isfile(rendered_recipe_path):
            error_message = f"Sub-recipe file not found: {rendered_recipe_path}"
            self.logger.error(error_message)
            raise ValueError(error_message)

        self.logger.info(f"Starting sub-recipe execution: {rendered_recipe_path}")

        try:
            executor = Executor()
            # The executor uses the same context which may be updated by the sub-recipe
            await executor.execute(rendered_recipe_path, context)
        except Exception as exc:
            error_message = f"Error executing sub-recipe '{rendered_recipe_path}': {str(exc)}"
            self.logger.error(error_message)
            raise RuntimeError(error_message) from exc

        self.logger.info(f"Completed sub-recipe execution: {rendered_recipe_path}")


=== File: recipe_executor/steps/generate_llm.py ===
import logging
from typing import Optional

from recipe_executor.llm_utils.llm import call_llm
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    GenerateWithLLMStep enables recipes to generate content using large language models (LLMs).
    It processes prompt templates using context data, handles model selection, makes LLM calls,
    and stores the generated result in the execution context under a dynamic artifact key.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger or logging.getLogger(__name__))

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the LLM generation step:
          1. Render the prompt using context data.
          2. Render the model identifier using context data.
          3. Log a debug message with call details.
          4. Call the LLM with the rendered prompt and model.
          5. Render the artifact key using context data and store the response.

        Args:
            context (ContextProtocol): Execution context implementing artifact storage.

        Raises:
            Exception: Propagates any exceptions from the LLM call for upstream handling.
        """
        rendered_prompt = ""  # Initialize before try block to avoid "possibly unbound" error
        try:
            # Render prompt, model, and artifact key using the provided context
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model: str = render_template(self.config.model, context)
            artifact_key: str = render_template(self.config.artifact, context)

            # Log debug message about the LLM call details
            self.logger.debug(f"Calling LLM with prompt: {rendered_prompt[:50]}... and model: {rendered_model}")

            # Call the LLM asynchronously
            response = await call_llm(prompt=rendered_prompt, model=rendered_model, logger=self.logger)

            # Store the generated result in the execution context
            context[artifact_key] = response

        except Exception as error:
            self.logger.error(f"LLM call failed for prompt: {rendered_prompt[:50]}... with error: {error}")
            raise


=== File: recipe_executor/steps/parallel.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Attributes:
        substeps: List of sub-step configurations to execute in parallel.
                   Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc.).
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default of 0 means no explicit limit (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay (all allowed substeps start immediately).
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """ParallelStep enables the execution of multiple sub-steps concurrently.

    Each sub-step runs in its own cloned context to ensure isolation. Execution is controlled
    using asyncio concurrency primitives, with configurable concurrency and launch delays.
    Fail-fast behavior is implemented: if any sub-step fails, pending steps are cancelled and
    the error is propagated.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Parse config using the ParallelConfig model
        super().__init__(ParallelConfig(**config), logger)

    async def execute(self, context: ContextProtocol) -> None:
        self.logger.info(f"Starting ParallelStep with {len(self.config.substeps)} substeps")

        # Set up concurrency control
        semaphore: Optional[asyncio.Semaphore] = None
        if self.config.max_concurrency > 0:
            semaphore = asyncio.Semaphore(self.config.max_concurrency)
            self.logger.debug(f"Max concurrency set to {self.config.max_concurrency}")
        else:
            self.logger.debug("No max concurrency limit set; running all substeps concurrently")

        tasks: List[asyncio.Task] = []

        async def run_substep(sub_config: Dict[str, Any], sub_context: ContextProtocol, index: int) -> None:
            try:
                self.logger.debug(f"Starting substep {index} with config: {sub_config}")
                # Lookup the step type from the registry
                step_type = sub_config.get("type")
                if step_type not in STEP_REGISTRY:
                    raise ValueError(f"Substep {index}: Unknown step type '{step_type}'")

                # Instantiate the substep using the registered step class
                step_class = STEP_REGISTRY[step_type]
                substep_instance = step_class(config=sub_config, logger=self.logger)

                # Execute the substep with its own cloned context
                await substep_instance.execute(sub_context)
                self.logger.debug(f"Substep {index} completed successfully")
            except Exception as e:
                self.logger.error(f"Substep {index} failed: {e}")
                raise

        async def run_substep_with_control(sub_config: Dict[str, Any], index: int) -> None:
            # Each substep gets its own cloned context for isolation
            cloned_context = context.clone()
            if semaphore is not None:
                async with semaphore:
                    await run_substep(sub_config, cloned_context, index)
            else:
                await run_substep(sub_config, cloned_context, index)

        # Launch substeps sequentially respecting the optional delay between launches
        for index, sub_config in enumerate(self.config.substeps):
            if index > 0 and self.config.delay > 0:
                self.logger.debug(f"Delaying launch of substep {index} by {self.config.delay} seconds")
                await asyncio.sleep(self.config.delay)

            task = asyncio.create_task(run_substep_with_control(sub_config, index))
            tasks.append(task)

        # Wait for all substeps to complete with fail-fast behavior
        try:
            # Wait until all tasks complete or one fails
            results = await asyncio.gather(*tasks)
            self.logger.info(f"ParallelStep completed all {len(tasks)} substeps successfully")
        except Exception as e:
            self.logger.error("ParallelStep encountered an error; cancelling remaining substeps")
            # Cancel all pending tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            # Optionally wait for cancellation to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            raise e


=== File: recipe_executor/steps/read_files.py ===
import os
import logging
from typing import Any, List, Union, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + contents
            - "dict": Store a dictionary with filenames as keys and contents as values
    """

    path: Union[str, List[str]]
    artifact: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    ReadFilesStep reads one or more files from the filesystem, processes templated paths, and stores their content
    in the execution context under the specified artifact key. It supports single or multiple file reads and
    flexible content merging options.
    """
    
    def __init__(self, config: Any, logger: Optional[logging.Logger] = None) -> None:
        # Ensure config is a ReadFilesConfig object, not a raw dict
        if not isinstance(config, ReadFilesConfig):
            config = ReadFilesConfig(**config)
        super().__init__(config, logger)
    
    async def execute(self, context: ContextProtocol) -> None:
        # Resolve the raw paths from configuration
        raw_paths: Union[str, List[str]] = self.config.path
        file_paths: List[str] = []

        if isinstance(raw_paths, list):
            file_paths = raw_paths
        elif isinstance(raw_paths, str):
            if "," in raw_paths:
                file_paths = [p.strip() for p in raw_paths.split(",") if p.strip()]
            else:
                file_paths = [raw_paths.strip()]
        else:
            raise ValueError(f"Unsupported type for path: {type(raw_paths)}")

        # Render template for each path
        rendered_paths: List[str] = []
        for path in file_paths:
            try:
                rendered = render_template(path, context)
                rendered_paths.append(rendered)
                self.logger.debug(f"Rendered path: '{path}' to '{rendered}'")
            except Exception as e:
                self.logger.error(f"Error rendering template for path '{path}': {e}")
                raise

        # Initialize storage based on merge_mode
        merge_mode = self.config.merge_mode.lower()
        # For single file, even with concat mode, we return a string for backward compatibility
        is_single = len(rendered_paths) == 1

        # Initialize both storage variables to avoid "possibly unbound" errors
        aggregated_result: dict = {}
        aggregated_result_list: List[str] = []
        final_content: Any = None

        # Validate merge_mode
        if merge_mode not in ["dict", "concat"]:
            raise ValueError(f"Unsupported merge_mode: {self.config.merge_mode}")

        # Iterate over each rendered file path and read the contents
        for rendered_path in rendered_paths:
            self.logger.debug(f"Attempting to read file: {rendered_path}")
            if not os.path.exists(rendered_path):
                msg = f"File not found: {rendered_path}"
                if self.config.optional:
                    self.logger.warning(msg + " (optional file, continuing)")
                    if merge_mode == "dict":
                        # Use empty string for missing optional file
                        key = os.path.basename(rendered_path)
                        aggregated_result[key] = ""
                    elif merge_mode == "concat":
                        # For single file, assign empty string; for multiple files, skip missing file
                        if is_single:
                            aggregated_result_list.append("")
                        else:
                            self.logger.debug(f"Skipping missing optional file: {rendered_path}")
                    continue
                else:
                    self.logger.error(msg)
                    raise FileNotFoundError(msg)

            try:
                with open(rendered_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.logger.info(f"Successfully read file: {rendered_path}")
            except Exception as e:
                self.logger.error(f"Error reading file {rendered_path}: {e}")
                raise

            if merge_mode == "dict":
                key = os.path.basename(rendered_path)
                aggregated_result[key] = content
            elif merge_mode == "concat":
                # For multiple files, include a header with the filename
                if is_single:
                    aggregated_result_list.append(content)
                else:
                    header = f"File: {os.path.basename(rendered_path)}"
                    aggregated_result_list.append(f"{header}\n{content}")

        # Finalize artifact based on merge_mode
        if merge_mode == "dict":
            final_content: Any = aggregated_result
        elif merge_mode == "concat":
            if is_single:
                final_content = aggregated_result_list[0] if aggregated_result_list else ""
            else:
                final_content = "\n\n".join(aggregated_result_list)

        # Store the result in context under the specified artifact key
        context[self.config.artifact] = final_content
        self.logger.info(f"Stored file content under context key '{self.config.artifact}'")


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global registry mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import os
from typing import List, Union

from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        artifact: Name of the context key holding a FileGenerationResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """
    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, config: dict, logger=None) -> None:
        super().__init__(WriteFilesConfig(**config), logger)

    async def execute(self, context: ContextProtocol) -> None:
        # Retrieve the artifact from the context
        artifact_key = self.config.artifact
        artifact_value = context.get(artifact_key)
        if artifact_value is None:
            self.logger.error(f"Artifact '{artifact_key}' not found in context")
            raise KeyError(f"Artifact '{artifact_key}' not found in context")

        files_list: List[FileSpec] = []

        # Determine if artifact_value is FileGenerationResult or a list of FileSpec
        if hasattr(artifact_value, 'files'):
            # Assume artifact_value is FileGenerationResult
            files_list = artifact_value.files
        elif isinstance(artifact_value, list):
            # Validate each element in the list is a FileSpec
            files_list = artifact_value
        else:
            message = "Artifact does not hold a valid FileGenerationResult or list of FileSpec objects."
            self.logger.error(message)
            raise ValueError(message)

        # Render the root path using the context, supports template variables
        rendered_root = render_template(self.config.root, context)

        # Write each file
        for file_spec in files_list:
            # Render the dynamic file path
            rendered_file_path = render_template(file_spec.path, context)
            # Combine the rendered root and file path
            full_path = os.path.join(rendered_root, rendered_file_path)
            
            # Ensure the parent directories exist
            directory = os.path.dirname(full_path)
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                self.logger.error(f"Failed to create directories for path {directory}: {str(e)}")
                raise

            # Log debug information with file path and content length
            self.logger.debug(f"Preparing to write file: {full_path}\nContent:\n{file_spec.content}")
            
            try:
                with open(full_path, 'w', encoding='utf-8') as file_handle:
                    file_handle.write(file_spec.content)
                self.logger.info(f"Successfully wrote file: {full_path} (size: {len(file_spec.content)} bytes)")
            except Exception as e:
                self.logger.error(f"Failed writing file {full_path}: {str(e)}")
                raise


=== File: recipe_executor/utils.py ===
import logging

import liquid

from recipe_executor.protocols import ContextProtocol


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    logger = logging.getLogger(__name__)

    # Convert all context values to strings to prevent type errors
    try:
        context_dict = context.as_dict()
    except Exception as conv_error:
        error_message = f"Failed to extract context data: {conv_error}"
        logger.error(error_message)
        raise ValueError(error_message) from conv_error

    template_context = {key: str(value) for key, value in context_dict.items()}

    # Log the template text and the context keys being used
    logger.debug("Rendering template: %s", text)
    logger.debug("Context keys: %s", list(template_context.keys()))

    try:
        # Create a Liquid template, then render with the provided context
        tpl = liquid.Template(text)
        rendered_text = tpl.render(**template_context)
        return rendered_text
    except Exception as e:
        error_message = f"Error rendering template. Template: {text}. Error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message) from e


