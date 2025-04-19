import logging
import os
from typing import Any, Dict

from recipe_executor.protocols import ContextProtocol
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
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ExecuteRecipeConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Import Executor here to avoid circular dependencies
        from recipe_executor.executor import Executor

        # 1. Render recipe_path as template
        try:
            rendered_recipe_path: str = render_template(self.config.recipe_path, context)
        except Exception as e:
            raise ValueError(f"Failed to render recipe_path template '{self.config.recipe_path}': {e}")

        # 2. Render context_overrides as templates
        rendered_context_overrides: Dict[str, str] = {}
        for key, raw_value in self.config.context_overrides.items():
            try:
                rendered_context_overrides[key] = render_template(raw_value, context)
            except Exception as e:
                raise ValueError(f"Failed to render context_overrides['{key}'] template '{raw_value}': {e}")

        # 3. Check if the recipe file exists
        if not os.path.exists(rendered_recipe_path):
            raise FileNotFoundError(f"Sub-recipe file does not exist: {rendered_recipe_path}")

        # 4. Apply context overrides
        for key, override_value in rendered_context_overrides.items():
            context[key] = override_value

        self.logger.info(f"Starting execution of sub-recipe: {rendered_recipe_path}")

        # 5. Execute the sub-recipe with the shared context
        executor = Executor(self.logger)
        try:
            result = await executor.execute(rendered_recipe_path, context)
        except Exception as e:
            raise RuntimeError(f"Error during execution of sub-recipe '{rendered_recipe_path}': {e}") from e

        self.logger.info(f"Finished execution of sub-recipe: {rendered_recipe_path}")
