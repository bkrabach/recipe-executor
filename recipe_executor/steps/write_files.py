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

    Attributes:
        files (str): Name of the context key holding a FileSpec or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to ".".
    """

    files_key: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        files_key: str = self.config.files_key
        root: str = self.config.root or "."

        if files_key not in context:
            self.logger.error(f"No artifact with key '{files_key}' found in context.")
            raise KeyError(f"Context missing artifact '{files_key}' for WriteFilesStep.")

        files_value = context[files_key]
        files_list: List[FileSpec] = []

        # Determine if input is FileSpec or list of FileSpec
        if isinstance(files_value, FileSpec):
            files_list = [files_value]
        elif isinstance(files_value, list):
            files_list = []
            for idx, item in enumerate(files_value):
                if isinstance(item, FileSpec):
                    files_list.append(item)
                elif isinstance(item, dict):
                    try:
                        files_list.append(FileSpec.model_validate(item))
                    except Exception as e:
                        self.logger.error(f"Invalid FileSpec in list at index {idx}: {e}")
                        raise ValueError(f"Invalid FileSpec in list at index {idx}: {e}")
                else:
                    self.logger.error(f"List item at index {idx} is not a FileSpec or dict: {item}")
                    raise TypeError(f"Artifact list contains invalid item at index {idx}.")
        elif isinstance(files_value, dict):
            # Possibly a FileSpec provided as dict
            try:
                files_list = [FileSpec.model_validate(files_value)]
            except Exception as e:
                self.logger.error(f"Invalid FileSpec dict for artifact '{files_key}': {e}")
                raise ValueError(f"Invalid FileSpec dict for artifact '{files_key}': {e}")
        else:
            self.logger.error(
                f"Artifact '{files_key}' must be a FileSpec or list of FileSpec objects. Got type: {type(files_value)}"
            )
            raise TypeError(f"Artifact '{files_key}' must be a FileSpec or list of FileSpec objects.")

        for file_spec in files_list:
            # Render file path template
            try:
                rendered_path = render_template(file_spec.path, context)
                rendered_path = rendered_path.strip().replace("\\", "/")
            except Exception as e:
                self.logger.error(f"Failed to render template for file path '{file_spec.path}': {e}")
                raise ValueError(f"Failed to render template for file path '{file_spec.path}': {e}")

            try:
                rendered_root = render_template(root, context)
                rendered_root = rendered_root.strip()
            except Exception as e:
                self.logger.error(f"Failed to render template for root '{root}': {e}")
                raise ValueError(f"Failed to render template for root '{root}': {e}")
            # Construct the full file system output path
            output_path = os.path.normpath(os.path.join(rendered_root, rendered_path))

            # Debug log the file details before writing
            self.logger.debug(f"Preparing to write file: {output_path}\nContent:\n{file_spec.content}")

            # Create parent directories if needed
            parent_dir = os.path.dirname(output_path)
            try:
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
            except Exception as e:
                self.logger.error(f"Failed to create directory '{parent_dir}': {e}")
                raise OSError(f"Failed to create directory '{parent_dir}': {e}")

            # Write the file content
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(file_spec.content or "")
            except Exception as e:
                self.logger.error(f"Failed to write file '{output_path}': {e}")
                raise OSError(f"Failed to write file '{output_path}': {e}")

            file_size = len(file_spec.content.encode("utf-8")) if file_spec.content else 0
            # Info log on success
            self.logger.info(f"Wrote file: {output_path} ({file_size} bytes)")
