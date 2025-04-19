import os
import logging
from typing import Any, Dict, List, Optional, Union

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils import render_template
from recipe_executor.models import FileSpec

class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        files_key: Name of the context key holding a List[FileSpec] or FileSpec.
        root: Optional base path to prepend to all output file paths.
    """
    files_key: str
    root: str = "."

class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        files_key: str = self.config.files_key
        root_template: str = self.config.root
        
        # Ensure the artifact exists in context
        if files_key not in context:
            error_message = f"WriteFilesStep: Context missing required artifact '{files_key}'"
            self.logger.error(error_message)
            raise KeyError(error_message)

        artifact: Any = context[files_key]

        # Handle FileSpec or List[FileSpec]
        file_specs: List[FileSpec] = []
        if isinstance(artifact, FileSpec):
            file_specs = [artifact]
        elif isinstance(artifact, list):
            for item in artifact:
                if not isinstance(item, FileSpec):
                    error_message = (
                        f"WriteFilesStep: Expected FileSpec or list of FileSpec for '{files_key}', "
                        f"but found list item of type {type(item)}"
                    )
                    self.logger.error(error_message)
                    raise TypeError(error_message)
            file_specs = artifact
        else:
            error_message = (
                f"WriteFilesStep: Context value for '{files_key}' must be FileSpec or list of FileSpec, "
                f"not {type(artifact)}"
            )
            self.logger.error(error_message)
            raise TypeError(error_message)

        rendered_root: str = render_template(root_template, context)
        
        for file_spec in file_specs:
            # Template render the file path (may use template variables)
            rendered_path: str = render_template(file_spec.path, context)
            full_path: str = os.path.normpath(os.path.join(rendered_root, rendered_path))

            # Prepare directory
            parent_dir: str = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    self.logger.debug(f"Created directories for '{parent_dir}'")
                except Exception as exc:
                    error_message = f"WriteFilesStep: Failed to create directories for '{parent_dir}': {exc}"
                    self.logger.error(error_message)
                    raise

            # Debug log path and content
            self.logger.debug(
                f"WriteFilesStep: Preparing to write file: {full_path}\nContent (first 500 chars):\n{file_spec.content[:500]}"
            )

            # Write file
            try:
                with open(full_path, "w", encoding="utf-8") as file_obj:
                    file_obj.write(file_spec.content)
                file_size: int = len(file_spec.content.encode("utf-8"))
                self.logger.info(
                    f"WriteFilesStep: Wrote '{full_path}' [{file_size} bytes]"
                )
            except Exception as exc:
                error_message = f"WriteFilesStep: Failed to write file '{full_path}': {exc}"
                self.logger.error(error_message)
                raise
