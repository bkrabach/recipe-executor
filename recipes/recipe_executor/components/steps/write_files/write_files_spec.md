# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both FileGenerationResult and list of FileSpec formats as input
- Create directories as needed for file paths
- Apply template rendering to file paths
- Provide appropriate logging for file operations
- Follow a minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (FileGenerationResult or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically if they do not exist
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Logging

- Debug: Log each file’s path and content before writing (to help debug failures)
- Info: Log the successful writing of each file (including its path) and the size of its content

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for reading artifact data and StepProtocol for step interface compliance
- **Step Interface** – (Required) Follows the step interface via StepProtocol
- **Context** – (Required) Retrieves file content from a context implementing ContextProtocol
- **Models** – (Required) Uses FileGenerationResult and FileSpec models for content structure
- **Utils** – (Required) Uses render_template for dynamic path resolution

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the specified artifact exists in context
- Ensure the artifact contains a valid FileGenerationResult or list of FileSpec objects
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Output Files

- `steps/write_files.py`

## Future Considerations

- “Dry-run” mode that logs intended writes without performing them
