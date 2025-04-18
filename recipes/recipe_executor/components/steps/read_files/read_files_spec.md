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
