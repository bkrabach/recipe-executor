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
