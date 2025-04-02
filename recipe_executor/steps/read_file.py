import os
import logging
from typing import Any, Dict, Optional

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFileConfig(StepConfig):
    """
    Configuration for ReadFileStep.

    Fields:
        path (str): Path to the file to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if the file is not found.
    """
    path: str
    artifact: str
    optional: bool = False


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    ReadFileStep reads a file from the filesystem using a dynamic path resolved via templating.
    It stores the file content in the provided context under the specified artifact key.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to ReadFileConfig using pydantic or similar underlying mechanism
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Render the file path using context and provided template
        rendered_path = render_template(self.config.path, context)
        self.logger.debug(f"Attempting to read file from path: {rendered_path}")

        # Check if file exists
        if not os.path.exists(rendered_path):
            if self.config.optional:
                self.logger.warning(f"Optional file not found at path: {rendered_path}. Continuing with empty content.")
                context[self.config.artifact] = ""
                return
            else:
                error_message = f"ReadFileStep: file not found at path: {rendered_path}"
                self.logger.error(error_message)
                raise FileNotFoundError(error_message)

        # Read the file using UTF-8 encoding
        self.logger.info(f"Reading file from: {rendered_path}")
        try:
            with open(rendered_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading file at {rendered_path}: {e}")
            raise

        # Store the file content in context under the specified artifact key
        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")
