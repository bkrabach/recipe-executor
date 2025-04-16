import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from recipe_executor.models import Recipe, RecipeStep
from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Executor implementation adhering to ExecutorProtocol. Stateless class for executing JSON-based recipes using a shared context.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger: logging.Logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any]],
        context: ContextProtocol,
    ) -> None:
        raw_recipe: Any = None
        recipe_source: str = ""
        # Recipe loading
        if isinstance(recipe, Path):
            recipe_path: str = str(recipe)
        else:
            recipe_path: Optional[str] = None
            if isinstance(recipe, str):
                recipe_path = recipe

        if isinstance(recipe, dict):
            raw_recipe = recipe
            recipe_source = "dict"
        elif isinstance(recipe, Path) or (isinstance(recipe, str) and os.path.isfile(recipe_path)):
            try:
                with open(recipe_path, "r", encoding="utf-8") as f:
                    raw_recipe = json.load(f)
                recipe_source = f"file: {recipe_path}"
            except Exception as e:
                raise ValueError(f"Failed to load recipe file '{recipe_path}': {e}")
        elif isinstance(recipe, str):
            try:
                raw_recipe = json.loads(recipe)
                recipe_source = "json string"
            except Exception as e:
                raise ValueError(f"Failed to parse recipe JSON string: {e}")
        else:
            raise TypeError(
                f"Unsupported recipe type: {type(recipe).__name__}. Must be dict, file path, Path, or JSON string."
            )

        self.logger.debug(f"Loaded recipe from {recipe_source}.")
        self.logger.debug(f"Recipe content: {repr(raw_recipe)[:1000]}")

        # Model validation
        try:
            recipe_model = Recipe.model_validate(raw_recipe)
        except Exception as e:
            raise ValueError(f"Invalid recipe structure: {e}")

        steps = recipe_model.steps
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError("Recipe must contain a non-empty 'steps' list.")

        self.logger.debug(f"Executing recipe with {len(steps)} steps.")

        for step_index, step in enumerate(steps):
            if not isinstance(step, RecipeStep):
                try:
                    step = RecipeStep.model_validate(step)
                except Exception as e:
                    raise ValueError(f"Invalid step at index {step_index}: {e}")
            step_type = step.type
            step_config = step.config
            self.logger.debug(f"Step {step_index}: type='{step_type}' config={step_config}")
            step_class = STEP_REGISTRY.get(step_type)
            if step_class is None:
                raise ValueError(f"Unknown step type '{step_type}' at index {step_index}.")
            try:
                # Step __init__ takes config and logger
                step_instance = step_class(step_config, self.logger)
                await step_instance.execute(context)
                self.logger.debug(f"Step {step_index} ('{step_type}') executed successfully.")
            except Exception as err:
                raise ValueError(f"Execution failed at step {step_index} ('{step_type}') with error: {err}") from err

        self.logger.debug("All recipe steps executed successfully.")
