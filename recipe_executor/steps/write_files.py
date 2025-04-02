import os
import logging
from typing import List, Union, Any

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.models import FileSpec, FileGenerationResult
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
    """
    WriteFilesStep component responsible for writing generated files to disk.

    It supports both FileGenerationResult and List[FileSpec] formats, creates directories 
    as needed, applies template rendering to the file paths, and logs file operation details.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Retrieve the files artifact from the context using the configured artifact key
        artifact_key = self.config.artifact
        if artifact_key not in context:
            error_msg = f"Artifact '{artifact_key}' not found in the context."
            self.logger.error(error_msg)
            raise KeyError(error_msg)

        raw_files = context[artifact_key]

        # Determine if raw_files is a FileGenerationResult or list of FileSpec
        files_to_write: List[FileSpec] = []
        if isinstance(raw_files, FileGenerationResult):
            files_to_write = raw_files.files
        elif isinstance(raw_files, list):
            # Validate that every element in the list is a FileSpec
            if all(isinstance(f, FileSpec) for f in raw_files):
                files_to_write = raw_files
            else:
                error_msg = f"Artifact '{artifact_key}' does not contain valid FileSpec objects."
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            error_msg = f"Artifact '{artifact_key}' must be a FileGenerationResult or a list of FileSpec, got {type(raw_files)}."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Render the root template and ensure it's a proper directory path
        rendered_root = render_template(self.config.root, context)
        if not os.path.isdir(rendered_root):
            try:
                os.makedirs(rendered_root, exist_ok=True)
                self.logger.debug(f"Created directory: {rendered_root}")
            except Exception as e:
                error_msg = f"Failed to create root directory '{rendered_root}': {str(e)}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

        # Write each file
        for file_spec in files_to_write:
            # Render file path using the current context
            rendered_file_path = render_template(file_spec.path, context)
            # Combine with rendered root
            full_path = os.path.join(rendered_root, rendered_file_path)
            parent_dir = os.path.dirname(full_path)
            if not os.path.isdir(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    self.logger.debug(f"Created directory: {parent_dir}")
                except Exception as e:
                    error_msg = f"Failed to create directory '{parent_dir}': {str(e)}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
            
            # Log debug information before writing
            self.logger.debug(f"Writing file '{full_path}' with content length {len(file_spec.content)}")
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(file_spec.content)
                self.logger.info(f"Successfully wrote file '{full_path}' (size: {len(file_spec.content)} bytes)")
            except Exception as e:
                error_msg = f"Error writing file '{full_path}': {str(e)}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
