from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global dictionary to store step registrations
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}
