"""
Core data models for the Recipe Executor system.
Defines file and recipe schemas using Pydantic for validation.
"""

from typing import Dict, List

from pydantic import BaseModel


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file.
    """

    path: str
    content: str


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """

    type: str
    config: Dict


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]
