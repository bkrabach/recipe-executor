import logging
from typing import Dict

import liquid

from recipe_executor.protocols import ContextProtocol

# Set up module-level logger
logger = logging.getLogger(__name__)


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All context values are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    # Extract all artifacts from context using as_dict() for safety
    try:
        context_dict = context.as_dict()
    except Exception as e:
        raise ValueError(f"Failed to retrieve context data: {e}")

    # Convert all context values to strings
    safe_context: Dict[str, str] = {}
    for key, value in context_dict.items():
        try:
            safe_context[key] = str(value)
        except Exception as e:
            logger.debug(f"Error converting context value for key '{key}' to string: {e}")
            safe_context[key] = ""

    # Log debug information: template text and context keys
    logger.debug(f"Rendering template: {text}")
    logger.debug(f"Using context keys: {list(safe_context.keys())}")

    try:
        # Create a Liquid template instance
        template = liquid.Template(text)
        # Render the template with the safe context
        rendered_text = template.render(**safe_context)
        return rendered_text
    except Exception as e:
        error_message = (
            f"Error rendering template. Template: '{text}'. Context keys: {list(safe_context.keys())}. Error: {e}"
        )
        logger.debug(error_message)
        raise ValueError(error_message) from e
