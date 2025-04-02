import os
import logging
from typing import List, Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.models import FileSpec, FileGenerationResult
from recipe_executor.context import Context
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths.
    """
    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    WriteFilesStep writes generated files to disk based on the content in the context.
    It supports both FileGenerationResult and list of FileSpec formats.
    It renders file paths using templates, creates necessary directories, and writes the file content.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to WriteFilesConfig using StepConfig capabilities
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Retrieve the artifact from the context
        data = context.get(self.config.artifact)
        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine the list of files to write
        files: List[FileSpec] = []
        if isinstance(data, FileGenerationResult):
            files = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        try:
            # Render the output root path using template rendering
            output_root = render_template(self.config.root, context)
        except Exception as e:
            self.logger.error(f"Failed to render template for root path: {e}")
            raise ValueError(f"Failed to render template for root path: {e}")

        # Process each file in the list
        for file in files:
            try:
                # Render the file path using template rendering
                rel_path = render_template(file.path, context)
                full_path = os.path.join(output_root, rel_path)

                # Log debug information before writing
                self.logger.debug(f"Writing file at path: {full_path} with content size: {len(file.content)}")

                # Create parent directories if they don't exist
                parent_dir = os.path.dirname(full_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                # Write the file content using UTF-8 encoding
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)

                # Log success of file write operation
                self.logger.info(f"Wrote file: {full_path} (size: {len(file.content)} bytes)")
            except IOError as ioe:
                self.logger.error(f"I/O error writing file: {ioe}")
                raise
            except Exception as e:
                self.logger.error(f"Error processing file {file.path}: {e}")
                raise
