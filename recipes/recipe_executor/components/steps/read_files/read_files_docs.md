# ReadFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.read_files import ReadFilesStep, ReadFilesConfig
```

## Configuration

The ReadFilesStep is configured with a ReadFilesConfig:

```python
class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path or list of paths to the file(s) to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + contents
            - "dict": Store a dictionary with filenames as keys and contents as values
    """

    path: Union[str, List[str]]
    artifact: str
    optional: bool = False
    merge_mode: str = "concat"
```

## Step Registration

The ReadFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_files import ReadFilesStep

STEP_REGISTRY["read_files"] = ReadFilesStep
```

## Basic Usage in Recipes

### Reading a Single File

The ReadFilesStep can be used to read a single file just like the original read_file step:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

### Reading Multiple Files

You can read multiple files by providing a list of paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/component_spec.md", "specs/component_docs.md"],
      "artifact": "component_specs",
      "merge_mode": "concat"
    }
  ]
}
```

### Reading Multiple Files as a Dictionary

You can also store multiple files as a dictionary with filenames as keys:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/component_spec.md", "specs/component_docs.md"],
      "artifact": "component_specs",
      "merge_mode": "dict"
    }
  ]
}
```

## Template-Based Paths

The path can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

Template variables can also be used in list paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": [
        "specs/{{component_id}}_spec.md",
        "specs/{{component_id}}_docs.md"
      ],
      "artifact": "component_files"
    }
  ]
}
```

## Optional Files

You can specify that files are optional, and execution will continue even if files don't exist:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": ["specs/required_file.md", "specs/optional_file.md"],
      "artifact": "component_files",
      "optional": true
    }
  ]
}
```

If an optional file is not found:

- For a single file: an empty string is stored in the context
- For multiple files with `merge_mode: "concat"`: the file is skipped in the concatenation
- For multiple files with `merge_mode: "dict"`: an empty string is stored for that file key

## Common Use Cases

**Loading Multiple Related Specifications**:

```json
{
  "type": "read_files",
  "path": ["specs/{{component_id}}_spec.md", "specs/{{component_id}}_docs.md"],
  "artifact": "component_files",
  "merge_mode": "concat"
}
```

**Loading Templates with Optional Components**:

```json
{
  "type": "read_files",
  "path": [
    "templates/email_base.txt",
    "templates/email_header.txt",
    "templates/email_footer.txt"
  ],
  "artifact": "email_templates",
  "optional": true,
  "merge_mode": "dict"
}
```

**Dynamic Path Resolution with Multiple Files**:

```json
{
  "type": "read_files",
  "path": [
    "docs/{{project}}/{{component}}/README.md",
    "docs/{{project}}/{{component}}/USAGE.md"
  ],
  "artifact": "documentation",
  "optional": true
}
```

**Command Line Integration**:

```bash
python -m recipe_executor.main recipes/generate.json --context files_to_read="specs/component_a.md,specs/component_b.md"
```

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{files_to_read.split(',')|default:'specs/default.md'}}",
      "artifact": "input_files"
    }
  ]
}
```

## Important Notes

- The step uses UTF-8 encoding by default for all files
- When a file is optional and missing, it's handled differently based on merge_mode
- Template variables in all paths are resolved before reading the files
- For backwards compatibility, single file behavior matches the original read_file step
- When using merge_mode "dict", the keys are the basenames of the files (not full paths)
- All paths support template rendering, including paths in a list
