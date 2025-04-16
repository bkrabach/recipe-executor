from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# STEP_REGISTRY is a simple, global dictionary that maps step type names to their implementation classes.
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}
