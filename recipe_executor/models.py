from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """
    path: str = Field(..., description="Relative path where the file should be written")
    content: str = Field(..., description="The content of the file")


class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """
    files: List[FileSpec] = Field(..., description="List of files to generate")
    commentary: Optional[str] = Field(None, description="Optional commentary from the LLM")


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """
    type: str = Field(..., description="The type of the recipe step")
    config: Dict = Field(..., description="Dictionary containing configuration for the step")


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    steps: List[RecipeStep] = Field(..., description="List of steps in the recipe")
