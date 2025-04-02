# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both FileGenerationResult and list of FileSpec formats
- Create directories as needed for file paths
- Apply template rendering to file paths
- Provide appropriate logging for file operations
- Follow minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (FileGenerationResult or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Logging

- Debug: Log the file path and content being written before writing (in case of failure)
- Info: Log the successful writing of the file (including path) and its content size

## Component Dependencies

### Internal Components

- **Steps Base** - (Required) Extends BaseStep to implement the step interface
- **Context** - (Required) Retrieves file content from the context
- **Models** - (Required) Uses FileGenerationResult and FileSpec models for content structure
- **Utils** - (Required) Uses render_template for dynamic path resolution

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the artifact exists in context
- Ensure artifact contains a valid FileGenerationResult or list of FileSpec objects
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Output Files

- `steps/write_files.py`

## Future Considerations

- Dry-run mode that logs without writing
