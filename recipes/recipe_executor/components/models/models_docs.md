# Models Component Usage

## Importing

```python
from recipe_executor.models import (
    FileSpec,
    RecipeStep,
    Recipe
)
```

## File Models

### FileSpec

Represents a single file:

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file.
    """

    path: str
    content: str
```

Usage example:

```python
file = FileSpec(
    path="src/utils.py",
    content="def hello_world():\n    print('Hello, world!')"
)

# Access properties
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
```

## Recipe Models

### RecipeStep

Represents a single step in a recipe:

```python
class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """

    type: str
    config: Dict
```

### Recipe

Represents a complete recipe with multiple steps:

```python
class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]
```

Usage example:

```python
from recipe_executor.models import Recipe, RecipeStep

# Create a recipe with steps
recipe = Recipe(
    steps=[
        RecipeStep(
            type="read_files",
            config={"path": "specs/component_spec.md", "content_key": "spec"}
        ),
        RecipeStep(
            type="generate_with_llm",
            config={
                "prompt": "Generate code for: {{spec}}",
                "model": "{{model|default:'openai/o3-mini'}}",
                "response_format": "files",
                "response_key": "code_result"
            }
        ),
        RecipeStep(
            type="write_files",
            config={"files_key": "code_result", "root": "./output"}
        )
    ]
)
```

## Model Validation

All models inherit from Pydantic's BaseModel, providing automatic validation:

```python
# This will raise a validation error because path is required
try:
    FileSpec(content="File content")
except Exception as e:
    print(f"Validation error: {e}")

# This works correctly
valid_file = FileSpec(path="file.txt", content="File content")
```

## Important Notes

- Models can be converted to dictionaries with `.model_dump()` method
- Models can be created from dictionaries with `Model.model_validate(dict_data)`
- Models can be converted to JSON with `.model_dump_json()` method
- Models can be created from JSON with `Model.model_validate_json(json_data)`
