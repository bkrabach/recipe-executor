"""
File Write Step implementation for the Recipe Executor CLI tool.

This step writes content to a file. It resolves the output path based on the
configured OUTPUT_ROOT, creates necessary directories, and writes the content
after performing template substitutions using the provided context.
"""

import logging
import os
from typing import Optional
from recipe_executor.models import Step
from recipe_executor.config import OUTPUT_ROOT

class FileWriteStep(Step):
    """
    Step that writes content to a file.

    Attributes:
        type: The step type identifier ("file_write").
        name: An optional name for the step.
        path: The relative path where the file should be written.
        content: The file content, which may include placeholders to be replaced.
    """
    type: str = "file_write"
    name: Optional[str] = None
    path: str
    content: str

    def execute(self, context: dict) -> None:
        """
        Execute the step by writing the processed content to a file.

        Args:
            context: A dictionary holding shared execution state. Placeholders
                     in the content are replaced using keys from this context.
        """

        logging.info("Executing FileWriteStep: writing file '%s'", self.path)

        try:
            resolved_path = os.path.join(OUTPUT_ROOT, self.path)
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)

            processed_content = self.content
            for key, value in context.items():
                processed_content = processed_content.replace(f"{{{{{key}}}}}", str(value))

            with open(resolved_path, "w") as f:
                f.write(processed_content)
            logging.debug("File '%s' written successfully", resolved_path)

            # Update context with the file path for later steps.
            context[self.name or f"file_write_{len(context)}"] = resolved_path

        except Exception as e:
            logging.error("Error writing file '%s': %s", self.path, e)
            raise

    model_config = {"extra": "forbid"}
