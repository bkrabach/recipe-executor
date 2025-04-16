# Utils Component Usage

## Importing

```python
from recipe_executor.utils import render_template
```

## Template Rendering

The Utils component provides a `render_template` function that renders Liquid templates using values from a context object implementing the ContextProtocol:

```python
def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

Basic usage example:

```python
from recipe_executor.utils import render_template

# Create a context with some values
context = Context(artifacts={"name": "World", "count": 42})

# Render a template string using the context
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Liquid syntax. Here are some common features:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains nested dictionaries)
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
