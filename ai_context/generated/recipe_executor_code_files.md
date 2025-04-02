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
dev = ["pyright>=1.1.389", "ruff>=0.11.2"]

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
from typing import Any, Dict, Iterator, Optional
import copy


class Context:
    """
    Context is the shared state container for the Recipe Executor system,
    providing a dictionary-like interface for storing and retrieving artifacts
    along with separate configuration values.
    
    Attributes:
        config (Dict[str, Any]): A dictionary holding the configuration values.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store
            config: Configuration values
        """
        # Use deep copy to prevent external modifications
        self.__artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-like setting of artifacts."""
        self.__artifacts[key] = value

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access to artifacts.

        Raises:
            KeyError: If the key does not exist in the artifacts.
        """
        if key not in self.__artifacts:
            raise KeyError(f"Key '{key}' not found in Context.")
        return self.__artifacts[key]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get an artifact with an optional default value."""
        return self.__artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in artifacts."""
        return key in self.__artifacts

    def __iter__(self) -> Iterator[str]:
        """Iterate over artifact keys."""
        # Return a list copy of keys to ensure immutability
        return iter(list(self.__artifacts.keys()))

    def keys(self) -> Iterator[str]:
        """Return an iterator over the keys of artifacts."""
        return iter(list(self.__artifacts.keys()))

    def __len__(self) -> int:
        """Return the number of artifacts."""
        return len(self.__artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """Return a deep copy of the artifacts as a dictionary to ensure immutability."""
        return copy.deepcopy(self.__artifacts)

    def clone(self) -> "Context":
        """Return a deep copy of the current context, including artifacts and configuration."""
        cloned_artifacts = copy.deepcopy(self.__artifacts)
        cloned_config = copy.deepcopy(self.config)
        return Context(artifacts=cloned_artifacts, config=cloned_config)


=== File: recipe_executor/executor.py ===
import json
import logging
import os
from typing import Any, Dict, Optional, Union

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor:
    """
    Executor component for the Recipe Executor system.

    Loads recipe definitions from various sources and executes their steps sequentially using the provided context.

    Supported recipe formats:
        - File path pointing to a JSON file
        - JSON string
        - Dictionary

    Each recipe must be a dictionary with a 'steps' key containing a list of step definitions.
    Each step must have a 'type' field that corresponds to a registered step in STEP_REGISTRY.
    """

    def __init__(self) -> None:
        # Minimal initialization. Could be expanded later if needed.
        pass

    def execute(
        self, recipe: Union[str, Dict[str, Any]], context: Context, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Execute a recipe with the given context.

        Args:
            recipe: Recipe to execute; can be a file path, JSON string, or dictionary.
            context: Context instance for execution that stores shared artifacts.
            logger: Optional logger; if not provided, a default one will be created.

        Raises:
            ValueError: If the recipe format is invalid or the execution of any step fails.
            TypeError: If the recipe type is not supported.
        """
        # Set up the logger if not provided
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

        # Determine the recipe data source (dictionary, file path, or JSON string)
        recipe_data: Dict[str, Any]
        if isinstance(recipe, dict):
            recipe_data = recipe
            logger.debug("Loaded recipe from dictionary.")
        elif isinstance(recipe, str):
            # Check if the string is a file path
            if os.path.exists(recipe) and os.path.isfile(recipe):
                try:
                    with open(recipe, "r", encoding="utf-8") as f:
                        recipe_data = json.load(f)
                    logger.debug(f"Recipe loaded successfully from file: {recipe}")
                except Exception as e:
                    raise ValueError(f"Failed to read or parse recipe file '{recipe}': {e}") from e
            else:
                # Attempt to parse the string as JSON
                try:
                    recipe_data = json.loads(recipe)
                    logger.debug("Recipe loaded successfully from JSON string.")
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid recipe format. Expected file path or valid JSON string. Error: {e}"
                    ) from e
        else:
            raise TypeError(f"Unsupported recipe type: {type(recipe)}")

        # Validate that the parsed recipe is a dictionary
        if not isinstance(recipe_data, dict):
            raise ValueError("Recipe must be a dictionary after parsing.")

        steps = recipe_data.get("steps")
        if not isinstance(steps, list):
            raise ValueError("Recipe must contain a 'steps' key with a list of steps.")

        logger.debug(f"Starting recipe execution with {len(steps)} step(s). Recipe data: {recipe_data}")

        # Execute each step sequentially
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step at index {idx} is not a valid dictionary.")

            step_type = step.get("type")
            if not step_type:
                raise ValueError(f"Step at index {idx} is missing the 'type' field.")

            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}. Please ensure it is registered.")

            step_class = STEP_REGISTRY[step_type]

            try:
                logger.debug(f"Executing step {idx} of type '{step_type}'. Step details: {step}")
                step_instance = step_class(step, logger)
                step_instance.execute(context)
                logger.debug(f"Step {idx} executed successfully.")
            except Exception as e:
                raise ValueError(f"Error executing step at index {idx} (type '{step_type}'): {e}") from e

        logger.debug("Recipe execution completed successfully.")


=== File: recipe_executor/llm.py ===
import logging
import time
from typing import Optional

# Import the required pydantic-ai models and Agent
from pydantic_ai import Agent

# Import the LLM model classes
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# Import the FileGenerationResult (structured output) model from the models component
# (Assuming it is defined in recipe_executor/models.py)
from recipe_executor.models import FileGenerationResult


# For Azure OpenAI, use the get_openai_model function from our azure utility module
from recipe_executor.llm_utils.azure_openai import get_openai_model


def get_model(model_id: Optional[str] = None):
    """
    Initialize an LLM model instance based on a standardized model_id string.
    Expected format:
      provider:model_name
      For Azure OpenAI, you can additionally supply a deployment name, e.g.,
         azure:model_name:deployment_name
    If model_id is None, it will default to 'openai:gpt-4o'.

    Supported providers:
      - openai
      - anthropic
      - gemini
      - azure

    Returns:
      An instance of the appropriate LLM model class.
    
    Raises:
      ValueError: If the model_id format is invalid or provider is unsupported.
    """
    if not model_id:
        model_id = "openai:gpt-4o"
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model id format: {model_id}")
    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "azure":
        # For Azure, we allow an optional deployment name; if not provided, default to model_name
        deployment = parts[2] if len(parts) >= 3 else model_name
        return get_openai_model(model_name, deployment)
    elif provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Create and return an Agent instance configured with the specified LLM model and structured output type.
    If no model_id is provided, it defaults to 'openai:gpt-4o'.

    Returns:
      Agent with the LLM model and result_type set to FileGenerationResult.
    """
    model = get_model(model_id)
    # Create the agent with the chosen model and specifying FileGenerationResult as the structured output type
    return Agent(model, result_type=FileGenerationResult)


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or 'provider:model_name:deployment_name').
            If not provided, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): A logger instance; if None, one named 'RecipeExecutor' is used.

    Returns:
        FileGenerationResult: The structured result from the LLM call.

    Raises:
        Exception: Propagates exceptions encountered during the LLM call.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    try:
        model_id = model if model else "openai:gpt-4o"
        parts = model_id.split(":")
        provider = parts[0] if parts else "openai"
        logger.info(f"Calling LLM: provider={provider}, model_id={model_id}")
        logger.debug(f"Prompt payload: {prompt}")

        agent = get_agent(model_id)
        start_time = time.time()
        result = agent.run_sync(prompt)
        elapsed = time.time() - start_time
        logger.info(f"LLM call completed in {elapsed:.2f} seconds")
        logger.debug(f"Full response: {result}")
        # Return the data portion of the result
        return result.data
    except Exception as e:
        logger.error("Error calling LLM", exc_info=True)
        raise e


=== File: recipe_executor/llm_utils/azure_openai.py ===
import os
import logging
from typing import Optional

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key by revealing only the first and last character.
    For example, 'abcd1234' becomes 'a******4'.
    """
    if not api_key:
        return ""
    if len(api_key) <= 4:
        return '*' * len(api_key)
    return api_key[0] + ('*' * (len(api_key) - 2)) + api_key[-1]



def get_openai_model(model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance configured for Azure OpenAI.

    The method determines the authentication method based on environment variables:
      - If AZURE_USE_MANAGED_IDENTITY is set to true (or '1'), it uses Azure Identity for authentication.
      - Otherwise, it uses the AZURE_OPENAI_API_KEY for API key authentication.

    Required Environment Variables:
      - AZURE_OPENAI_ENDPOINT
      - AZURE_OPENAI_API_VERSION (optional, defaults to '2025-03-01-preview')
      - AZURE_OPENAI_DEPLOYMENT_NAME (optional, fallback to model_name if not provided)

    For API key authentication (if not using managed identity):
      - AZURE_OPENAI_API_KEY

    For Managed Identity authentication:
      - AZURE_USE_MANAGED_IDENTITY (set to true or 1)
      - Optionally, AZURE_MANAGED_IDENTITY_CLIENT_ID

    Args:
        model_name (str): Name of the model (e.g., 'gpt-4o').
        deployment_name (Optional[str]): Custom deployment name, defaults to environment var or model_name.
        logger (Optional[logging.Logger]): Logger instance, defaults to a logger named 'RecipeExecutor'.

    Returns:
        OpenAIModel: Configured for Azure OpenAI.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Load required environment variables
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise Exception("Missing required environment variable: AZURE_OPENAI_ENDPOINT")

    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    env_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    deployment = deployment_name or env_deployment or model_name

    # Determine authentication method
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ["true", "1"]

    if use_managed_identity:
        # Use Azure Identity
        try:
            managed_identity_client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
            if managed_identity_client_id:
                credential = ManagedIdentityCredential(client_id=managed_identity_client_id)
                logger.info("Using ManagedIdentityCredential with client id.")
            else:
                credential = DefaultAzureCredential()
                logger.info("Using DefaultAzureCredential for Managed Identity.")
        except Exception as ex:
            logger.error("Failed to create Azure Credential: %s", ex)
            raise

        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

        try:
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment
            )
            logger.info("Initialized Azure OpenAI client with Managed Identity.")
        except Exception as ex:
            logger.error("Error initializing AsyncAzureOpenAI client with Managed Identity: %s", ex)
            raise
    else:
        # Use API key authentication
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not azure_api_key:
            raise Exception("Missing required environment variable: AZURE_OPENAI_API_KEY")
        masked_key = mask_api_key(azure_api_key)
        logger.info("Initializing Azure OpenAI client with API Key: %s", masked_key)

        try:
            azure_client = AsyncAzureOpenAI(
                api_key=azure_api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment
            )
            logger.info("Initialized Azure OpenAI client with API Key.")
        except Exception as ex:
            logger.error("Error initializing AsyncAzureOpenAI client with API key: %s", ex)
            raise

    # Create the provider and model instance
    provider = OpenAIProvider(openai_client=azure_client)
    model_instance = OpenAIModel(model_name, provider=provider)
    logger.info("Created OpenAIModel instance for model '%s' using deployment '%s'", model_name, deployment)
    return model_instance


=== File: recipe_executor/logger.py ===
import os
import sys
import logging
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
    # Create log directory if it doesn't exist
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            # Log creation of directory if running in debug mode later
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Define log file paths
    debug_log = os.path.join(log_dir, "debug.log")
    info_log = os.path.join(log_dir, "info.log")
    error_log = os.path.join(log_dir, "error.log")

    # Common log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Get logger instance with a specific name
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Set logger to capture all messages

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    try:
        # Debug file handler: logs all messages
        debug_handler = logging.FileHandler(debug_log, mode="w")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)

        # Info file handler: logs INFO and above
        info_handler = logging.FileHandler(info_log, mode="w")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)

        # Error file handler: logs ERROR and above
        error_handler = logging.FileHandler(error_log, mode="w")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # Console handler: logs INFO and above to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    except Exception as e:
        raise Exception(f"Failed to set up logging handlers: {e}")

    # Log debug message indicating logger initialization
    logger.debug(f"Logger initialized. Log directory: {log_dir}")

    return logger


=== File: recipe_executor/main.py ===
import argparse
import sys
import time
import traceback
from typing import Dict, Optional

from dotenv import load_dotenv

from recipe_executor.context import Context
from executor import Executor
from recipe_executor.logger import init_logger


def parse_context(context_list: Optional[list]) -> Dict[str, str]:
    """
    Parse a list of key=value pairs into a dictionary.

    Args:
        context_list: List of strings in the format key=value.

    Returns:
        Dictionary with keys and values as strings.

    Raises:
        ValueError: If any of the context items is not in key=value format.
    """
    context_dict: Dict[str, str] = {}
    if not context_list:
        return context_dict

    for item in context_list:
        if '=' not in item:
            raise ValueError(f"Invalid context format: '{item}'. Expected key=value.")
        key, value = item.split('=', 1)
        if not key:
            raise ValueError(f"Context key cannot be empty in pair: '{item}'.")
        context_dict[key] = value
    return context_dict


def main() -> None:
    # Load environment variables as early as possible
    load_dotenv()

    # Setup argument parser
    parser = argparse.ArgumentParser(description="Recipe Executor Tool")
    parser.add_argument(
        "recipe_path",
        type=str,
        help="Path to the recipe file to execute"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for log files (default: logs)"
    )
    parser.add_argument(
        "--context",
        action="append",
        help="Context values as key=value pairs (can be used multiple times)"
    )

    args = parser.parse_args()

    start_time = time.time()

    # Parse context values from command-line
    try:
        context_artifacts = parse_context(args.context)
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    # Initialize logger
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger initialization failed: {str(e)}\n")
        sys.exit(1)

    logger.debug(f"Starting main function with arguments: {args}")
    logger.debug(f"Context artifacts: {context_artifacts}")

    # Create the execution context
    context = Context(artifacts=context_artifacts)

    # Initialize Executor
    executor = Executor()

    try:
        logger.info("Starting Recipe Executor Tool")
        logger.info(f"Executing recipe: {args.recipe_path}")

        executor.execute(args.recipe_path, context, logger=logger)

        elapsed_time = time.time() - start_time
        logger.info(f"Recipe executed successfully in {elapsed_time:.2f} seconds")

    except Exception as e:
        error_message = f"An error occurred during recipe execution: {str(e)}"
        logger.error(error_message, exc_info=True)
        sys.stderr.write(error_message + "\n")
        sys.stderr.write(traceback.format_exc() + "\n")
        sys.exit(1)

    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds")


if __name__ == '__main__':
    main()


=== File: recipe_executor/models.py ===
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """
    path: str = Field(..., description="Relative path where the file should be written")
    content: str = Field(..., description="The content of the file")


class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """
    files: List[FileSpec] = Field(..., description="List of files to generate")
    commentary: Optional[str] = Field(None, description="Optional commentary from the LLM")


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """
    type: str = Field(..., description="The type of the recipe step")
    config: Dict = Field(..., description="Dictionary containing configuration for the step")


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    steps: List[RecipeStep] = Field(..., description="List of steps in the recipe")


=== File: recipe_executor/steps/__init__.py ===
from recipe_executor.steps.registry import STEP_REGISTRY

from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register standard steps in the registry
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_file": ReadFileStep,
    "write_files": WriteFilesStep,
})


=== File: recipe_executor/steps/base.py ===
import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

from recipe_executor.context import Context

# Base configuration class for all step configurations
class StepConfig(BaseModel):
    """Base class for step configurations. Extend this class for specific steps."""
    pass

# Generic type variable for step configuration types
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """Base class for all step implementations in the Recipe Executor system.

    Subclasses must implement the execute(context) method. Each step receives a config
    object and a logger instance. If no logger is provided, a default logger named 'RecipeExecutor'
    will be used.

    Args:
        config (ConfigType): Configuration for the step.
        logger (Optional[logging.Logger]): Logger instance; defaults to a logger with name "RecipeExecutor".
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")
        # Log at debug level when the step component is initialized
        self.logger.debug(f"Step component initialized with configuration: {self.config.json()}")

    @abstractmethod
    def execute(self, context: Context) -> None:
        """Execute the step with the given context.

        Args:
            context: A context object for data sharing among steps.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Each step must implement the execute() method.")



=== File: recipe_executor/steps/execute_recipe.py ===
import os
import logging
from typing import Dict, Optional

from recipe_executor.context import Context
from recipe_executor.executor import Executor
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
    """Step to execute a sub-recipe using a provided recipe file path and context overrides.

    This step:
      - Applies template rendering on the recipe path and on context overrides.
      - Shares the current context with the sub-recipe, modifying it as needed with overrides.
      - Validates that the sub-recipe file exists before executing it.
      - Logs the start and completion details of sub-recipe execution.
      - Uses the existing Executor to run the sub-recipe.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize with config converted by ExecuteRecipeConfig
        super().__init__(ExecuteRecipeConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """Execute the sub-recipe with context overrides and template rendering.

        Args:
            context (Context): The execution context received from the parent recipe.

        Raises:
            FileNotFoundError: If the sub-recipe file does not exist.
            Exception: Propagates any error encountered during sub-recipe execution.
        """
        # Apply context overrides using template rendering
        if hasattr(self.config, 'context_overrides') and self.config.context_overrides:
            for key, value in self.config.context_overrides.items():
                try:
                    rendered_value = render_template(value, context)
                    context[key] = rendered_value
                except Exception as e:
                    self.logger.error(f"Error rendering context override for key '{key}': {str(e)}")
                    raise

        # Render the recipe path using the current context
        try:
            recipe_path = render_template(self.config.recipe_path, context)
        except Exception as e:
            self.logger.error(f"Error rendering recipe path '{self.config.recipe_path}': {str(e)}")
            raise

        # Validate that the sub-recipe file exists
        if not os.path.exists(recipe_path):
            error_msg = f"Sub-recipe file not found: {recipe_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Log sub-recipe execution start
        self.logger.info(f"Executing sub-recipe: {recipe_path}")

        try:
            # Execute the sub-recipe using the same executor
            executor = Executor()
            executor.execute(recipe=recipe_path, context=context, logger=self.logger)
        except Exception as e:
            # Log error with sub-recipe path and propagate
            self.logger.error(f"Error during sub-recipe execution ({recipe_path}): {str(e)}")
            raise

        # Log sub-recipe execution completion
        self.logger.info(f"Completed sub-recipe: {recipe_path}")


=== File: recipe_executor/steps/generate_llm.py ===
import logging
from typing import Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.llm import call_llm
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
    Step that generates content using a large language model (LLM).
    It processes templates for the prompt, model, and artifact key, calls the LLM, and stores the result in the context.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Process the artifact key using templating if needed
        artifact_key: str = self.config.artifact
        if '{{' in artifact_key and '}}' in artifact_key:
            try:
                artifact_key = render_template(artifact_key, context)
            except Exception as e:
                self.logger.error(f"Error rendering artifact template '{artifact_key}': {e}")
                raise ValueError(f"Invalid artifact template: {artifact_key}")

        # Render the prompt and model using the current context
        try:
            rendered_prompt: str = render_template(self.config.prompt, context)
        except Exception as e:
            self.logger.error(f"Error rendering prompt template: {e}")
            raise ValueError(f"Invalid prompt template: {self.config.prompt}")

        try:
            rendered_model: str = render_template(self.config.model, context)
        except Exception as e:
            self.logger.error(f"Error rendering model template: {e}")
            raise ValueError(f"Invalid model template: {self.config.model}")

        self.logger.debug(f"LLM call is being made for artifact '{artifact_key}' with model '{rendered_model}'.")

        # Call the LLM and store the response
        try:
            response = call_llm(rendered_prompt, rendered_model, logger=self.logger)
        except Exception as e:
            self.logger.error(f"LLM call failed for artifact '{artifact_key}': {e}", exc_info=True)
            raise RuntimeError(f"LLM call failed: {e}")

        context[artifact_key] = response
        self.logger.debug(f"LLM response stored in context under '{artifact_key}'")


=== File: recipe_executor/steps/parallel.py ===
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition.
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default = 0 means no explicit limit.
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep executes multiple sub-recipes concurrently.

    Each sub-recipe is executed in its own cloned context.
    Fail-fast behavior is implemented to stop execution upon a substep failure.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[Any] = None) -> None:
        # Convert the config dict to ParallelConfig object
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info(f"Starting ParallelStep with {len(self.config.substeps)} substeps.")

        # Determine the maximum concurrency to use
        if self.config.max_concurrency and self.config.max_concurrency > 0:
            max_workers = self.config.max_concurrency
        else:
            max_workers = len(self.config.substeps) if self.config.substeps else 1

        futures = []
        exception_occurred = False

        def run_substep(index: int, substep: Dict[str, Any], parent_context: Context) -> None:
            substep_type = substep.get("type", "unknown")
            # Clone the parent context to ensure isolation
            cloned_context = parent_context.clone()
            self.logger.debug(f"[Substep {index}] Cloned context for substep: {substep}.")
            try:
                # Get the step class from the registry
                if substep_type not in STEP_REGISTRY:
                    raise ValueError(f"Substep type '{substep_type}' is not registered in STEP_REGISTRY.")
                step_cls = STEP_REGISTRY[substep_type]
                self.logger.debug(f"[Substep {index}] Instantiating step of type '{substep_type}'.")
                # Instantiate the step
                step_instance = step_cls(substep, self.logger)
                self.logger.info(f"[Substep {index}] Execution started for substep with config: {substep}.")
                # Execute the substep
                step_instance.execute(cloned_context)
                self.logger.info(f"[Substep {index}] Execution completed successfully.")
            except Exception as e:
                error_msg = (f"[Substep {index}] Substep execution failed for type '{substep_type}' "
                             f"with recipe_path '{substep.get('recipe_path', 'N/A')}'. Error: {str(e)}")
                self.logger.error(error_msg)
                raise Exception(error_msg) from e

        # Use ThreadPoolExecutor to execute substeps concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx, substep in enumerate(self.config.substeps):
                # Before launching a new substep, check if an error has already occurred
                if exception_occurred:
                    self.logger.debug(f"[Substep {idx}] Skipped launching due to previous errors.")
                    break
                self.logger.debug(f"[Substep {idx}] Submitting substep for execution.")
                future = executor.submit(run_substep, idx, substep, context)
                futures.append((idx, future))
                # Apply launch delay if specified and if this is not the last substep
                if self.config.delay > 0 and idx < len(self.config.substeps) - 1:
                    self.logger.debug(f"Delaying next substep launch by {self.config.delay} seconds.")
                    time.sleep(self.config.delay)

            # Monitor the futures for completion and fail-fast in case of exception
            for idx, future in futures:
                try:
                    # This will re-raise any exception encountered during execution
                    future.result()
                except Exception as e:
                    self.logger.error(f"Fail-fast: Cancelling remaining substeps due to failure in substep {idx}.")
                    exception_occurred = True
                    # Cancel any futures that haven't completed yet
                    for _, f in futures:
                        if not f.done():
                            f.cancel()
                    # Propagate the error
                    raise e

        self.logger.info(f"ParallelStep completed. All substeps finished successfully.")


=== File: recipe_executor/steps/read_file.py ===
import os
import logging
from typing import Any, Dict, Optional

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


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


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    ReadFileStep reads a file from the filesystem using a dynamic path resolved via templating.
    It stores the file content in the provided context under the specified artifact key.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to ReadFileConfig using pydantic or similar underlying mechanism
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Render the file path using context and provided template
        rendered_path = render_template(self.config.path, context)
        self.logger.debug(f"Attempting to read file from path: {rendered_path}")

        # Check if file exists
        if not os.path.exists(rendered_path):
            if self.config.optional:
                self.logger.warning(f"Optional file not found at path: {rendered_path}. Continuing with empty content.")
                context[self.config.artifact] = ""
                return
            else:
                error_message = f"ReadFileStep: file not found at path: {rendered_path}"
                self.logger.error(error_message)
                raise FileNotFoundError(error_message)

        # Read the file using UTF-8 encoding
        self.logger.info(f"Reading file from: {rendered_path}")
        try:
            with open(rendered_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading file at {rendered_path}: {e}")
            raise

        # Store the file content in context under the specified artifact key
        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global dictionary to store step registrations
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import os
import logging
from typing import List, Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.models import FileSpec, FileGenerationResult
from recipe_executor.context import Context
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths.
    """
    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    WriteFilesStep writes generated files to disk based on the content in the context.
    It supports both FileGenerationResult and list of FileSpec formats.
    It renders file paths using templates, creates necessary directories, and writes the file content.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to WriteFilesConfig using StepConfig capabilities
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Retrieve the artifact from the context
        data = context.get(self.config.artifact)
        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine the list of files to write
        files: List[FileSpec] = []
        if isinstance(data, FileGenerationResult):
            files = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        try:
            # Render the output root path using template rendering
            output_root = render_template(self.config.root, context)
        except Exception as e:
            self.logger.error(f"Failed to render template for root path: {e}")
            raise ValueError(f"Failed to render template for root path: {e}")

        # Process each file in the list
        for file in files:
            try:
                # Render the file path using template rendering
                rel_path = render_template(file.path, context)
                full_path = os.path.join(output_root, rel_path)

                # Log debug information before writing
                self.logger.debug(f"Writing file at path: {full_path} with content size: {len(file.content)}")

                # Create parent directories if they don't exist
                parent_dir = os.path.dirname(full_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                # Write the file content using UTF-8 encoding
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)

                # Log success of file write operation
                self.logger.info(f"Wrote file: {full_path} (size: {len(file.content)} bytes)")
            except IOError as ioe:
                self.logger.error(f"I/O error writing file: {ioe}")
                raise
            except Exception as e:
                self.logger.error(f"Error processing file {file.path}: {e}")
                raise


=== File: recipe_executor/utils.py ===
import logging
from typing import Any, Dict

from liquid import Template

from recipe_executor.context import Context

# Configure module-level logger
logger = logging.getLogger(__name__)


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
    logger.debug(f"Rendering template: {text}")
    
    try:
        # Retrieve context artifacts and log the keys for debugging
        context_dict: Dict[str, Any] = context.as_dict()
        debug_context_keys = list(context_dict.keys())
        logger.debug(f"Context keys: {debug_context_keys}")

        # Convert all context values to strings to avoid type errors
        safe_context = {key: str(value) for key, value in context_dict.items()}

        # Create the Liquid template and render it using the safe context
        template_obj = Template(text)
        result = template_obj.render(safe_context)

        return result
    except Exception as e:
        error_message = f"Error rendering template: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


