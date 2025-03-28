"""
Executor module for the Recipe Executor CLI tool.

This module is responsible for executing a parsed recipe by iterating
through each step and invoking its execution logic. Errors during step
execution are logged, and the process stops immediately if any step fails.
"""

import logging
from recipe_executor.models import Recipe

def execute_recipe(recipe: Recipe, context: dict | None = None) -> None:
    """
    Execute the provided recipe.

    Args:
        recipe: A validated Recipe object containing a title, description,
                and a list of steps.
        context: An optional dictionary to hold state across steps.

    Raises:
        Exception: Propagates exceptions raised by individual step executions.
    """
    logger = logging.getLogger(__name__)
    context = context or {}

    for step in recipe.steps:
        step_name = step.name or f"{step.type} step"
        logger.info("=== Executing: %s ===", step_name)
        try:
            step.execute(context)
        except Exception as e:
            logger.error("Error in %s: %s", step_name, e)
            logger.error("Recipe execution aborted.")
            raise
        logger.info("Completed: %s", step_name)
