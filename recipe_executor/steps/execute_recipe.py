import os
import logging
from typing import Any, Dict, Optional
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
        # Render the recipe path template with the current context
        rendered_recipe_path: str = render_template(self.config.recipe_path, context)
        
        # Render each context_override value as a template using the current context
        rendered_context_overrides: Dict[str, Any] = {}
        for key, value in self.config.context_overrides.items():
            rendered_context_overrides[key] = render_template(value, context)

        # Validate sub-recipe file exists
        if not os.path.isfile(rendered_recipe_path):
            self.logger.error(f"Sub-recipe file not found: {rendered_recipe_path}")
            raise FileNotFoundError(f"Sub-recipe file not found: {rendered_recipe_path}")

        # Apply context overrides to the shared context before execution
        for key, value in rendered_context_overrides.items():
            context[key] = value

        self.logger.info(f"Executing sub-recipe: {rendered_recipe_path}")
        try:
            # Import Executor inside the method to avoid circular dependencies
            from recipe_executor.executor import Executor
            executor = Executor(self.logger)
            await executor.execute(rendered_recipe_path, context)
        except Exception as exc:
            self.logger.error(f"Error executing sub-recipe '{rendered_recipe_path}': {exc}")
            raise
        self.logger.info(f"Sub-recipe completed: {rendered_recipe_path}")
