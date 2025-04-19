import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Union

from recipe_executor.models import Recipe
from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Stateless executor for loading, validating, and running recipe steps.
    Implements ExecutorProtocol. Does NOT retain state between runs.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger: logging.Logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Load the recipe from any supported type, validate structure, and execute each step sequentially.
        On error, raises ValueError with context about which step or input failed.
        """
        recipe_obj: Recipe = self._load_recipe(recipe)
        self.logger.debug(f"Loaded recipe ({len(recipe_obj.steps)} steps): {recipe_obj.model_dump()}")
        for index, step in enumerate(recipe_obj.steps):
            step_type: str = step.type
            step_config: Dict[str, Any] = step.config or {}
            self.logger.debug(f"Executing step {index}: type='{step_type}', config={step_config}")
            step_class = STEP_REGISTRY.get(step_type)
            if step_class is None:
                raise ValueError(f"Unknown step type '{step_type}' at index {index}")
            try:
                step_instance = step_class(self.logger, step_config)
                result = step_instance.execute(context)
                if hasattr(result, "__await__"):
                    await result
            except Exception as exc:
                raise ValueError(f"Step {index} ('{step_type}') failed: {exc}") from exc
            self.logger.debug(f"Step {index} ('{step_type}') executed successfully.")
        self.logger.debug("All recipe steps executed successfully.")

    def _load_recipe(self, recipe: Union[str, Path, Dict[str, Any], Recipe]) -> Recipe:
        # If already validated model
        if isinstance(recipe, Recipe):
            self.logger.debug("Recipe input is already a Recipe model.")
            return recipe
        # Dict
        if isinstance(recipe, dict):
            self.logger.debug("Recipe input is a dict; validating against Recipe model.")
            try:
                return Recipe.model_validate(recipe)
            except Exception as exc:
                raise ValueError(f"Invalid recipe dictionary: {exc}") from exc
        # If Path or string: determine whether file path or raw JSON
        recipe_str: str
        if isinstance(recipe, Path):
            recipe_str = str(recipe)
        else:
            recipe_str = recipe
        if not isinstance(recipe_str, str):
            raise TypeError(f"Recipe argument must be a str, Path, dict, or Recipe model, not {type(recipe)}")
        if os.path.isfile(recipe_str):
            self.logger.debug(f"Recipe input is a file path: {recipe_str}")
            try:
                with open(recipe_str, "r", encoding="utf-8") as file:
                    loaded = json.load(file)
            except Exception as exc:
                raise ValueError(f"Error reading recipe file '{recipe_str}': {exc}") from exc
            try:
                return Recipe.model_validate(loaded)
            except Exception as exc:
                raise ValueError(f"Invalid recipe in file '{recipe_str}': {exc}") from exc
        else:
            self.logger.debug("Recipe input is a raw JSON string.")
            try:
                loaded = json.loads(recipe_str)
            except Exception as exc:
                raise ValueError(f"Error parsing recipe JSON string: {exc}") from exc
            try:
                return Recipe.model_validate(loaded)
            except Exception as exc:
                raise ValueError(f"Invalid recipe JSON string: {exc}") from exc
