from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Central registry for mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}
