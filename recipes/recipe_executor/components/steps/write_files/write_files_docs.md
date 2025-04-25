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
        files_key: Optional name of the context key holding a List[FileSpec].
        files: Optional list of dictionaries with 'path' and 'content' keys.
        root: Optional base path to prepend to all output file paths.
    """
    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
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

Either `files_key` or `files` is required in the configuration. If both are provided, `files` takes precedence.

The `files_key` is the context key where the generated files are stored. The `files` parameter can be used to directly provide a list of dictionaries with `path` and `content` keys. Alternatively, the path and content can be specfied using `path_key` and `content_key` respectively to reference values in the context.

The WriteFilesStep can be used in recipes like this:

Files Key Example:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate a Python script that prints 'Hello, world!'",
        "model": "openai/o3-mini",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        # Preferred way to receive "files" from other steps that create FileSpec objects
        "files_key": "generated_files",
        "root": "output/src"
      }
    }
  ]
}
```

Files Example:

```json
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files": [
          { "path": "src/main.py", "content": "print('Hello, world!')" },
          {
            "path": "src/{{component_name}}_utils.py",
            "content_key": "generated_code"
          },
          {
            "path_key": "generated_config_path",
            "content_key": "generated_config_data"
          }
        ],
        "root": "output/src"
      }
    }
  ]
}
```

## Supported Context Values

The WriteFilesStep can work with two types of artifacts in the context:

### Single FileSpec object

```python
from recipe_executor.models import FileSpec
# Example of generating a FileSpec object
file = FileSpec(path="src/main.py", content="print('Hello, world!')")
# Store in context
context["generated_file"] = file
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

## Automatic JSON Serialization

When the content to be written is a Python dictionary or list, WriteFilesStep automatically serializes it to properly formatted JSON:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate configuration data for a project.",
        "model": "openai/o3-mini",
        "output_format": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "version": { "type": "string" },
            "dependencies": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "output_key": "project_config"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "config.json",
            "content_key": "project_config"
          }
        ],
        "root": "output"
      }
    }
  ]
}
```

In this example, `project_config` is a Python dictionary, but when written to `config.json`, it will be automatically serialized as proper JSON with double quotes and indentation.

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files",
        "root": "output/{{project_name}}"
      }
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
  "config": {
    "root": "output/src",
    "files_key": "generated_files"
  }
}
```

**Writing Structured Data as JSON**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/data",
    "files": [
      {
        "path": "config.json",
        "content_key": "config_data"
      }
    ]
  }
}
```

When `config_data` is a Python dictionary or list, it will be automatically serialized as formatted JSON.

**Project-Specific Output**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/{{project_name}}",
    "files_key": "project_files"
  }
}
```

**Component Generation**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/components",
    "files_key": "component_result"
  }
}
```

## Important Notes

- Directories are created automatically if they don't exist
- Files are overwritten without confirmation if they already exist
- All paths are rendered using template variables from the context (ContextProtocol)
- File content is written using UTF-8 encoding
- Both FileSpec and List[FileSpec] input formats are supported
- Python dictionaries and lists are automatically serialized to properly formatted JSON with indentation
- JSON serialization uses `json.dumps(content, ensure_ascii=False, indent=2)` for consistent formatting
