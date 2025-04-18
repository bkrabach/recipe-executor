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
    Executor component for running JSON-defined recipes.

    Implements ExecutorProtocol. Stateless between executions.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger: logging.Logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Execute a recipe on the given context.
        Args:
            recipe: Recipe definition (file path, JSON string, dict, Path, or Recipe).
            context: Shared context object implementing ContextProtocol.
        Raises:
            TypeError: Unsupported recipe argument type.
            ValueError: Loading/parsing/validation/step errors.
        """
        # Step 1: Load and parse the recipe
        loaded_recipe: Optional[Recipe] = None
        recipe_source: str = ""
        recipe_obj: Optional[Dict[str, Any]] = None

        # Accept Path objects as file paths as well
        if isinstance(recipe, Path):
            recipe = str(recipe)

        if isinstance(recipe, Recipe):
            loaded_recipe = recipe
            recipe_source = "Recipe object"
        elif isinstance(recipe, dict):
            try:
                loaded_recipe = Recipe.model_validate(recipe)
                recipe_source = "dict"
            except Exception as exc:
                raise ValueError(f"Recipe validation failed from dict: {exc}") from exc
        elif isinstance(recipe, str):
            # Is recipe a file path?
            if os.path.isfile(recipe):
                try:
                    with open(recipe, "r", encoding="utf-8") as file:
                        recipe_str = file.read()
                    recipe_obj = json.loads(recipe_str)
                    loaded_recipe = Recipe.model_validate(recipe_obj)
                    recipe_source = f"file: {recipe}"
                except Exception as exc:
                    raise ValueError(f"Failed to load or parse recipe file '{recipe}': {exc}") from exc
            else:
                # Treat as raw JSON string
                try:
                    recipe_obj = json.loads(recipe)
                    loaded_recipe = Recipe.model_validate(recipe_obj)
                    recipe_source = "JSON string"
                except Exception as exc:
                    raise ValueError(f"Failed to load recipe from JSON string: {exc}") from exc
        else:
            raise TypeError(
                f"Unsupported recipe argument type: {type(recipe)}. "
                "Expected dict, str (filepath/JSON), Path, or Recipe."
            )

        if not loaded_recipe or not isinstance(loaded_recipe, Recipe):
            raise ValueError("Recipe could not be loaded or validated.")

        if not hasattr(loaded_recipe, "steps") or not isinstance(loaded_recipe.steps, list):
            raise ValueError("Recipe is missing required 'steps' list after validation.")

        num_steps: int = len(loaded_recipe.steps)

        self.logger.debug(f"Loaded recipe from {recipe_source} with {num_steps} steps.")
        self.logger.debug(f"Recipe content (summary): {loaded_recipe.model_dump()}")

        # Step 2: Sequentially execute steps
        for step_index, step in enumerate(loaded_recipe.steps):
            if not isinstance(step, RecipeStep):
                try:
                    step = RecipeStep.model_validate(step)
                except Exception as exc:
                    raise ValueError(f"Invalid step structure at index {step_index}: {exc}") from exc

            step_type: str = step.type
            step_config: Dict[str, Any] = step.config

            self.logger.debug(f"Executing step {step_index + 1}/{num_steps}: type='{step_type}', config={step_config}")

            if step_type not in STEP_REGISTRY:
                raise ValueError(
                    f"Unknown step type '{step_type}' at index {step_index}. Check that the step type is registered."
                )

            step_class = STEP_REGISTRY[step_type]
            try:
                # StepProtocol interface: __init__(logger, config)
                step_instance = step_class(self.logger, step_config)
                # If the step instance's execute is a coroutine (async), await it
                import inspect

                exec_func = getattr(step_instance, "execute")
                if callable(exec_func):
                    result = exec_func(context)
                    if inspect.isawaitable(result):
                        await result
                else:
                    raise ValueError(
                        f"Step instance for type '{step_type}' at index {step_index} does not have an executable 'execute' method."
                    )
            except Exception as exc:
                raise ValueError(f"Step {step_index + 1} ('{step_type}') failed: {exc}") from exc
            self.logger.debug(f"Step {step_index + 1} ('{step_type}') executed successfully.")

        self.logger.debug(f"All {num_steps} steps executed successfully.")
