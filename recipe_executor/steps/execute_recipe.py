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
