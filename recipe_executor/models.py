"""
Domain models for the Recipe Executor CLI tool.

This module defines the core Pydantic models for representing recipes and steps.
Each step must be implemented as a subclass of Step and provide its own execution logic.
"""

from pydantic import BaseModel
from typing import Any, Optional, List

class Step(BaseModel):
    """
    Base class for all recipe steps.

    Attributes:
        type: A string indicating the step type.
        name: An optional name for the step.
    """
    type: str
    name: Optional[str] = None

    def execute(self, context: dict) -> Any:
        """
        Execute the step using the provided context.

        Args:
            context: A dictionary containing shared state for recipe execution.

        Returns:
            The result of the step execution.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")

    class Config:
        extra = "forbid"


class Recipe(BaseModel):
    """
    Represents a complete recipe.

    Attributes:
        title: The title of the recipe.
        description: An optional description of the recipe.
        steps: A list of steps that constitute the recipe.
    """
    title: str
    description: Optional[str] = None
    steps: List[Step]

    class Config:
        extra = "forbid"
