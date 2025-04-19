from typing import Dict, Type
from recipe_executor.steps.base import BaseStep

# Simple, central registry for step implementations.
# Maps step type name (str) to the step implementation class (subclass of BaseStep).
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}
