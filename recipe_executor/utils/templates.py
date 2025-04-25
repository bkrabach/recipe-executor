from typing import Any

import liquid
from liquid.exceptions import LiquidError

from recipe_executor.protocols import ContextProtocol


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are passed as-is to the template.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    context_dict: dict[str, Any] = context.dict()
    try:
        template = liquid.Template(text)
        return template.render(**context_dict)
    except LiquidError as exc:
        raise ValueError(f"Template rendering failed: {exc}\nTemplate: {text!r}\nContext: {context_dict!r}") from exc
    except Exception as exc:
        raise ValueError(
            f"Unknown error during template rendering: {exc}\nTemplate: {text!r}\nContext: {context_dict!r}"
        ) from exc
