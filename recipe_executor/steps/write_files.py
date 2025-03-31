import logging
import os
from typing import List, Optional

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFileStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to '.'
    """

    artifact: str
    root: str = "."


class WriteFileStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes files to disk based on the provided artifact in the context.
    The artifact can be either a FileGenerationResult or a list of FileSpec objects.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize configuration using WriteFilesConfig
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the step: write files to disk by resolving paths using template rendering and
        creating directories as needed.

        Args:
            context (Context): Execution context containing artifacts and configuration.

        Raises:
            ValueError: If no artifact is found in the context.
            TypeError: If the artifact is not of an expected type.
            IOError: If file writing fails.
        """
        # Retrieve artifact from context
        data = context.get(self.config.artifact)

        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine file list based on artifact type
        if isinstance(data, FileGenerationResult):
            files: List[FileSpec] = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        # Render output root using the context to resolve any template variables
        output_root = render_template(self.config.root, context)

        # Process each file in the file list
        for file in files:
            # Render the relative file path from template variables
            rel_path = render_template(file.path, context)
            full_path = os.path.join(output_root, rel_path)

            # Create parent directories if they do not exist
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                except Exception as e:
                    self.logger.error(f"Failed to create directory {parent_dir}: {e}")
                    raise IOError(f"Error creating directory {parent_dir}: {e}")

            # Write file content to disk
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)
                self.logger.info(f"Wrote file: {full_path}")
            except Exception as e:
                self.logger.error(f"Failed to write file {full_path}: {e}")
                raise IOError(f"Error writing file {full_path}: {e}")
