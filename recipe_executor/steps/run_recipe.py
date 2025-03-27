"""
Run Recipe Step implementation for the Recipe Executor CLI tool.

This step runs a nested recipe by reading a Markdown file, parsing it into a Recipe model,
and executing it using the shared context.
"""

import logging
from typing import Optional
from recipe_executor.models import Step

class RunRecipeStep(Step):
    """
    Step that runs another recipe from a given file path.

    Attributes:
        type: The step type identifier ("run_recipe").
        name: An optional name for the step.
        recipe_path: The path to the nested recipe Markdown file.
    """
    type: str = "run_recipe"
    name: Optional[str] = None
    recipe_path: str

    def execute(self, context: dict) -> None:
        """
        Execute the nested recipe by:
          1. Parsing the specified recipe file.
          2. Executing the parsed recipe with the provided context.

        To avoid circular dependency issues, the imports are done locally.

        Args:
            context: A dictionary holding shared state for recipe execution.
        """

        logging.info("Executing RunRecipeStep: running sub-recipe from file '%s'", self.recipe_path)

        try:
            # Use local imports to avoid circular dependency issues.
            from recipe_executor.preprocessor import parse_recipe
            from recipe_executor.executor import execute_recipe

            nested_recipe = parse_recipe(self.recipe_path)
            execute_recipe(nested_recipe, context)
            logging.debug("Sub-recipe '%s' executed successfully", self.recipe_path)

        except Exception as e:
            logging.error("Error executing sub-recipe '%s': %s", self.recipe_path, e)
            raise

    model_config = {"extra": "forbid"}
