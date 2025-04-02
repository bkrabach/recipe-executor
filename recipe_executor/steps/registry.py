from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global registry for step implementations
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}
