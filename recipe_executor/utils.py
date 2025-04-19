from typing import Any

from liquid import Template
from liquid.exceptions import LiquidError

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
    data: dict[str, Any] = context.dict()
    string_context: dict[str, str] = {k: str(v) if v is not None else "" for k, v in data.items()}
    try:
        template = Template(text)
        return template.render(**string_context)
    except LiquidError as exc:
        raise ValueError(
            f"Liquid template rendering error: {exc}\nTemplate: {text}\nContext: {string_context}"
        ) from exc
    except Exception as exc:
        raise ValueError(f"Template rendering error: {exc}\nTemplate: {text}\nContext: {string_context}") from exc
