# WriteFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.write_files import WriteFilesStep, WriteFilesConfig
```

## Configuration

The WriteFilesStep is configured with a WriteFilesConfig:

```python
class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        artifact: Name of the context key holding a FileGenerationResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """

    artifact: str
    root: str = "."
```

## Step Registration

The WriteFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

STEP_REGISTRY["write_files"] = WriteFilesStep
```

## Basic Usage in Recipes

The WriteFilesStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "output/project"
    }
  ]
}
```

## Supported Context Values

The WriteFilesStep can work with two types of artifacts in the context:

### FileGenerationResult

```python
from recipe_executor.models import FileGenerationResult, FileSpec

# Example of generating a FileGenerationResult
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)

# Store in context
context["generated_code"] = result
```

### List of FileSpec objects

```python
from recipe_executor.models import FileSpec

# Example of generating a list of FileSpec objects
files = [
    FileSpec(path="src/main.py", content="print('Hello, world!')"),
    FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
]

# Store in context
context["generated_files"] = files
```

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "output/{{project_name}}"
    }
  ]
}
```

File paths within the FileSpec objects can also contain templates:

```python
FileSpec(
    path="{{component_name}}/{{filename}}.py",
    content="# Generated code for {{component_name}}"
)
```

## Common Use Cases

**Writing Generated Code**:

```json
{
  "type": "write_files",
  "artifact": "generated_code",
  "root": "output/src"
}
```

**Project-Specific Output**:

```json
{
  "type": "write_files",
  "artifact": "project_files",
  "root": "output/{{project_name}}"
}
```

**Component Generation**:

```json
{
  "type": "write_files",
  "artifact": "component_result",
  "root": "output/components"
}
```

## Important Notes

- Directories are created automatically if they don't exist
- Files are overwritten without confirmation if they already exist
- All paths are rendered using template variables from the context
- File content is written using UTF-8 encoding
- Both FileGenerationResult and List[FileSpec] formats are supported
