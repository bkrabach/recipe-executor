# Utils Component Usage

## Importing

```python
from recipe_executor.utils import render_template
```

## Template Rendering

The Utils component provides a `render_template` function that renders Liquid templates using values from the Context:

```python
def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

Basic usage example:

```python
from recipe_executor.context import Context
from recipe_executor.utils import render_template

# Create a context with values
context = Context(artifacts={"name": "World", "count": 42})

# Render a template
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Liquid syntax:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains dictionaries)
template = "Author: {{book.author}}"
```

### Conditionals

```python
template = "{% if user_count > 0 %}Users: {{user_count}}{% else %}No users{% endif %}"
```

### Loops

```python
template = "{% for item in items %}Item: {{item}}{% endfor %}"
```

## Type Handling

All values from the context are converted to strings before rendering:

```python
# Context with mixed types
context = Context(artifacts={
    "number": 42,
    "boolean": True,
    "list": [1, 2, 3],
    "dict": {"key": "value"}
})

# All values become strings in templates
template = "Number: {{number}}, Boolean: {{boolean}}, List: {{list}}, Dict: {{dict}}"
# Renders as: "Number: 42, Boolean: True, List: [1, 2, 3], Dict: {'key': 'value'}"
```

## Error Handling

Template rendering errors are wrapped in a ValueError:

```python
try:
    result = render_template("{% invalid syntax %}", context)
except ValueError as e:
    print(f"Template error: {e}")
    # Handle the error
```

## Common Usage Patterns

### In Step Classes

The primary use of template rendering is in step execution:

```python
# Example from ReadFilesStep.execute()
def execute(self, context: Context) -> None:
    # Render the path using the current context
    path = render_template(self.config.path, context)

    # Read the file at the rendered path
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Store in context (with rendered artifact key if needed)
    artifact_key = render_template(self.config.artifact, context)
    context[artifact_key] = content
```

### In Recipe Steps

Templates are typically used in recipe step configurations:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    },
    {
      "type": "generate",
      "prompt": "Generate code based on: {{component_spec}}",
      "model": "{{model_id|default:'openai:o3-mini'}}",
      "artifact": "generated_code"
    }
  ]
}
```

## Important Notes

1. All context values are converted to strings, which may affect formatting
2. Template rendering is synchronous and blocking
3. The Context's `as_dict()` method is used to access all artifacts
4. Empty or missing variables will be replaced with an empty string
