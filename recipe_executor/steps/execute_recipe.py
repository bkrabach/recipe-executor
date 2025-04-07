import os
from typing import Any, Dict

from recipe_executor.context import Context
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
            context.executor.execute(rendered_recipe_path, context, self.logger)

            # Log completion of sub-recipe execution
            self.logger.info(f"Completed execution of sub-recipe: {rendered_recipe_path}")

        except Exception as e:
            error_msg = f"Error executing sub-recipe '{self.config.recipe_path}': {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
