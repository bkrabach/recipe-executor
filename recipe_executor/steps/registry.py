from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# The global step registry mapping step type names to implementation classes.
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}
