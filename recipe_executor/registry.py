"""
Step Registry for the Recipe Executor CLI tool.

This module dynamically discovers and registers all step implementations
found in the recipe_executor.steps package. Steps are registered using the
default value of their "type" field, which is later used to map LLM-provided
step types to concrete step classes during recipe parsing.
"""

import importlib
import pkgutil
import inspect

from recipe_executor.models import Step
from recipe_executor import steps

def register_steps() -> dict[str, type[Step]]:
    """
    Discover and register step classes from the recipe_executor.steps package.

    Returns:
        A dictionary mapping each step's "type" field default value to the
        corresponding step class.
    """
    step_registry: dict[str, type[Step]] = {}

    # Iterate over all modules in the 'steps' package.
    for _, module_name, _ in pkgutil.iter_modules(steps.__path__, steps.__name__ + "."):
        module = importlib.import_module(module_name)
        # Iterate over all classes defined in the module.
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Register only subclasses of Step (excluding Step itself).
            if issubclass(obj, Step) and obj is not Step:
                try:
                    # Retrieve the default value of the "type" field
                    step_key = obj.__fields__["type"].default
                except KeyError:
                    raise Exception(f"Step class {obj.__name__} must define a default value for 'type'")
                step_registry[step_key] = obj
    return step_registry

STEP_REGISTRY = register_steps()
