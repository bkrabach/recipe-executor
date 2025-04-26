# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both single FileSpec and list of FileSpec formats as input
- Optional use of `files_key` to specify the context key for file content or `files` for direct input
- While `FileSpec` is preferred, the component should also support a list of dictionaries with `path` and `content` keys and then write the files to disk, preserving the original structure of `content`
- Create directories as needed for file paths
- Apply template rendering to all file paths, content, and keys
- Automatically serialize Python dictionaries or lists to proper JSON format when writing to files
- Provide appropriate logging for file operations
- Follow a minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (single FileSpec or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically if they do not exist
- Apply template rendering to content prior to detecting its type, in case the content is a string that needs to be serialized
- Automatically detect when content is a Python dictionary or list and serialize it to proper JSON with indentation
- When serializing to JSON, use `json.dumps(content, ensure_ascii=False, indent=2)` for consistent, readable formatting
- Handle serialization errors with clear messages
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Logging

- Debug: Log each file's path and content before writing (to help debug failures)
- Info: Log the successful writing of each file (including its path) and the size of its content

## Component Dependencies

### Internal Components

- **Step Interface** – (Required) Follows the step interface via StepProtocol
- **Models** – (Required) Uses FileSpec models for content structure
- **Context** – (Required) Reads file content from a context that implements ContextProtocol (artifacts stored under a specified key)
- **Utils/Templates** – (Required) Uses render_template for dynamic path resolution

### External Libraries

- **json** - (Required) For serializing Python dictionaries and lists to JSON

### Configuration Dependencies

None

## Error Handling

- Validate that the specified artifact exists in context
- Ensure the artifact contains a valid single FileSpec or list of FileSpec objects
- Handle serialization errors with clear error messages when content cannot be converted to JSON
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Output Files

- `recipe_executor/steps/write_files.py`
