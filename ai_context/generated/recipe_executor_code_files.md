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
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register steps by updating the registry
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
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from recipe_executor.context import Context  # Assumed to exist in the project


class StepConfig(BaseModel):
    """Base class for all step configurations. Extend this class in each step's configuration."""
    pass


# Type variable for configuration types bound to StepConfig
ConfigType = TypeVar('ConfigType', bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """
    Base class for all step implementations in the Recipe Executor system.
    Subclasses must implement the `execute` method.

    Each step is initialized with a configuration object and an optional logger.

    Args:
        config (ConfigType): Configuration for the step, validated using Pydantic.
        logger (Optional[logging.Logger]): Logger instance; defaults to the 'RecipeExecutor' logger.
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config}")

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Execute the step using the provided context.

        Args:
            context (Context): Shared context for data exchange between steps.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError("Each step must implement the `execute()` method.")


=== File: recipe_executor/steps/execute_recipe.py ===
import os
from typing import Dict, Any

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.executor import Executor
from recipe_executor.context import Context
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
    """Step that executes a sub-recipe with optional context overrides.

    This component uses template rendering for dynamic resolution of recipe paths and context overrides, 
    validates that the target recipe file exists, applies context overrides, and executes the sub-recipe 
    using a shared Executor instance. Execution start and completion are logged as info messages.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        super().__init__(ExecuteRecipeConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """Execute the sub-recipe with rendered paths and context overrides.

        Args:
            context (Context): The shared context object.

        Raises:
            RuntimeError: If the sub-recipe file does not exist or if execution fails.
        """
        try:
            # Render the recipe path using the current context
            rendered_recipe_path = render_template(self.config.recipe_path, context)
            
            # Render context overrides
            rendered_overrides: Dict[str, str] = {}
            for key, value in self.config.context_overrides.items():
                rendered_overrides[key] = render_template(value, context)
            
            # Validate that the sub-recipe file exists
            if not os.path.isfile(rendered_recipe_path):
                error_msg = f"Sub-recipe file not found: {rendered_recipe_path}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Log start of execution
            self.logger.info(f"Starting execution of sub-recipe: {rendered_recipe_path}")
            
            # Apply context overrides before sub-recipe execution
            for key, value in rendered_overrides.items():
                context[key] = value
            
            # Execute the sub-recipe with the same context and logger
            executor = Executor()
            executor.execute(rendered_recipe_path, context, self.logger)
            
            # Log completion of sub-recipe execution
            self.logger.info(f"Completed execution of sub-recipe: {rendered_recipe_path}")

        except Exception as e:
            error_msg = f"Error executing sub-recipe '{self.config.recipe_path}': {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e


=== File: recipe_executor/steps/generate_llm.py ===
import logging
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.steps.base import BaseStep, StepConfig
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
    GenerateWithLLMStep enables recipes to generate content using large language models.
    It processes prompt templates using context data, supports configurable model selection,
    calls the LLM for content generation, and then stores the generated results in the context.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert the config dict into a GenerateLLMConfig Pydantic model
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the LLM generation step by rendering templates, calling the LLM, and storing the result.

        Args:
            context (Context): The execution context containing artifacts and configuration.

        Raises:
            Exception: Propagates exceptions from LLM call failures.
        """
        try:
            # Render the prompt, model identifier, and artifact key using the provided context
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)
            artifact_key = render_template(self.config.artifact, context)

            self.logger.debug("Calling LLM with prompt: %s using model: %s", rendered_prompt, rendered_model)
            # Call the large language model with the rendered prompt and model identifier
            response = call_llm(rendered_prompt, rendered_model, logger=self.logger)

            # Store the generation result in the context under the dynamically rendered artifact key
            context[artifact_key] = response

        except Exception as e:
            self.logger.error("LLM call failed for prompt: %s with error: %s", self.config.prompt, str(e))
            raise e


=== File: recipe_executor/steps/parallel.py ===
from typing import List, Dict, Any, Optional
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel. Each substep should be an execute_recipe step definition.
        max_concurrency: Maximum number of substeps to run concurrently. Default = 0 means no explicit limit.
        delay: Optional delay (in seconds) between launching each substep. Default = 0 means no delay.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep executes multiple sub-steps concurrently within a single step.

    It clones the provided context for each sub-step, executes sub-steps concurrently using a ThreadPoolExecutor,
    supports an optional delay between launching each sub-step, implements fail-fast behavior, and waits for all
    sub-steps to complete before proceeding.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Initialize with ParallelConfig created from the provided dict config
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info("Starting ParallelStep execution.")
        substeps = self.config.substeps
        if not substeps:
            self.logger.info("No substeps provided. Exiting ParallelStep.")
            return

        # Determine max_workers based on configuration
        max_workers = self.config.max_concurrency if self.config.max_concurrency > 0 else len(substeps)

        futures = []
        executor = ThreadPoolExecutor(max_workers=max_workers)
        error_occurred = None

        try:
            for index, sub_config in enumerate(substeps):
                # If an error has already occurred, do not launch further substeps (fail-fast behavior)
                if error_occurred:
                    self.logger.error("Fail-fast: Aborting launch of further substeps due to earlier error.")
                    break

                # Clone the context for isolation
                cloned_context = context.clone()

                # Determine sub-step type and ensure it is registered
                step_type = sub_config.get("type")
                if step_type not in STEP_REGISTRY:
                    raise ValueError(f"Sub-step type '{step_type}' is not registered in STEP_REGISTRY.")

                sub_step_class = STEP_REGISTRY[step_type]
                sub_step = sub_step_class(sub_config, self.logger)

                self.logger.debug(f"Launching sub-step {index + 1}/{len(substeps)} of type '{step_type}'.")

                # Define the runner function for the sub-step
                def run_sub_step(step=sub_step, ctx=cloned_context, idx=index):
                    self.logger.debug(f"Sub-step {idx + 1} started.")
                    step.execute(ctx)
                    self.logger.debug(f"Sub-step {idx + 1} completed.")

                # Submit the sub-step for execution
                future = executor.submit(run_sub_step)
                futures.append(future)

                # Optional delay between launching each sub-step
                if self.config.delay > 0 and index < len(substeps) - 1:
                    self.logger.debug(f"Delaying launch of next sub-step by {self.config.delay} seconds.")
                    time.sleep(self.config.delay)

            # Wait for all futures to complete, handling any exception immediately (fail-fast behavior)
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    error_occurred = exc
                    self.logger.error(f"A sub-step raised an exception: {exc}. Cancelling pending substeps.")
                    # Cancel pending substeps
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    # Shutdown executor immediately, cancelling futures if supported
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise exc
        finally:
            executor.shutdown(wait=True)

        self.logger.info(f"ParallelStep completed: {len(substeps)} substeps executed.")


=== File: recipe_executor/steps/read_files.py ===
import os
import logging
from typing import List, Union, Optional, Dict

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.utils import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path or list of paths to the file(s) to read (may be templated).
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
    A step that reads one or more files from the filesystem and stores their contents in the execution context.

    It supports both single file and multiple file operations, template-based path resolution,
    and flexible merging modes for multiple files.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to ReadFilesConfig instance
        super().__init__(ReadFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the file reading step. Resolves template-based paths, reads file(s), handles optional files,
        and stores the content into the context using the artifact key.

        Args:
            context (Context): The execution context.

        Raises:
            FileNotFoundError: If a required file does not exist.
        """
        # Resolve artifact key using template rendering
        artifact_key = render_template(self.config.artifact, context)

        # Ensure paths is a list
        paths_input = self.config.path
        if isinstance(paths_input, str):
            paths_list: List[str] = [paths_input]
        else:
            paths_list = paths_input

        # This will hold the results for multiple files
        file_contents: Union[str, Dict[str, str]] = "" if self.config.merge_mode == "concat" else {}
        multiple_files = len(paths_list) > 1

        # Temp storage for individual file contents
        contents_list: List[str] = []
        contents_dict: Dict[str, str] = {}

        for path_template in paths_list:
            # Render the file path using the context
            rendered_path = render_template(path_template, context)
            self.logger.debug(f"Attempting to read file: {rendered_path}")

            if not os.path.exists(rendered_path):
                message = f"File not found: {rendered_path}"
                if self.config.optional:
                    self.logger.warning(message + " [optional]")
                    # For optional files, handle based on merge mode
                    if multiple_files and self.config.merge_mode == "dict":
                        # Use the basename as key with empty content
                        contents_dict[os.path.basename(rendered_path)] = ""
                    elif multiple_files and self.config.merge_mode == "concat":
                        # Skip file in concatenation mode
                        continue
                    else:
                        # Single file optional: store empty string
                        file_contents = ""
                        self.logger.info(f"Stored empty content for optional file: {rendered_path}")
                        context[artifact_key] = file_contents
                        continue
                else:
                    self.logger.error(message)
                    raise FileNotFoundError(message)
            else:
                try:
                    with open(rendered_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.logger.info(f"Successfully read file: {rendered_path}")
                except Exception as e:
                    self.logger.error(f"Error reading file {rendered_path}: {str(e)}")
                    raise e

                # Process content based on merge mode
                if multiple_files:
                    if self.config.merge_mode == "dict":
                        key = os.path.basename(rendered_path)
                        contents_dict[key] = content
                    else:  # Default to 'concat'
                        # Append filename and content separated by newlines
                        formatted = f"{rendered_path}\n{content}"
                        contents_list.append(formatted)
                else:
                    # Single file; simply assign content
                    file_contents = content

        # Merge file contents if multiple files
        if multiple_files:
            if self.config.merge_mode == "dict":
                file_contents = contents_dict
            else:  # concat
                # Join each file's formatted content with double newlines
                file_contents = "\n\n".join(contents_list)

        # Store the final content under the artifact key in the context
        context[artifact_key] = file_contents
        self.logger.info(f"Stored file content under key: '{artifact_key}'")


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global registry for step implementations
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import os
import logging
from typing import List, Union, Any

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.models import FileSpec, FileGenerationResult
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
    """
    WriteFilesStep component responsible for writing generated files to disk.

    It supports both FileGenerationResult and List[FileSpec] formats, creates directories 
    as needed, applies template rendering to the file paths, and logs file operation details.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Retrieve the files artifact from the context using the configured artifact key
        artifact_key = self.config.artifact
        if artifact_key not in context:
            error_msg = f"Artifact '{artifact_key}' not found in the context."
            self.logger.error(error_msg)
            raise KeyError(error_msg)

        raw_files = context[artifact_key]

        # Determine if raw_files is a FileGenerationResult or list of FileSpec
        files_to_write: List[FileSpec] = []
        if isinstance(raw_files, FileGenerationResult):
            files_to_write = raw_files.files
        elif isinstance(raw_files, list):
            # Validate that every element in the list is a FileSpec
            if all(isinstance(f, FileSpec) for f in raw_files):
                files_to_write = raw_files
            else:
                error_msg = f"Artifact '{artifact_key}' does not contain valid FileSpec objects."
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            error_msg = f"Artifact '{artifact_key}' must be a FileGenerationResult or a list of FileSpec, got {type(raw_files)}."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Render the root template and ensure it's a proper directory path
        rendered_root = render_template(self.config.root, context)
        if not os.path.isdir(rendered_root):
            try:
                os.makedirs(rendered_root, exist_ok=True)
                self.logger.debug(f"Created directory: {rendered_root}")
            except Exception as e:
                error_msg = f"Failed to create root directory '{rendered_root}': {str(e)}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

        # Write each file
        for file_spec in files_to_write:
            # Render file path using the current context
            rendered_file_path = render_template(file_spec.path, context)
            # Combine with rendered root
            full_path = os.path.join(rendered_root, rendered_file_path)
            parent_dir = os.path.dirname(full_path)
            if not os.path.isdir(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    self.logger.debug(f"Created directory: {parent_dir}")
                except Exception as e:
                    error_msg = f"Failed to create directory '{parent_dir}': {str(e)}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
            
            # Log debug information before writing
            self.logger.debug(f"Writing file '{full_path}' with content length {len(file_spec.content)}")
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(file_spec.content)
                self.logger.info(f"Successfully wrote file '{full_path}' (size: {len(file_spec.content)} bytes)")
            except Exception as e:
                error_msg = f"Error writing file '{full_path}': {str(e)}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)


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


