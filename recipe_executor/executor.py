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
