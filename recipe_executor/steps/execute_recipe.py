import logging
import os
from typing import Dict, Optional

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
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
    """Step to execute a sub-recipe with an optional context override.

    This step uses template rendering to dynamically resolve the recipe path and any context overrides,
    then executes the sub-recipe using the provided executor. The same executor instance is used to ensure
    consistency between parent and sub-recipe execution.
    """

    def __init__(
        self, config: dict, logger: Optional[logging.Logger] = None, executor: Optional[ExecutorProtocol] = None
    ) -> None:
        """Initialize the ExecuteRecipeStep.

        Args:
            config (dict): The step configuration as a dictionary. It must contain the recipe_path, and may
                           contain context_overrides.
            logger: Optional logger instance.
            executor: Optional executor instance. If not provided, a new Executor instance will be created.
        """
        super().__init__(ExecuteRecipeConfig(**config), logger)
        # Use the provided executor or create a new one if none is provided.

        if executor is None:
            from recipe_executor.executor import Executor

            self.executor = Executor()
        else:
            self.executor = executor

    def execute(self, context: ContextProtocol) -> None:
        """Execute the sub-recipe defined in the configuration.

        This method applies template rendering to the recipe path and context overrides, ensures that the
        sub-recipe file exists, applies the context overrides, and then executes the sub-recipe using the
        shared executor instance. Logging is performed at the start and completion of sub-recipe execution.

        Args:
            context (ContextProtocol): The shared execution context.

        Raises:
            FileNotFoundError: If the resolved sub-recipe file does not exist.
            Exception: Propagates any errors that occur during sub-recipe execution.
        """
        try:
            # Render the recipe path using the current context
            rendered_recipe_path = render_template(self.config.recipe_path, context)

            # Verify that the sub-recipe file exists
            if not os.path.exists(rendered_recipe_path):
                error_message = f"Sub-recipe file not found: {rendered_recipe_path}"
                self.logger.error(error_message)
                raise FileNotFoundError(error_message)

            # Render context overrides and apply them before execution
            rendered_overrides: Dict[str, str] = {}
            for key, value in self.config.context_overrides.items():
                rendered_value = render_template(value, context)
                rendered_overrides[key] = rendered_value
                # Update the context with the override
                context[key] = rendered_value

            # Log the start of sub-recipe execution
            self.logger.info(f"Starting execution of sub-recipe: {rendered_recipe_path}")

            # Execute the sub-recipe using the shared executor instance
            self.executor.execute(rendered_recipe_path, context)

            # Log the successful completion of sub-recipe execution
            self.logger.info(f"Completed execution of sub-recipe: {rendered_recipe_path}")
        except Exception as error:
            # Log the error with sub-recipe path for debugging
            self.logger.error(f"Error executing sub-recipe '{self.config.recipe_path}': {str(error)}")
            raise
