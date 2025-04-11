import logging

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
    logger = logging.getLogger(__name__)

    # Convert all context values to strings to prevent type errors
    try:
        context_dict = context.as_dict()
    except Exception as conv_error:
        error_message = f"Failed to extract context data: {conv_error}"
        logger.error(error_message)
        raise ValueError(error_message) from conv_error

    template_context = {key: str(value) for key, value in context_dict.items()}

    # Log the template text and the context keys being used
    logger.debug("Rendering template: %s", text)
    logger.debug("Context keys: %s", list(template_context.keys()))

    try:
        # Create a Liquid template, then render with the provided context
        tpl = liquid.Template(text)
        rendered_text = tpl.render(**template_context)
        return rendered_text
    except Exception as e:
        error_message = f"Error rendering template. Template: {text}. Error: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message) from e
