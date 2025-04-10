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
    "pydantic-ai>=0.0.46",
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
    Context component for Recipe Executor system.

    Maintains a store for artifacts and configuration values, and provides a dictionary-like interface
    for accessing and modifying artifacts. Configuration is stored separately in a 'config' attribute.

    Example usage:

        context = Context(artifacts={"input": "data"}, config={"mode": "test"})
        context["result"] = 42
        value = context["result"]
        if "result" in context:
            print(context["result"])

    The clone() method creates a deep copy of both artifacts and configuration, ensuring isolation when needed.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        # Deep copy to ensure caller modifications do not affect internal state
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self._artifacts:
            del self._artifacts[key]
        else:
            raise KeyError(f"Key '{key}' not found in Context.")

    def __contains__(self, key: object) -> bool:
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Return an iterator over a snapshot of the keys
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        """
        Return an iterator of keys in the artifacts store.
        """
        return iter(list(self._artifacts.keys()))

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._artifacts.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts as a dictionary.
        """
        return copy.deepcopy(self._artifacts)

    def clone(self) -> ContextProtocol:
        """
        Create a deep copy of the Context including both artifacts and configuration.
        """
        return Context(artifacts=copy.deepcopy(self._artifacts), config=copy.deepcopy(self.config))


__all__ = ["Context"]


=== File: recipe_executor/executor.py ===
import json
import logging
import os
from typing import Any, Dict, Optional, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """Executor component that loads and sequentially executes recipe steps."""

    def execute(
        self, recipe: Union[str, Dict[str, Any]], context: ContextProtocol, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Execute a recipe on the provided context.

        The recipe parameter can be one of:
          - A file path to a JSON recipe file.
          - A raw JSON string representing the recipe.
          - A dictionary representing the recipe.

        :param recipe: Recipe to execute in string (file path or JSON) or dict format.
        :param context: The shared context object implementing ContextProtocol.
        :param logger: Optional logger. If None, a default logger is configured.
        :raises ValueError: If recipe structure is invalid or a step fails.
        :raises TypeError: If recipe type is not supported.
        """
        # Setup logger if not provided
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.hasHandlers():
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        # Load recipe into dictionary form
        recipe_obj: Dict[str, Any]
        if isinstance(recipe, dict):
            recipe_obj = recipe
            logger.debug("Received recipe as dictionary.")
        elif isinstance(recipe, str):
            # First check if it's a valid file path
            if os.path.exists(recipe) and os.path.isfile(recipe):
                try:
                    with open(recipe, "r") as file:
                        recipe_obj = json.load(file)
                    logger.debug(f"Loaded recipe from file: {recipe}")
                except Exception as file_error:
                    logger.error(f"Failed to load recipe file '{recipe}': {file_error}")
                    raise ValueError(f"Error reading recipe file: {file_error}")
            else:
                try:
                    recipe_obj = json.loads(recipe)
                    logger.debug("Loaded recipe from JSON string.")
                except json.JSONDecodeError as json_error:
                    logger.error(f"Invalid JSON recipe string: {json_error}")
                    raise ValueError(f"Invalid JSON recipe string: {json_error}")
        else:
            raise TypeError("Recipe must be a dict or a str representing a JSON recipe or file path.")

        # Validate recipe structure
        if not isinstance(recipe_obj, dict):
            raise ValueError("Recipe format invalid: expected a dictionary at the top level.")

        if "steps" not in recipe_obj or not isinstance(recipe_obj["steps"], list):
            raise ValueError("Recipe must contain a 'steps' key mapping to a list.")

        steps = recipe_obj["steps"]
        logger.debug(f"Recipe contains {len(steps)} step(s).")

        # Execute steps sequentially
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step at index {index} is not a valid dictionary.")

            if "type" not in step:
                raise ValueError(f"Step at index {index} is missing the 'type' field.")

            step_type = step["type"]
            logger.debug(f"Preparing to execute step {index}: type='{step_type}', details={step}.")

            # Look up step class in STEP_REGISTRY
            if step_type not in STEP_REGISTRY:
                logger.error(f"Unknown step type '{step_type}' at index {index}.")
                raise ValueError(f"Unknown step type '{step_type}' encountered at step index {index}.")

            step_class = STEP_REGISTRY[step_type]
            try:
                # Instantiate the step - assume the step class takes the step configuration and a logger
                step_instance = step_class(step, logger)
                # Execute the step, passing in the shared context
                step_instance.execute(context)
                logger.debug(f"Step {index} ('{step_type}') executed successfully.")
            except Exception as e:
                logger.error(f"Execution failed for step {index} ('{step_type}'): {e}")
                raise ValueError(f"Step {index} with type '{step_type}' failed during execution.") from e

        logger.debug("All steps executed successfully.")


# Expose Executor through module API
__all__ = ["Executor"]


=== File: recipe_executor/llm_utils/azure_openai.py ===
import logging
import os
from typing import Optional

import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def _mask_api_key(api_key: str) -> str:
    """Return a masked version of the API key, showing only the first and last characters."""
    if len(api_key) <= 4:
        return api_key
    return api_key[0] + "*" * (len(api_key) - 2) + api_key[-1]


def get_openai_model(
    model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance configured to use Azure OpenAI.

    This function loads configuration from environment variables. It supports two authentication methods:
    - API key authentication using AZURE_OPENAI_API_KEY
    - Managed Identity authentication if AZURE_USE_MANAGED_IDENTITY is set

    Environment Variables:
    - AZURE_OPENAI_ENDPOINT: URL for the Azure OpenAI service (required)
    - AZURE_OPENAI_API_VERSION: API version (default: "2025-03-01-preview")
    - AZURE_OPENAI_DEPLOYMENT_NAME: Deployment name (optional, defaults to model_name if not provided)
    - AZURE_USE_MANAGED_IDENTITY: If set to true ("true", "1", or "yes"), uses Managed Identity authentication
    - AZURE_MANAGED_IDENTITY_CLIENT_ID: (Optional) Client ID for managed identity
    - AZURE_OPENAI_API_KEY: API key for Azure OpenAI (required if not using managed identity)

    Args:
        model_name (str): The name of the OpenAI model (e.g. "gpt-4o")
        deployment_name (Optional[str]): Optional deployment name; defaults to AZURE_OPENAI_DEPLOYMENT_NAME or model_name
        logger (Optional[logging.Logger]): Logger instance; if not provided, defaults to a logger named "RecipeExecutor"

    Returns:
        OpenAIModel: A configured instance of OpenAIModel using Azure OpenAI

    Raises:
        ValueError: If required environment variables are missing.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Load required environment variables
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise ValueError("Missing required environment variable: AZURE_OPENAI_ENDPOINT")

    azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    deployment = deployment_name or os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", model_name)

    logger.debug(f"Azure OpenAI Endpoint: {azure_endpoint}")
    logger.debug(f"Azure API Version: {azure_api_version}")
    logger.debug(f"Azure Deployment: {deployment}")

    use_managed_identity = os.environ.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("true", "1", "yes")

    if use_managed_identity:
        logger.info("Using Azure Managed Identity for authentication.")
        client_id = os.environ.get("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        if client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            credential = DefaultAzureCredential()
        scope = "https://cognitiveservices.azure.com/.default"
        token_provider = get_bearer_token_provider(credential, scope)

        azure_client = openai.AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version=azure_api_version,
            azure_deployment=deployment,
            azure_ad_token_provider=token_provider,
        )
    else:
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing required environment variable: AZURE_OPENAI_API_KEY when not using managed identity"
            )
        logger.info("Using Azure OpenAI API key for authentication.")
        masked_key = _mask_api_key(api_key)
        logger.debug(f"Azure API Key: {masked_key}")

        azure_client = openai.AsyncAzureOpenAI(
            api_key=api_key, azure_endpoint=azure_endpoint, api_version=azure_api_version, azure_deployment=deployment
        )

    provider = OpenAIProvider(openai_client=azure_client)
    model = OpenAIModel(model_name, provider=provider)

    logger.info(f"Azure OpenAI model '{model_name}' created successfully using deployment '{deployment}'.")
    return model


=== File: recipe_executor/llm_utils/llm.py ===
import logging
import os
from typing import Optional

# Import LLM model classes from pydantic_ai
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel

# Azure OpenAI support - this should be provided via an internal module
from recipe_executor.llm_utils.azure_openai import get_openai_model

# Import structured models from the recipe_executor models module
from recipe_executor.models import FileGenerationResult

# Default model identifier. Falls back to 'openai:gpt-4o' if no environment variable DEFAULT_MODEL is found.
DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL", "openai:gpt-4o")


def get_model(model_id: Optional[str] = None):
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected formats:
      - 'openai:model_name'
      - 'azure:model_name' or 'azure:model_name:deployment_name'
      - 'anthropic:model_name'
      - 'gemini:model_name'

    If model_id is None, defaults to DEFAULT_MODEL_ID.

    Returns:
      An instance of a model interface from pydantic_ai.

    Raises:
      ValueError if the model_id format is invalid or if the provider is unsupported.
    """
    if model_id is None:
        model_id = DEFAULT_MODEL_ID

    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model id format: {model_id}")

    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "azure":
        # For Azure, if a deployment name is provided, use it; otherwise default to model_name
        deployment_name = model_name
        if len(parts) == 3:
            deployment_name = parts[2]
        return get_openai_model(model_name, deployment_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model using a structured output type of FileGenerationResult.

    Args:
      model_id: Model identifier string in the format 'provider:model' or 'provider:model:deployment'.
                If None, defaults to DEFAULT_MODEL_ID.

    Returns:
      An Agent configured for processing file generation requests.
    """
    model = get_model(model_id)
    agent = Agent(model, result_type=FileGenerationResult)
    return agent


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
      prompt: The prompt string to send to the LLM.
      model: The model identifier in the form 'provider:model' (or for Azure, 'azure:model:deployment').
             If None, defaults to DEFAULT_MODEL_ID.
      logger: Logger instance to use; if None, defaults to a logger named "RecipeExecutor".

    Returns:
      FileGenerationResult: The structured result containing generated files and commentary.

    Raises:
      Exception: If the LLM call fails.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    try:
        # Log the full request payload at the debug level
        logger.debug(f"LLM Request - model: {model or DEFAULT_MODEL_ID}, prompt: {prompt}")

        # Log basic model and provider info at info level
        parts = (model or DEFAULT_MODEL_ID).split(":")
        provider = parts[0] if parts else "unknown"
        model_name = parts[1] if len(parts) > 1 else "unknown"
        logger.info(f"Calling LLM with provider: {provider}, model: {model_name}")

        agent = get_agent(model)

        result = agent.run_sync(prompt)

        # Log the full response payload at debug level, including messages
        logger.debug(f"LLM Response Messages: {result.all_messages()}")

        try:
            usage = result.usage()
            logger.info(f"LLM call completed. Usage: {usage}")
        except Exception:
            pass

        # CRITICAL: Return the result's data
        return result.data
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}", exc_info=True)
        raise


=== File: recipe_executor/logger.py ===
import logging
import os
import sys
from logging import Logger
from typing import Optional


def init_logger(log_dir: str = "logs") -> Logger:
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
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Reset any existing handlers to ensure consistent configuration
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create log directory if it does not exist, with error handling
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        # Log to stderr since file logging isn't configured yet
        error_message = f"Failed to create log directory '{log_dir}': {e}"
        sys.stderr.write(error_message + "\n")
        raise Exception(error_message)

    # Define a consistent log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Create File Handlers with mode 'w' to clear previous logs
    try:
        debug_file = os.path.join(log_dir, "debug.log")
        debug_handler = logging.FileHandler(debug_file, mode='w')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)

        info_file = os.path.join(log_dir, "info.log")
        info_handler = logging.FileHandler(info_file, mode='w')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        error_file = os.path.join(log_dir, "error.log")
        error_handler = logging.FileHandler(error_file, mode='w')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
    except Exception as e:
        error_message = f"Failed to set up log file handlers: {e}"
        sys.stderr.write(error_message + "\n")
        raise Exception(error_message)

    # Create console (stdout) handler with level INFO
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add all handlers to the logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    # Log debug message for initialization
    logger.debug("Initializing logger component")

    return logger


=== File: recipe_executor/main.py ===
import argparse
import sys
import time

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_context(context_list: list[str]) -> dict[str, str]:
    """
    Parses a list of context items in key=value format into a dictionary.

    Args:
        context_list (list[str]): List of context strings in key=value format.

    Returns:
        dict[str, str]: Parsed context dictionary.

    Raises:
        ValueError: If any context string is not in the key=value format.
    """
    context_data: dict[str, str] = {}
    for item in context_list:
        if "=" not in item:
            raise ValueError(f"Invalid context format '{item}'")
        key, value = item.split("=", 1)
        context_data[key] = value
    return context_data


def main() -> None:
    # Load environment variables from .env file if available
    load_dotenv()

    parser = argparse.ArgumentParser(description="Recipe Executor")
    parser.add_argument("recipe_path", type=str, help="Path to the recipe file")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory to store log files")
    parser.add_argument("--context", action="append", default=[], help="Context values in key=value format")
    args = parser.parse_args()

    try:
        context_artifacts = parse_context(args.context) if args.context else {}
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    try:
        logger = init_logger(args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: {str(e)}\n")
        sys.exit(1)

    logger.info("Starting Recipe Executor Tool")
    logger.debug(f"Parsed arguments: {args}")
    logger.debug(f"Initial context artifacts: {context_artifacts}")

    # Create Context and Executor instances
    context = Context(artifacts=context_artifacts)
    executor = Executor()

    start_time = time.time()

    try:
        logger.info(f"Executing recipe: {args.recipe_path}")
        executor.execute(args.recipe_path, context, logger=logger)
        duration = time.time() - start_time
        logger.info(f"Recipe executed successfully in {duration:.2f} seconds.")
        sys.exit(0)
    except Exception as e:
        logger.error("An error occurred during recipe execution:", exc_info=True)
        sys.stderr.write(f"Recipe execution failed: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
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
from typing import Any, Dict, Iterator, Optional, Protocol, Union, runtime_checkable
import logging


@runtime_checkable
class ContextProtocol(Protocol):
    """
    Defines the interface for context-like objects that hold shared state.
    It supports dictionary-like operations and additional utility methods.
    """

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __contains__(self, key: object) -> bool:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def keys(self) -> Iterator[str]:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def as_dict(self) -> Dict[str, Any]:
        ...

    def clone(self) -> 'ContextProtocol':
        """
        Returns a deep copy of the context.
        """
        ...


@runtime_checkable
class StepProtocol(Protocol):
    """
    Protocol for an executable step in a recipe.
    
    The step must implement the execute method which takes a context
    and performs its operations.
    """

    def execute(self, context: ContextProtocol) -> None:
        ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    """
    Protocol for recipe executors.
    
    The executor must be able to execute a recipe given in various formats (string, JSON string, or dict)
    using a provided context and an optional logger. It is expected to raise exceptions on errors.
    """

    def execute(
        self, 
        recipe: Union[str, Dict[str, Any]], 
        context: ContextProtocol, 
        logger: Optional[logging.Logger] = None
    ) -> None:
        ...


=== File: recipe_executor/steps/__init__.py ===
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.write_files import WriteFilesStep

__all__ = [
    'STEP_REGISTRY',
    'ExecuteRecipeStep',
    'GenerateWithLLMStep',
    'ParallelStep',
    'ReadFilesStep',
    'WriteFilesStep',
]

# Register steps by updating the global registry
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})


=== File: recipe_executor/steps/base.py ===
import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

# Assuming ContextProtocol is defined in recipe_executor.protocols
from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """Base configuration class for steps using Pydantic.

    This class serves as the foundation for step-specific configuration models.
    Concrete steps should subclass this to define their own configuration attributes.
    """
    pass


# Define a TypeVar for configuration types that extend StepConfig
ConfigType = TypeVar('ConfigType', bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """Abstract base class for all steps in the Recipe Executor system.

    This class defines the common interface and behavior for steps. Concrete steps must
    implement the execute method.
    """
    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        """Initialize the step with a given configuration and an optional logger.

        Args:
            config (ConfigType): The configuration for the step, validated using Pydantic.
            logger (Optional[logging.Logger]): An optional logger. If not provided, a default
                                                 logger named 'RecipeExecutor' is used.
        """
        self.config: ConfigType = config
        self.logger: logging.Logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"Initialized step {self.__class__.__name__} with config: {self.config}")

    @abstractmethod
    def execute(self, context: ContextProtocol) -> None:
        """Execute the step with the provided context.

        Concrete implementations must override this method to perform step-specific actions.
        
        Args:
            context (ContextProtocol): The execution context which allows interaction with the
                                         shared state of the recipe execution.
        
        Raises:
            NotImplementedError: If not overridden in a subclass.
        """
        raise NotImplementedError(f"The execute method is not implemented in {self.__class__.__name__}")


=== File: recipe_executor/steps/execute_recipe.py ===
import logging
import os
from typing import Dict, Optional

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
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
    """Step to execute a sub-recipe with an optional context override.

    This step uses template rendering to dynamically resolve the recipe path and any context overrides,
    then executes the sub-recipe using the provided executor. The same executor instance is used to ensure
    consistency between parent and sub-recipe execution.
    """

    def __init__(
        self, config: dict, logger: Optional[logging.Logger] = None, executor: Optional[ExecutorProtocol] = None
    ) -> None:
        """Initialize the ExecuteRecipeStep.

        Args:
            config (dict): The step configuration as a dictionary. It must contain the recipe_path, and may
                           contain context_overrides.
            logger: Optional logger instance.
            executor: Optional executor instance. If not provided, a new Executor instance will be created.
        """
        super().__init__(ExecuteRecipeConfig(**config), logger)
        # Use the provided executor or create a new one if none is provided.

        if executor is None:
            from recipe_executor.executor import Executor

            self.executor = Executor()
        else:
            self.executor = executor

    def execute(self, context: ContextProtocol) -> None:
        """Execute the sub-recipe defined in the configuration.

        This method applies template rendering to the recipe path and context overrides, ensures that the
        sub-recipe file exists, applies the context overrides, and then executes the sub-recipe using the
        shared executor instance. Logging is performed at the start and completion of sub-recipe execution.

        Args:
            context (ContextProtocol): The shared execution context.

        Raises:
            FileNotFoundError: If the resolved sub-recipe file does not exist.
            Exception: Propagates any errors that occur during sub-recipe execution.
        """
        try:
            # Render the recipe path using the current context
            rendered_recipe_path = render_template(self.config.recipe_path, context)

            # Verify that the sub-recipe file exists
            if not os.path.exists(rendered_recipe_path):
                error_message = f"Sub-recipe file not found: {rendered_recipe_path}"
                self.logger.error(error_message)
                raise FileNotFoundError(error_message)

            # Render context overrides and apply them before execution
            rendered_overrides: Dict[str, str] = {}
            for key, value in self.config.context_overrides.items():
                rendered_value = render_template(value, context)
                rendered_overrides[key] = rendered_value
                # Update the context with the override
                context[key] = rendered_value

            # Log the start of sub-recipe execution
            self.logger.info(f"Starting execution of sub-recipe: {rendered_recipe_path}")

            # Execute the sub-recipe using the shared executor instance
            self.executor.execute(rendered_recipe_path, context)

            # Log the successful completion of sub-recipe execution
            self.logger.info(f"Completed execution of sub-recipe: {rendered_recipe_path}")
        except Exception as error:
            # Log the error with sub-recipe path for debugging
            self.logger.error(f"Error executing sub-recipe '{self.config.recipe_path}': {str(error)}")
            raise


=== File: recipe_executor/steps/generate_llm.py ===
import logging
from typing import Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.llm_utils.llm import call_llm
from recipe_executor.utils import render_template


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


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    GenerateWithLLMStep executes an LLM call using a templated prompt and model.
    The result is stored in the context under a dynamically rendered artifact key.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: ContextProtocol) -> None:
        """
        Executes the generate_llm step:
          - Renders prompt and model using the context
          - Calls the LLM with the rendered prompt and model
          - Renders artifact key and stores the result in the context
        """
        try:
            # Render the prompt and model identifier from the configuration using the context values
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)

            self.logger.debug(f"Calling LLM with prompt: {rendered_prompt} and model: {rendered_model}")

            # Call the LLM with the rendered prompt and model
            result = call_llm(prompt=rendered_prompt, model=rendered_model, logger=self.logger)

            # Render the artifact key to store the generation result
            artifact_key = render_template(self.config.artifact, context)
            context[artifact_key] = result
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}", exc_info=True)
            raise e


=== File: recipe_executor/steps/parallel.py ===
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from recipe_executor.context import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc).
        max_concurrency: Maximum number of substeps to run concurrently. Default = 0 means no explicit limit
                         (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep. Default = 0 means no delay.
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep component that enables concurrent execution of multiple sub-steps within a recipe.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[Any] = None) -> None:
        # Parse the raw config dict into a ParallelConfig instance
        super().__init__(ParallelConfig(**config), logger)

    def execute_substep(self, substep_config: Dict[str, Any], context: ContextProtocol) -> None:
        """
        Executes a single sub-step in its own cloned context.

        Args:
            substep_config (Dict[str, Any]): The configuration dictionary for the sub-step.
            context (ContextProtocol): The parent execution context.
        """
        # Create an isolated clone of the context for this sub-step
        sub_context = context.clone()

        # Retrieve the step type; it is expected to be present in the substep_config
        step_type = substep_config.get("type")
        if not step_type:
            raise ValueError("Substep configuration missing required 'type' field")

        # Look up the registered step class by type
        if step_type not in STEP_REGISTRY:
            raise ValueError(f"Step type '{step_type}' is not registered in the STEP_REGISTRY")

        step_cls = STEP_REGISTRY[step_type]
        self.logger.debug(f"Instantiating substep of type '{step_type}' with config: {substep_config}")

        # Instantiate the step using its configuration; passing shared logger for consistency
        step_instance = step_cls(substep_config, self.logger)
        self.logger.debug(f"Starting execution of substep: {substep_config}")

        # Execute the sub-step; any exception will be propagated
        step_instance.execute(sub_context)
        self.logger.debug(f"Completed execution of substep: {substep_config}")

    def execute(self, context: ContextProtocol) -> None:
        """
        Executes all sub-steps concurrently with optional delay and fail-fast behavior.

        Args:
            context (ContextProtocol): The execution context for the current recipe step.

        Raises:
            Exception: Propagates the original exception from any sub-step that fails.
        """
        self.logger.info("Starting ParallelStep execution of %d substeps", len(self.config.substeps))
        substeps = self.config.substeps

        # Determine maximum worker threads: if max_concurrency is 0 or less, run all concurrently
        max_workers = self.config.max_concurrency if self.config.max_concurrency > 0 else len(substeps)

        # List to hold the futures of the submitted substeps
        futures = []
        exception_occurred: Optional[BaseException] = None

        # Using ThreadPoolExecutor to launch substeps concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for index, substep_config in enumerate(substeps):
                # Check if any previously submitted future has failed (fail-fast behavior)
                for future in futures:
                    if future.done() and future.exception() is not None:
                        exception_occurred = future.exception()
                        break
                if exception_occurred:
                    self.logger.error("A substep failed; aborting submission of further substeps")
                    break

                self.logger.info("Launching substep %d/%d", index + 1, len(substeps))
                # Submit the substep for execution
                future = executor.submit(self.execute_substep, substep_config, context)
                futures.append(future)

                # If a delay is specified and this is not the last substep, sleep before launching the next
                if self.config.delay > 0 and index < len(substeps) - 1:
                    self.logger.debug("Delaying next substep launch by %f seconds", self.config.delay)
                    time.sleep(self.config.delay)

            # After submission, wait for all submitted substeps to complete
            for future in futures:
                try:
                    # This will raise an exception if the substep execution failed
                    future.result()
                except Exception as e:
                    self.logger.error("A substep execution error occurred", exc_info=True)
                    raise Exception("ParallelStep failed due to a substep error") from e

        self.logger.info("ParallelStep execution completed successfully")


=== File: recipe_executor/steps/read_files.py ===
import os
from typing import Union, List

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template
from recipe_executor.protocols import ContextProtocol


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
    def __init__(self, config: dict, logger=None):
        # Initialize configuration and logger using the base step
        super().__init__(ReadFilesConfig(**config), logger)

    def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step: read one or more files, merge their contents as specified,
        and store the result into the context under the given artifact key.
        """
        # Normalize the input paths
        raw_paths = self.config.path
        if isinstance(raw_paths, str):
            # Check if the string contains comma-separated paths
            if "," in raw_paths:
                paths = [p.strip() for p in raw_paths.split(",") if p.strip()]
            else:
                paths = [raw_paths.strip()]
        elif isinstance(raw_paths, list):
            paths = raw_paths
        else:
            raise ValueError(f"Invalid type for path: {type(raw_paths)}")

        # Render template for each path
        rendered_paths: List[str] = []
        for path in paths:
            try:
                rendered = render_template(path, context)
                rendered_paths.append(rendered)
            except Exception as e:
                self.logger.error(f"Error rendering template for path '{path}': {e}")
                raise

        # Read file(s) and accumulate their contents
        # We store tuples of (identifier, content). For 'dict' mode, identifier is basename.
        file_contents: List[tuple] = []
        merge_mode = self.config.merge_mode

        for path in rendered_paths:
            self.logger.debug(f"Attempting to read file: {path}")

            if not os.path.exists(path):
                message = f"File not found: {path}"
                if self.config.optional:
                    self.logger.warning(message + " (optional file, handling accordingly)")
                    if merge_mode == "dict":
                        file_contents.append((os.path.basename(path), ""))
                    else:
                        # For concat mode, skip missing files
                        continue
                else:
                    raise FileNotFoundError(message)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.logger.info(f"Successfully read file: {path}")
                if merge_mode == "dict":
                    file_contents.append((os.path.basename(path), content))
                else:
                    file_contents.append((path, content))
            except Exception as e:
                self.logger.error(f"Error reading file '{path}': {e}")
                raise

        # If no content was read, handle accordingly
        if not file_contents:
            if self.config.optional:
                self.logger.info(f"No files were read; storing empty content for artifact '{self.config.artifact}'")
                final_content = {} if merge_mode == "dict" else ""
            else:
                raise FileNotFoundError(f"None of the specified files were found: {rendered_paths}")
        elif len(file_contents) == 1:
            # Single file behavior: maintain original behavior
            if merge_mode == "dict":
                final_content = {file_contents[0][0]: file_contents[0][1]}
            else:
                final_content = file_contents[0][1]
        else:
            # Multiple files handling
            if merge_mode == "dict":
                final_content = {filename: content for filename, content in file_contents}
            else:
                # Concatenate with newlines between each file's content, including a header with the file name
                content_list = []
                for identifier, content in file_contents:
                    header = os.path.basename(identifier)
                    content_list.append(f"{header}:\n{content}")
                final_content = "\n".join(content_list)

        # Store the final result into the context under the specified artifact key
        context[self.config.artifact] = final_content
        self.logger.info(f"Stored file content under artifact key '{self.config.artifact}' in context.")


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# A global registry for mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import logging
import os
from typing import List, Optional

from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
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
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(WriteFilesConfig(**config), logger)
        if self.logger is None:
            self.logger = logging.getLogger(__name__)

    def execute(self, context: ContextProtocol) -> None:
        # Retrieve the artifact from context
        artifact_key = self.config.artifact
        artifact = context.get(artifact_key)
        if artifact is None:
            error_msg = f"Artifact '{artifact_key}' not found in context."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Determine type of artifact and extract list of FileSpec
        file_specs: List[FileSpec] = []
        if isinstance(artifact, FileGenerationResult):
            file_specs = artifact.files
        elif isinstance(artifact, list):
            # Validate that all elements are FileSpec instances
            if all(isinstance(item, FileSpec) for item in artifact):
                file_specs = artifact
            else:
                error_msg = f"Artifact '{artifact_key}' list does not contain valid FileSpec objects."
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            error_msg = f"Artifact '{artifact_key}' is neither a FileGenerationResult nor a list of FileSpec objects."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Render the root path using template variables from context
        rendered_root = render_template(self.config.root, context)

        for file_spec in file_specs:
            try:
                # Render the file path template
                rendered_file_path = render_template(file_spec.path, context)

                # Prepend the rendered root path
                final_path = os.path.join(rendered_root, rendered_file_path) if rendered_root else rendered_file_path

                # Ensure the directory exists
                parent_dir = os.path.dirname(final_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                    self.logger.debug(f"Created directory: {parent_dir}")

                # Debug log before writing file
                self.logger.debug(f"Writing file: {final_path}")
                self.logger.debug(f"File content (first 100 chars): {file_spec.content[:100]}...")

                # Write the file content to disk
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(file_spec.content)

                # Log successful write
                file_size = len(file_spec.content.encode("utf-8"))
                self.logger.info(f"Successfully wrote file: {final_path} ({file_size} bytes)")
            except Exception as e:
                self.logger.error(f"Error writing file '{file_spec.path}': {str(e)}")
                raise


=== File: recipe_executor/utils.py ===
import logging
from typing import Dict

import liquid

from recipe_executor.protocols import ContextProtocol

# Set up module-level logger
logger = logging.getLogger(__name__)


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All context values are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    # Extract all artifacts from context using as_dict() for safety
    try:
        context_dict = context.as_dict()
    except Exception as e:
        raise ValueError(f"Failed to retrieve context data: {e}")

    # Convert all context values to strings
    safe_context: Dict[str, str] = {}
    for key, value in context_dict.items():
        try:
            safe_context[key] = str(value)
        except Exception as e:
            logger.debug(f"Error converting context value for key '{key}' to string: {e}")
            safe_context[key] = ""

    # Log debug information: template text and context keys
    logger.debug(f"Rendering template: {text}")
    logger.debug(f"Using context keys: {list(safe_context.keys())}")

    try:
        # Create a Liquid template instance
        template = liquid.Template(text)
        # Render the template with the safe context
        rendered_text = template.render(**safe_context)
        return rendered_text
    except Exception as e:
        error_message = (
            f"Error rendering template. Template: '{text}'. Context keys: {list(safe_context.keys())}. Error: {e}"
        )
        logger.debug(error_message)
        raise ValueError(error_message) from e


