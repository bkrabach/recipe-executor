# recipe_executor/executor.py

import logging
import os
from datetime import datetime
from recipe_executor import config, models
from recipe_executor.steps import llm_generate, file_write, run_command, run_recipe

def setup_logging():
    """Configure logging to separate info, error, and debug logs in the logs directory."""
    logs_dir = config.Config.LOGS_DIR
    os.makedirs(logs_dir, exist_ok=True)
    # Define log file paths
    info_path = os.path.join(logs_dir, "info.log")
    error_path = os.path.join(logs_dir, "error.log")
    debug_path = os.path.join(logs_dir, "debug.log")
    # Set up the root logger with handlers for each log level
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    # Debug log handler (captures all levels)
    debug_handler = logging.FileHandler(debug_path, mode='w')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    # Info log handler (captures info and above)
    info_handler = logging.FileHandler(info_path, mode='w')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    # Error log handler (captures only errors)
    error_handler = logging.FileHandler(error_path, mode='w')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    # Add handlers to the root logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    # Also log INFO level to console for user feedback (optional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S'))
    logger.addHandler(console_handler)
    logging.debug("Logging initialized. Logs directory: %s", logs_dir)

def execute_recipe(recipe: models.Recipe, context=None):
    """
    Execute the given Recipe (sequence of steps) in order.
    An optional context dict can be provided; otherwise a new one is created.
    Returns the context with all outputs after executing the recipe.
    """
    if context is None:
        context = {}
    logging.info(f"Starting recipe: {recipe.name}")
    # Iterate over each step in the recipe
    for idx, step in enumerate(recipe.steps, start=1):
        try:
            logging.info(f"Step {idx}: {describe_step(step)}")
            logging.debug(f"Context before step {idx}: {context}")
            result = None
            # Dispatch to the appropriate step handler based on step.type
            if step.type == 'llm_generate':
                result = llm_generate.execute(step, context)
                logging.info(f"LLM output: {truncate_str(result)}")
            elif step.type == 'file_write':
                result = file_write.execute(step, context)
                logging.info(f"Wrote to file: {result}")
            elif step.type == 'run_command':
                result = run_command.execute(step, context)
                if isinstance(result, dict):
                    logging.info(f"Command output: {truncate_str(result.get('output', ''))}")
                    if result.get("returncode", 0) != 0:
                        logging.error(f"Command exited with code {result['returncode']}: {result.get('error')}")
                else:
                    logging.info(f"Command executed with result: {result}")
            elif step.type == 'run_recipe':
                result = run_recipe.execute(step, context)
                logging.info(f"Executed sub-recipe: {step.recipe}")
            logging.debug(f"Step {idx} result: {result}")
        except Exception as e:
            # Log the error and abort execution
            logging.error(f"Error in step {idx}: {e}")
            logging.debug("Aborting execution due to error.")
            raise  # Propagate the exception after logging
    logging.info(f"Recipe '{recipe.name}' completed.")
    return context

def describe_step(step):
    """Produce a concise description of a step for logging purposes."""
    if step.type == 'llm_generate':
        return f"LLM generate (prompt: {truncate_str(step.prompt)})"
    if step.type == 'file_write':
        return f"File write (path: {step.path})"
    if step.type == 'run_command':
        return f"Run command (`{step.command}`)"
    if step.type == 'run_recipe':
        return f"Run recipe ({step.recipe})"
    return str(step)

def truncate_str(s, length=60):
    """Helper to truncate long strings for cleaner log output."""
    s = str(s)
    return s if len(s) <= length else s[:length] + "..."
