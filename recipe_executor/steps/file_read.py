"""
File Read Step implementation for the Recipe Executor CLI tool.

This step reads data from a file and returns its content.
"""

import logging

from typing import Optional
from recipe_executor.models import Step

class FileReadStep(Step):
    """
    Step that reads data from a file.

    Attributes:
        type: The step type identifier ("file_read").
        name: An optional name for the step.
        file_path: The path of the file to read.
    """
    type: str = "file_read"
    name: Optional[str] = None
    file_path: str

    def execute(self, context: dict) -> str:
        """
        Execute the step by reading and returning the file content.

        Args:
            context: A dictionary holding shared execution state.

        Returns:
            The content of the file as a string.
        """

        logging.info("Executing FileReadStep: reading file '%s'", self.file_path)

        try:
            with open(self.file_path, "r") as file:
                data = file.read()
            logging.debug("Successfully read %d bytes from '%s'", len(data), self.file_path)
            return data

        except Exception as e:
            logging.error("Error reading file '%s': %s", self.file_path, e)
            raise

    model_config = {"extra": "forbid"}
