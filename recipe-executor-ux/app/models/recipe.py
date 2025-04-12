import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Step(BaseModel):
    """A single step in a recipe"""

    type: str
    path: Optional[str] = None
    artifact: Optional[str] = None
    prompt: Optional[str] = None
    model: Optional[str] = None
    root: Optional[str] = None
    recipe_path: Optional[str] = None
    context_overrides: Optional[Dict[str, str]] = None
    substeps: Optional[List["Step"]] = None
    optional: Optional[bool] = None
    merge_mode: Optional[str] = None

    # Allow arbitrary additional properties for different step types
    class Config:
        extra = "allow"


class RecipeCreate(BaseModel):
    """Model for creating a new recipe"""

    name: str = Field(..., description="Recipe name")
    description: Optional[str] = Field(None, description="Recipe description")
    steps: List[Step] = Field([], description="Recipe steps")
    tags: List[str] = Field([], description="Recipe tags for organization")


class Recipe(RecipeCreate):
    """Full recipe model with ID and metadata"""

    id: str = Field(..., description="Recipe unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    @classmethod
    def create_new(cls, recipe_create: RecipeCreate) -> "Recipe":
        """Create a new recipe with generated ID and timestamps"""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            name=recipe_create.name,
            description=recipe_create.description,
            steps=recipe_create.steps,
            tags=recipe_create.tags,
            created_at=now,
            updated_at=now,
        )


class RecipeList(BaseModel):
    """Model for a list of recipes"""

    recipes: List[Recipe] = Field([], description="List of recipes")


class ExecutionStatus(BaseModel):
    """Model for recipe execution status"""

    execution_id: str = Field(..., description="Execution unique identifier")
    recipe_id: str = Field(..., description="Recipe ID being executed")
    status: str = Field(..., description="Current status (pending, running, completed, failed)")
    start_time: datetime = Field(..., description="Execution start time")
    end_time: Optional[datetime] = Field(None, description="Execution end time (if completed)")
    current_step: Optional[int] = Field(None, description="Current step index being executed")
    total_steps: int = Field(..., description="Total number of steps")
    logs: List[str] = Field([], description="Execution logs")
    context: Optional[Dict[str, Any]] = Field(None, description="Execution context")
    error: Optional[str] = Field(None, description="Error message (if failed)")
