# ReadFilesStep Component Specification

## Purpose

The ReadFilesStep component reads one or more files from the filesystem and stores their contents in the execution context. It serves as a foundational step for loading data into recipes (such as specifications, templates, and other input files) with support for both single-file and multi-file operations.

## Core Requirements

- Read a file or multiple files from specified path(s)
- Support input specified as a single path string, a comma-separated string of paths, or a list of path strings
- If a single string is provided, detect commas to determine if it represents multiple paths and split accordingly
- Support template-based path resolution for all paths
- Store all file contents in the context under a single specified key
- Provide flexible content merging options for multi-file reads
- Support optional file handling for cases when files might not exist
- Include appropriate logging and error messages
- Follow a minimal design with clear error handling

## Implementation Considerations

- Render template strings for the `path` parameter before evaluating the input type
- Use template rendering to support dynamic paths for single path, comma-separated paths in one string, and lists of paths
- Handle missing files explicitly with meaningful error messages
- Use consistent UTF-8 encoding for text files
- Implement an `optional` flag to continue execution if files are missing
- For multiple files, provide a way to merge contents (default: concatenate with newlines separating each file’s content)
- Provide a clear content structure when reading multiple files (e.g. a dictionary with filenames as keys)
- Keep the implementation simple and focused on a single responsibility
- For backwards compatibility, preserve the behavior of the original single-file read step

## Logging

- Debug: Log each file path before attempting to read (useful for diagnosing failures)
- Info: Log the successful reading of each file (including its path) and the final storage key used in the context

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for context interactions and StepProtocol for step interface implementation
- **Step Interface** – (Required) Implements the step interface via StepProtocol
- **Context** – (Required) Stores file contents using a context that implements ContextProtocol (artifacts stored under a specified key)
- **Utils** – (Required) Uses render_template for dynamic path resolution

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Raise a FileNotFoundError with a clear message when required files do not exist
- Support the `optional` flag to continue execution (with empty content) if files are missing
- Handle error cases differently for single-file versus multiple-file scenarios
- Log appropriate warnings and information during execution
- When reading multiple files and some are optional, continue processing those files that exist

## Output Files

- `steps/read_files.py`

## Future Considerations

- Directory reading and file glob patterns
- Advanced content merging options
- Additional metadata capture (e.g. file size, timestamps)
- Content transformation or pre-processing options

## Dependency Integration Considerations

None

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
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
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

The ReadFilesStep can be used to read a single file (just like the original `read_file` step):

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

You can read multiple files by providing a comma-separated string of paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md,specs/component_docs.md",
      "artifact": "component_specs"
    }
  ]
}
```

You can also read multiple files by providing a list of path strings:

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

You can store multiple files as a dictionary with filenames as keys:

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

The `path` parameter can include template variables from the context:

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

Template variables can also be used within list paths:

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

You can specify that files are optional. If an optional file doesn't exist, execution will continue:

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
- For multiple files with `merge_mode: "concat"`: the missing file is skipped in the concatenated result
- For multiple files with `merge_mode: "dict"`: an empty string is stored for that file’s key

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

You can also supply paths via command-line context values:

```bash
python -m recipe_executor.main recipes/generate.json --context files_to_read="specs/component_a.md,specs/component_b.md"
```

Then in the recipe you can use that context value:

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
- When a file is optional and missing, it is handled according to the specified `merge_mode`
- Template variables in all paths are resolved before reading the files
- For backwards compatibility, single-file behavior matches the original `read_file` step
- When using `merge_mode: "dict"`, the keys in the output are the base names of the files (not the full paths)
- All paths support template rendering (including each path in a list)
