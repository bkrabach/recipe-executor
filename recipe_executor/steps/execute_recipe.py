import logging
import os
from typing import Any, Dict, Union

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
    def __init__(self, config: Union[Dict[str, Any], ExecuteRecipeConfig], logger: logging.Logger) -> None:
        # Ensure config is an ExecuteRecipeConfig object, not a raw dict
        if not isinstance(config, ExecuteRecipeConfig):
            config = ExecuteRecipeConfig(**config)
        super().__init__(logger, config)

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute a sub-recipe by rendering its path and applying any context overrides.

        Args:
            context (ContextProtocol): The shared execution context.

        Raises:
            ValueError: If the sub-recipe file does not exist.
            RuntimeError: If an error occurs during sub-recipe execution.
        """
        # Import Executor within execute to avoid circular dependencies
        from recipe_executor.executor import Executor

        # Render the sub-recipe path template using the current context
        rendered_recipe_path = render_template(self.config.recipe_path, context)

        # Apply context overrides with template rendering
        for key, value in self.config.context_overrides.items():
            rendered_value = render_template(value, context)
            context[key] = rendered_value

        # Validate that the sub-recipe file exists
        if not os.path.isfile(rendered_recipe_path):
            error_message = f"Sub-recipe file not found: {rendered_recipe_path}"
            self.logger.error(error_message)
            raise ValueError(error_message)

        self.logger.info(f"Starting sub-recipe execution: {rendered_recipe_path}")

        try:
            executor = Executor(self.logger)
            # The executor uses the same context which may be updated by the sub-recipe
            await executor.execute(rendered_recipe_path, context)
        except Exception as exc:
            error_message = f"Error executing sub-recipe '{rendered_recipe_path}': {str(exc)}"
            self.logger.error(error_message)
            raise RuntimeError(error_message) from exc

        self.logger.info(f"Completed sub-recipe execution: {rendered_recipe_path}")
