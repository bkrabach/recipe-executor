"""
Utils component for template rendering in recipes.

Provides a stateless function to render Liquid templates against ContextProtocol instances.
"""

from typing import Any

import liquid

from recipe_executor.protocols import ContextProtocol


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
    # Ensure context provides dict of values for template (keys as strings; values coerced to str)
    context_dict: dict[str, Any] = context.dict()
    str_context: dict[str, Any] = {k: _stringify_value(v) for k, v in context_dict.items()}
    try:
        template = liquid.Template(text)
        rendered = template.render(**str_context)
        return rendered
    except Exception as exc:
        raise ValueError(f"Template rendering failed: {exc}\nTemplate: {text}") from exc


def _stringify_value(value: Any) -> Any:
    """
    Recursively convert basic types and containers to strings, leaves mapping/list structure for Liquid.
    """
    if isinstance(value, dict):
        return {k: _stringify_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_stringify_value(v) for v in value]
    elif isinstance(value, tuple):
        return tuple(_stringify_value(v) for v in value)
    elif value is None:
        return ""
    return str(value)
