# recipe_executor/models.py

from pydantic import BaseModel
from typing import List, Literal, Union, Optional

class LLMGenerateStep(BaseModel):
    type: Literal['llm_generate']
    prompt: str
    # Optionally, a key to store this output in context (if provided by recipe author)
    output_key: Optional[str] = None

class FileWriteStep(BaseModel):
    type: Literal['file_write']
    path: str
    content: str

class RunCommandStep(BaseModel):
    type: Literal['run_command']
    command: str

class RunRecipeStep(BaseModel):
    type: Literal['run_recipe']
    recipe: str

# A step can be any one of the above (for type hinting)
Step = Union[LLMGenerateStep, FileWriteStep, RunCommandStep, RunRecipeStep]

class Recipe(BaseModel):
    name: str
    steps: List[Step]
