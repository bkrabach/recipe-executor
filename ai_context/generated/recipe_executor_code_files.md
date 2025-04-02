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
    Shared state container for the Recipe Executor system. It provides a dictionary-like interface to store and retrieve artifacts and configuration values.
    """
    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store.
            config: Configuration values.
        """
        # Copy input dictionaries to avoid external modification
        self._artifacts: Dict[str, Any] = artifacts.copy() if artifacts is not None else {}
        self.config: Dict[str, Any] = config.copy() if config is not None else {}

    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-like setting of artifacts."""
        self._artifacts[key] = value

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access to artifacts. Raises KeyError with descriptive message if key is missing."""
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Artifact with key '{key}' not found in context.")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get an artifact with an optional default value."""
        return self._artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in artifacts."""
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        """Iterate over artifact keys."""
        # Convert dict_keys to a list for safe iteration
        return iter(list(self._artifacts.keys()))

    def keys(self) -> Iterator[str]:
        """Return an iterator over the keys of artifacts."""
        return self.__iter__()

    def __len__(self) -> int:
        """Return the number of artifacts."""
        return len(self._artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """Return a copy of the artifacts as a dictionary to ensure immutability."""
        return self._artifacts.copy()

    def clone(self) -> "Context":
        """
        Return a deep copy of the current context, including artifacts and configuration.
        This ensures data isolation between different executions.
        """
        cloned_artifacts = copy.deepcopy(self._artifacts)
        cloned_config = copy.deepcopy(self.config)
        return Context(artifacts=cloned_artifacts, config=cloned_config)


=== File: recipe_executor/executor.py ===
import os
import json
import logging
from typing import Any, Dict, List, Union, Optional

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor:
    """
    Executor component for the Recipe Executor system.

    Loads recipe definitions, validates their structure, and executes steps sequentially
    using the provided context.
    """

    def execute(
        self,
        recipe: Union[str, Dict[str, Any]],
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
            ValueError: If recipe format is invalid or a step is improperly structured
            TypeError: If recipe type is not supported
        """
        # Setup logger
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.hasHandlers():
                # Basic logging configuration if no handlers are attached
                logging.basicConfig(level=logging.DEBUG)

        logger.debug("Starting recipe execution.")

        # Load recipe data based on type
        data: Dict[str, Any]
        if isinstance(recipe, dict):
            data = recipe
            logger.debug("Recipe provided as a dictionary.")
        elif isinstance(recipe, str):
            # Check if the string is a file path
            if os.path.exists(recipe):
                logger.debug(f"Loading recipe from file: {recipe}")
                try:
                    with open(recipe, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    raise ValueError(f"Failed to load recipe from file '{recipe}': {e}")
            else:
                # Attempt to parse recipe as a JSON string
                logger.debug("Attempting to parse recipe as JSON string.")
                try:
                    data = json.loads(recipe)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid recipe format. Unable to parse JSON string: {e}")
        else:
            raise TypeError("Recipe must be either a file path, JSON string, or dictionary")

        logger.debug(f"Parsed recipe: {data}")
        
        # Validate recipe structure
        if 'steps' not in data or not isinstance(data['steps'], list):
            raise ValueError("Invalid recipe structure: Missing or invalid 'steps' key")

        steps: List[Dict[str, Any]] = data['steps']

        # Execute each step sequentially
        for index, step in enumerate(steps):
            logger.debug(f"Processing step {index + 1}/{len(steps)}: {step}")
            # Validate that the step has a 'type'
            if 'type' not in step:
                raise ValueError(f"Step at index {index} is missing the 'type' field")
            step_type = step['type']

            # Lookup step in the registry
            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {index}")

            step_class = STEP_REGISTRY[step_type]

            try:
                # Instantiate the step and execute it
                step_instance = step_class(step, logger)
                logger.debug(f"Executing step of type '{step_type}'")
                step_instance.execute(context)
                logger.debug(f"Completed step {index + 1} successfully.")
            except Exception as e:
                logger.error(f"Error executing step at index {index} (type '{step_type}'): {e}")
                # Include original exception details for debugging purposes
                raise ValueError(f"Step execution failed at index {index} (type '{step_type}'): {e}") from e

        logger.debug("Recipe execution completed successfully.")


=== File: recipe_executor/llm.py ===
import logging
import os
import time
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# For Azure OpenAI use our internal utility
from recipe_executor.llm_utils.azure_openai import get_openai_model as get_azure_openai_model

from recipe_executor.models import FileGenerationResult


# Use DEFAULT_MODEL env variable if provided, otherwise default to 'openai:gpt-4o'
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai:gpt-4o")


def get_model(model_id: Optional[str] = None):
    """
    Initialize and return a PydanticAI model instance based on the standardized model identifier string.
    Expected formats:
      - openai:model_name
      - anthropic:model_name
      - gemini:model_name
      - azure:model_name or azure:model_name:deployment_name
    """
    model_id = model_id or DEFAULT_MODEL
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model_id format: {model_id}")

    provider = parts[0].lower()
    if provider == "openai":
        model_name = parts[1]
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        model_name = parts[1]
        return AnthropicModel(model_name)
    elif provider == "gemini":
        model_name = parts[1]
        return GeminiModel(model_name)
    elif provider == "azure":
        model_name = parts[1]
        # If deployment name is not provided, default deployment is same as model name
        deployment_name = parts[2] if len(parts) >= 3 else model_name
        return get_azure_openai_model(model_name, deployment_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize a PydanticAI Agent using the model specified in model_id (or default).
    The agent is configured to produce structured outputs of type FileGenerationResult.
    """
    model_instance = get_model(model_id)
    return Agent(model_instance, result_type=FileGenerationResult)


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt using the specified model (or default model if not provided).

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier, in the format 'provider:model_name' or 'provider:model_name:deployment_name'.
                              Defaults to the DEFAULT_MODEL if None.
        logger (Optional[logging.Logger]): Logger instance, defaults to 'RecipeExecutor' logger.

    Returns:
        FileGenerationResult: The structured output containing generated files and optional commentary.

    Raises:
        Exception: Propagates exceptions from the LLM call after logging.
    """
    logger = logger or logging.getLogger("RecipeExecutor")
    logger.info(f"Calling LLM with model: {model or DEFAULT_MODEL}")
    logger.debug(f"LLM request payload: {prompt}")
    start = time.monotonic()
    try:
        agent = get_agent(model)
        result = agent.run_sync(prompt)
    except Exception as e:
        logger.error(f"LLM call failed: {e}", exc_info=True)
        raise
    elapsed = time.monotonic() - start
    logger.info(f"LLM call completed in {elapsed:.2f} seconds")
    logger.debug(f"LLM response payload: {result}")
    return result.data


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    res = call_llm("Generate a Python utility module for handling dates.")
    print(res)


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
import logging
import os
import sys


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If the log directory cannot be created or log files cannot be opened.
    """
    # Define a consistent log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Create logger with the name 'RecipeExecutor'
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Capture all levels; individual handlers will filter

    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Attempt to create log directory if it doesn't exist
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        # Logging not yet configured; use print for error message
        print(f"Error: Failed to create log directory '{log_dir}': {e}")
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Setup file handlers for debug, info, and error levels
    try:
        # Debug file handler: logs all messages (DEBUG and above)
        debug_file = os.path.join(log_dir, "debug.log")
        fh_debug = logging.FileHandler(debug_file, mode='w')
        fh_debug.setLevel(logging.DEBUG)
        fh_debug.setFormatter(formatter)
        logger.addHandler(fh_debug)

        # Info file handler: logs INFO and above messages
        info_file = os.path.join(log_dir, "info.log")
        fh_info = logging.FileHandler(info_file, mode='w')
        fh_info.setLevel(logging.INFO)
        fh_info.setFormatter(formatter)
        logger.addHandler(fh_info)

        # Error file handler: logs ERROR and above messages
        error_file = os.path.join(log_dir, "error.log")
        fh_error = logging.FileHandler(error_file, mode='w')
        fh_error.setLevel(logging.ERROR)
        fh_error.setFormatter(formatter)
        logger.addHandler(fh_error)
    except Exception as e:
        print(f"Error: Failed to set up file handlers: {e}")
        raise Exception(f"Failed to set up file handlers: {e}")

    # Setup console handler for stdout with INFO level and above
    try:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    except Exception as e:
        print(f"Error: Failed to set up console handler: {e}")
        raise Exception(f"Failed to set up console handler: {e}")

    # Log a debug message indicating logger initialization
    logger.debug(f"Logger initialized. Log directory: {log_dir}")

    return logger


=== File: recipe_executor/main.py ===
import sys
import time
import traceback
import argparse
from typing import List, Dict

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.logger import init_logger
from executor import Executor  # Importing Executor from executor to avoid circular import issues


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for recipe execution."""
    parser = argparse.ArgumentParser(description='Execute a recipe with the Recipe Executor Tool.')
    parser.add_argument('recipe_path', type=str, help='Path to the recipe file to execute.')
    parser.add_argument('--log-dir', type=str, default='logs', help='Directory for log files (default: logs)')
    parser.add_argument('--context', type=str, action='append', default=[],
                        help='Context key=value pair. Can be specified multiple times.')
    return parser.parse_args()


def parse_context(context_args: List[str]) -> Dict[str, str]:
    """Parse context key=value pairs from the command line into a dictionary."""
    context: Dict[str, str] = {}
    for arg in context_args:
        if '=' not in arg:
            raise ValueError(f"Invalid context format for '{arg}'. Expected format key=value.")
        key, value = arg.split('=', 1)
        context[key] = value
    return context


def main() -> None:
    # Load environment variables from .env files
    load_dotenv()

    args = parse_arguments()

    # Initialize logger early
    logger = init_logger(args.log_dir)
    logger.debug(f"Main function started with arguments: {args}")

    start_time = time.time()
    try:
        # Parse context values from command line
        context_dict = parse_context(args.context)
        logger.debug(f"Parsed context values: {context_dict}")

        # Create a clean context with command-line provided artifacts
        context = Context(artifacts=context_dict)

        # Instantiate Executor and execute the specified recipe
        executor = Executor()
        logger.info('Starting Recipe Executor Tool')
        logger.info(f"Executing recipe: {args.recipe_path}")
        executor.execute(args.recipe_path, context, logger=logger)

        total_time = time.time() - start_time
        logger.info(f"Recipe executed successfully in {total_time:.2f} seconds.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()


=== File: recipe_executor/models.py ===
from typing import List, Optional, Dict, Any

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
        config (Dict[str, Any]): Dictionary containing configuration for the step.
    """
    type: str
    config: Dict[str, Any]


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    steps: List[RecipeStep]


=== File: recipe_executor/steps/__init__.py ===
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


=== File: recipe_executor/steps/base.py ===
import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from recipe_executor.context import Context


class StepConfig(BaseModel):
    """
    Base class for step configurations.

    Extend this class to create custom configuration models for steps.
    """
    pass


# Type variable for generic configuration type
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(Generic[ConfigType], ABC):
    """
    Base abstract class for all steps in the Recipe Executor system.

    Each concrete step must inherit from this class and implement the execute method.

    Args:
        config (ConfigType): The step configuration object validated via Pydantic.
        logger (Optional[logging.Logger]): Logger instance, defaults to 'RecipeExecutor' if not provided.
    """
    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger: logging.Logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config.dict()}" if hasattr(self.config, 'dict') else f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Execute the step using the provided context.

        Args:
            context (Context): The execution context for the recipe, enabling data sharing between steps.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        # Subclasses must override this method.
        raise NotImplementedError(f"Each step must implement the execute method. {self.__class__.__name__} did not.")


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
from typing import Any

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
    GenerateWithLLMStep is responsible for generating content using a large language model (LLM).
    It renders the prompt, model identifier, and artifact key from the provided context, calls the LLM,
    and stores the returned FileGenerationResult in the context under the rendered artifact key.

    The step follows a minimalistic design:
      - It uses template rendering for dynamic prompt and model resolution.
      - It allows the artifact key to be templated for dynamic context storage.
      - It logs details before and after calling the LLM.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        """
        Initialize the GenerateWithLLMStep with its configuration and an optional logger.

        Args:
            config (dict): A dictionary containing the configuration for the step.
            logger (Optional[Any]): Logger instance to use for logging. Defaults to a logger with name "RecipeExecutor".
        """
        super().__init__(GenerateLLMConfig(**config), logger or logging.getLogger("RecipeExecutor"))

    def execute(self, context: Context) -> None:
        """
        Execute the LLM generation step using the provided context.

        This method performs the following:
          1. Dynamically render artifact key, prompt, and model values from the context.
          2. Log debug and info messages with details of the rendered parameters.
          3. Call the LLM using the rendered prompt and model.
          4. Store the resulting FileGenerationResult in the context under the rendered artifact key.
          5. Handle and log any errors encountered during generation.

        Args:
            context (Context): The shared context for execution containing input data and used for storing results.

        Raises:
            Exception: Propagates any exception encountered during processing, after logging the error.
        """
        try:
            # Process the artifact key using templating if needed
            artifact_key = self.config.artifact
            if "{{" in artifact_key and "}}" in artifact_key:
                artifact_key = render_template(artifact_key, context)

            # Render the prompt and model values using the current context
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)

            # Log the LLM call details
            self.logger.info(f"Calling LLM with prompt for artifact: {artifact_key}")
            self.logger.debug(f"Rendered prompt: {rendered_prompt}")
            self.logger.debug(f"Rendered model: {rendered_model}")

            # Call the LLM to generate content
            response = call_llm(rendered_prompt, rendered_model, logger=self.logger)

            # Store the LLM response in the context
            context[artifact_key] = response
            self.logger.debug(f"LLM response stored in context under '{artifact_key}'")

        except Exception as e:
            # Log detailed error information for debugging
            self.logger.error(f"Failed to generate content using LLM. Error: {e}")
            raise


=== File: recipe_executor/steps/parallel.py ===
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

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
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep executes multiple sub-recipes concurrently in isolated contexts.

    It uses a ThreadPoolExecutor to run substeps in parallel with optional concurrency limits
    and launch delays. Implements fail-fast behavior: if any substep fails, execution aborts
    and propagates the first encountered exception.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize the base step with ParallelConfig
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the parallel step: launch substeps concurrently and wait for completion.

        Args:
            context (Context): The execution context.

        Raises:
            Exception: Propagates the first encountered exception from any substep.
        """
        total_substeps: int = len(self.config.substeps)
        self.logger.info(f"ParallelStep starting with {total_substeps} substep(s).")

        # Determine max_workers: if max_concurrency is 0 or greater than total, use total_substeps
        max_workers: int = self.config.max_concurrency if self.config.max_concurrency > 0 else total_substeps

        futures = []
        first_exception: Optional[Exception] = None
        executor = ThreadPoolExecutor(max_workers=max_workers)

        try:
            # Submit tasks sequentially and respect delay between launches
            for index, sub_config in enumerate(self.config.substeps):
                # Fail-fast: if an error was encountered, stop launching new substeps
                if first_exception is not None:
                    self.logger.error("Aborting submission of further substeps due to previous error.")
                    break

                # Clone context for isolation
                sub_context = context.clone()

                # Validate step type
                step_type = sub_config.get("type")
                if step_type not in STEP_REGISTRY:
                    err_msg = f"Unrecognized step type '{step_type}' in substep at index {index}."
                    self.logger.error(err_msg)
                    raise ValueError(err_msg)

                # Instantiate the substep using the registry
                step_class = STEP_REGISTRY[step_type]
                substep_instance = step_class(sub_config, logger=self.logger)

                self.logger.info(f"Launching substep {index} (type: {step_type}).")

                # Submit the substep execution as a separate task using the cloned context
                future = executor.submit(self._execute_substep, substep_instance, sub_context, index)
                futures.append(future)

                # If a launch delay is configured and this is not the last substep, sleep
                if self.config.delay > 0 and index < total_substeps - 1:
                    time.sleep(self.config.delay)

            # Wait for all submitted tasks to complete
            for future in as_completed(futures):
                try:
                    # This will re-raise any exception from the substep
                    future.result()
                except Exception as exc:
                    self.logger.error(f"A substep failed with error: {exc}", exc_info=True)
                    first_exception = exc
                    # Fail-fast: stop waiting on additional substeps
                    break

            # If an exception was encountered, cancel any pending substeps
            if first_exception is not None:
                self.logger.error("Fail-fast activated. Cancelling pending substeps.")
                for fut in futures:
                    fut.cancel()
                raise first_exception

            self.logger.info("ParallelStep completed all substeps successfully.")

        finally:
            executor.shutdown(wait=True)

    def _execute_substep(self, step_instance: BaseStep, context: Context, index: int) -> None:
        """
        Execute an individual substep with its cloned context.

        Args:
            step_instance (BaseStep): The substep instance to execute.
            context (Context): The cloned context for this substep.
            index (int): Index of the substep, for logging purposes.

        Raises:
            Exception: Propagates any exception encountered during execution of the substep.
        """
        self.logger.info(f"Substep {index} started.")
        try:
            step_instance.execute(context)
            self.logger.info(f"Substep {index} completed successfully.")
        except Exception as e:
            self.logger.error(f"Substep {index} failed with error: {e}", exc_info=True)
            raise e


=== File: recipe_executor/steps/read_file.py ===
import os
import logging
from typing import Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
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
    ReadFileStep component reads a file from the filesystem and stores its contents into the execution context.

    This step renders the file path using the given context, reads the contents of the file, and assigns it to a specified key.
    It handles missing files based on the 'optional' configuration flag. If the file is optional and not found,
    an empty string is stored in the context, otherwise a FileNotFoundError is raised.
    """
    
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert the provided config dictionary into a ReadFileConfig instance and initialize the base step
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the ReadFileStep:
          - Render the file path using template rendering
          - Check for file existence
          - Read file content using UTF-8 encoding
          - Store the content into the context under the specified artifact key
          - Handle missing files based on the 'optional' flag

        Args:
            context (Context): The shared execution context.

        Raises:
            FileNotFoundError: If the file is not found and the step is not marked as optional.
        """
        # Render the file path using values from the execution context
        path: str = render_template(self.config.path, context)
        self.logger.debug(f"Rendered file path: {path}")

        # Check if the file exists at the rendered path
        if not os.path.exists(path):
            if self.config.optional:
                self.logger.warning(f"Optional file not found at path: {path}, continuing without file.")
                context[self.config.artifact] = ""
                return
            else:
                error_msg: str = f"ReadFileStep: file not found at path: {path}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        # File exists, attempt to read its contents with UTF-8 encoding
        self.logger.info(f"Reading file from path: {path}")
        try:
            with open(path, "r", encoding="utf-8") as file:
                content: str = file.read()
        except Exception as e:
            self.logger.error(f"Error reading file at {path}: {e}")
            raise

        # Store the file content into the context under the specified artifact key
        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global step registry mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import logging
import os
from typing import List, Optional

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to ".".
    """

    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    WriteFilesStep writes generated files to disk based on content from the execution context.
    It handles template rendering, directory creation, and logging of file operations.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict config to WriteFilesConfig via Pydantic
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the write files step.

        Retrieves an artifact from the context, validates its type, and writes the corresponding files to disk.
        It supports both FileGenerationResult and a list of FileSpec objects.

        Args:
            context (Context): The execution context containing artifacts and configuration.

        Raises:
            ValueError: If the artifact is missing or if the root path rendering fails.
            TypeError: If the artifact is not a FileGenerationResult or a list of FileSpec objects.
            IOError: If an error occurs during file writing.
        """
        # Retrieve the artifact from the context
        data = context.get(self.config.artifact)
        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine the list of files to write
        if isinstance(data, FileGenerationResult):
            files: List[FileSpec] = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        # Render the root output path using template rendering
        try:
            output_root = render_template(self.config.root, context)
        except Exception as e:
            raise ValueError(f"Error rendering root path '{self.config.root}': {str(e)}")

        # Process each file: resolve file path, create directories, and write the file
        for file in files:
            try:
                # Render the file path; file.path may contain template variables
                rel_path = render_template(file.path, context)
                full_path = os.path.join(output_root, rel_path)

                # Ensure that the parent directory exists
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

                # Write the file content using UTF-8 encoding
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)

                self.logger.info(f"Wrote file: {full_path}")
            except Exception as e:
                self.logger.error(f"Error writing file '{file.path}': {str(e)}")
                raise IOError(f"Error writing file '{file.path}': {str(e)}")


=== File: recipe_executor/utils.py ===
import logging
from typing import Any, Dict

from liquid import Template

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def render_template(text: str, context: Any) -> str:
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
    # Convert context artifacts to a dict of strings
    try:
        context_artifacts: Dict[str, Any] = context.as_dict()
    except AttributeError as e:
        raise ValueError(f"Context provided does not have an as_dict() method: {e}")

    # Convert all values to string
    str_context = {key: str(value) for key, value in context_artifacts.items()}
    logger.debug(f"Rendering template: {text}")
    logger.debug(f"Context keys used: {list(str_context.keys())}")

    try:
        template = Template(text)
        result = template.render(**str_context)
        return result
    except Exception as e:
        error_message = f"Error rendering template: {e}. Template: '{text}' with context: {str_context}"
        logger.debug(error_message)
        raise ValueError(error_message) from e


