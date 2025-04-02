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
