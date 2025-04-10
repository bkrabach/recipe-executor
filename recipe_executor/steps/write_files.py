import logging
import os
from typing import List, Optional

from recipe_executor.models import FileGenerationResult, FileSpec
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
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(WriteFilesConfig(**config), logger)
        if self.logger is None:
            self.logger = logging.getLogger(__name__)

    def execute(self, context: ContextProtocol) -> None:
        # Retrieve the artifact from context
        artifact_key = self.config.artifact
        artifact = context.get(artifact_key)
        if artifact is None:
            error_msg = f"Artifact '{artifact_key}' not found in context."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Determine type of artifact and extract list of FileSpec
        file_specs: List[FileSpec] = []
        if isinstance(artifact, FileGenerationResult):
            file_specs = artifact.files
        elif isinstance(artifact, list):
            # Validate that all elements are FileSpec instances
            if all(isinstance(item, FileSpec) for item in artifact):
                file_specs = artifact
            else:
                error_msg = f"Artifact '{artifact_key}' list does not contain valid FileSpec objects."
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            error_msg = f"Artifact '{artifact_key}' is neither a FileGenerationResult nor a list of FileSpec objects."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Render the root path using template variables from context
        rendered_root = render_template(self.config.root, context)

        for file_spec in file_specs:
            try:
                # Render the file path template
                rendered_file_path = render_template(file_spec.path, context)

                # Prepend the rendered root path
                final_path = os.path.join(rendered_root, rendered_file_path) if rendered_root else rendered_file_path

                # Ensure the directory exists
                parent_dir = os.path.dirname(final_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                    self.logger.debug(f"Created directory: {parent_dir}")

                # Debug log before writing file
                self.logger.debug(f"Writing file: {final_path}")
                self.logger.debug(f"File content (first 100 chars): {file_spec.content[:100]}...")

                # Write the file content to disk
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(file_spec.content)

                # Log successful write
                file_size = len(file_spec.content.encode("utf-8"))
                self.logger.info(f"Successfully wrote file: {final_path} ({file_size} bytes)")
            except Exception as e:
                self.logger.error(f"Error writing file '{file_spec.path}': {str(e)}")
                raise
