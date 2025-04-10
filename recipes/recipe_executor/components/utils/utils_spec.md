# Utils Component Specification

## Purpose

The Utils component provides general utility functions for recipes, primarily focused on template rendering. It offers a way to render strings with template variables against the execution context, enabling dynamic content generation in recipes.

## Core Requirements

- Render strings as templates using context data
- Utilize a standard templating engine (Liquid) for consistency
- Ensure that all context values are accessible to the templates
- Handle errors in template rendering gracefully
- Keep the utility functions stateless and reusable

## Implementation Considerations

- Use the Liquid templating library directly without unnecessary abstraction
- Convert context values to strings before rendering to prevent type errors
- Handle rendering errors gracefully with clear error messages
- Keep the implementation stateless and focused on its single responsibility

## Logging

- Debug: Log the template text being rendered and the context keys used
- Info: None

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol definition for context data access
- **Context** – (Required) Uses a context implementing ContextProtocol for accessing artifacts during template rendering

### External Libraries

- **Liquid** – (Required) Uses the Liquid templating engine for rendering (`python-liquid`)
- **json** – (Required) Uses the built-in json module for handling dictionary-to-string conversions (when needed)

### Configuration Dependencies

None

## Error Handling

- Wrap template rendering in try/except blocks
- Provide specific error messages indicating the source of template failures
- Propagate rendering errors with useful context information

## Output Files

- `utils.py`

## Future Considerations

- Support custom template filters or tags
- Support template partials or includes
- Template validation or linting before rendering
