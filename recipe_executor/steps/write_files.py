import logging
import os
from typing import List

from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        artifact: Name of the context key holding a FileGenerationResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """

    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, logger: logging.Logger, config: dict) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Retrieve the artifact from the context
        artifact_key = self.config.artifact
        artifact_value = context.get(artifact_key)
        if artifact_value is None:
            self.logger.error(f"Artifact '{artifact_key}' not found in context")
            raise KeyError(f"Artifact '{artifact_key}' not found in context")

        files_list: List[FileSpec] = []

        # Determine if artifact_value is FileGenerationResult or a list of FileSpec
        if hasattr(artifact_value, "files"):
            # Assume artifact_value is FileGenerationResult
            files_list = artifact_value.files
        elif isinstance(artifact_value, list):
            # Validate each element in the list is a FileSpec
            files_list = artifact_value
        else:
            message = "Artifact does not hold a valid FileGenerationResult or list of FileSpec objects."
            self.logger.error(message)
            raise ValueError(message)

        # Render the root path using the context, supports template variables
        rendered_root = render_template(self.config.root, context)

        # Write each file
        for file_spec in files_list:
            # Render the dynamic file path
            rendered_file_path = render_template(file_spec.path, context)
            # Combine the rendered root and file path
            full_path = os.path.join(rendered_root, rendered_file_path)

            # Ensure the parent directories exist
            directory = os.path.dirname(full_path)
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                self.logger.error(f"Failed to create directories for path {directory}: {str(e)}")
                raise

            # Log debug information with file path and content length
            self.logger.debug(f"Preparing to write file: {full_path}\nContent:\n{file_spec.content}")

            try:
                with open(full_path, "w", encoding="utf-8") as file_handle:
                    file_handle.write(file_spec.content)
                self.logger.info(f"Successfully wrote file: {full_path} (size: {len(file_spec.content)} bytes)")
            except Exception as e:
                self.logger.error(f"Failed writing file {full_path}: {str(e)}")
                raise
