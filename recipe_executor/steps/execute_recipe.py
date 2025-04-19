import logging
from pathlib import Path
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
        # Import inside method to avoid circular dependencies
        from recipe_executor.executor import Executor

        # Render template for recipe_path
        recipe_path: str = render_template(self.config.recipe_path, context)
        context_overrides_rendered: Dict[str, str] = {}

        # Render all context_overrides values as templates
        for key, value in self.config.context_overrides.items():
            context_overrides_rendered[key] = render_template(value, context)

        # Apply context_overrides to the shared context
        for key, value in context_overrides_rendered.items():
            context[key] = value

        # Check if file exists
        recipe_file_path = Path(recipe_path)
        if not recipe_file_path.is_file():
            self.logger.error(f"Sub-recipe file not found: {recipe_path}")
            raise FileNotFoundError(f"Sub-recipe file not found for path: {recipe_path}")

        # Log execution start
        self.logger.info(f"Executing sub-recipe: {recipe_path}")

        try:
            # Use the same executor instance as parent (if possible)
            # But since step does not have a reference, create new instance (stateless)
            executor = Executor(self.logger)
            await executor.execute(str(recipe_file_path), context)
        except Exception as e:
            self.logger.error(f"Error in sub-recipe {recipe_path}: {e}")
            raise

        # Log execution end
        self.logger.info(f"Completed sub-recipe: {recipe_path}")
