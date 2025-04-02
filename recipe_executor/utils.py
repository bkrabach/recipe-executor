import logging
from typing import Any, Dict

from liquid import Template

from recipe_executor.context import Context

# Configure module-level logger
logger = logging.getLogger(__name__)


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
    logger.debug(f"Rendering template: {text}")
    
    try:
        # Retrieve context artifacts and log the keys for debugging
        context_dict: Dict[str, Any] = context.as_dict()
        debug_context_keys = list(context_dict.keys())
        logger.debug(f"Context keys: {debug_context_keys}")

        # Convert all context values to strings to avoid type errors
        safe_context = {key: str(value) for key, value in context_dict.items()}

        # Create the Liquid template and render it using the safe context
        template_obj = Template(text)
        result = template_obj.render(safe_context)

        return result
    except Exception as e:
        error_message = f"Error rendering template: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e
