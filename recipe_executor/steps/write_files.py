import logging
import os
from typing import Any, Dict, List

from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


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
    def __init__(
        self,
        logger: logging.Logger,
        config: Dict[str, Any],
    ) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        files_key: str = self.config.files_key
        root_template: str = self.config.root

        if files_key not in context:
            message = f"WriteFilesStep: Artifact '{files_key}' not found in context."
            self.logger.error(message)
            raise KeyError(message)

        artifact: Any = context[files_key]
        # Accept FileSpec or List[FileSpec]
        file_specs: List[FileSpec] = []
        if isinstance(artifact, FileSpec):
            file_specs = [artifact]
        elif isinstance(artifact, list):
            # Validate that each entry is a FileSpec
            try:
                file_specs = [fs if isinstance(fs, FileSpec) else FileSpec.model_validate(fs) for fs in artifact]
            except Exception as error:
                message = (
                    f"WriteFilesStep: The artifact '{files_key}' contains an invalid list of FileSpec objects: {error}"
                )
                self.logger.error(message)
                raise ValueError(message) from error
        else:
            message = (
                f"WriteFilesStep: The artifact '{files_key}' must be a FileSpec or List[FileSpec], got {type(artifact)}"
            )
            self.logger.error(message)
            raise TypeError(message)

        # Render root path (may be template)
        try:
            root_path: str = render_template(root_template, context).strip()
            if not root_path:
                root_path = "."
        except Exception as error:
            message = f"WriteFilesStep: Failed to render root template '{root_template}': {error}"
            self.logger.error(message)
            raise

        for file_spec in file_specs:
            # Render the file path (may be template)
            try:
                rendered_path = render_template(file_spec.path, context).strip()
            except Exception as error:
                message = f"WriteFilesStep: Failed to render template for file path '{file_spec.path}': {error}"
                self.logger.error(message)
                raise

            # Combine root_path and rendered_path
            full_path = os.path.normpath(os.path.join(root_path, rendered_path))
            file_content = file_spec.content

            self.logger.debug(
                f"WriteFilesStep: Preparing to write file at '{full_path}'. Content preview:\n{file_content[:2048]}"
            )

            # Ensure parent directories exist
            parent_dir = os.path.dirname(full_path)
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except Exception as error:
                message = f"WriteFilesStep: Failed to create directories for '{parent_dir}': {error}"
                self.logger.error(message)
                raise

            # Write the file
            try:
                with open(full_path, "w", encoding="utf-8") as file_handle:
                    file_handle.write(file_content)
            except Exception as error:
                message = f"WriteFilesStep: Failed to write file '{full_path}': {error}"
                self.logger.error(message)
                raise

            self.logger.info(f"WriteFilesStep: Wrote file '{full_path}' ({len(file_content)} bytes)")
