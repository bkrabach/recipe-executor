import os
import logging
from typing import Any, List, Union, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + contents
            - "dict": Store a dictionary with filenames as keys and contents as values
    """

    path: Union[str, List[str]]
    artifact: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    ReadFilesStep reads one or more files from the filesystem, processes templated paths, and stores their content
    in the execution context under the specified artifact key. It supports single or multiple file reads and
    flexible content merging options.
    """
    
    def __init__(self, config: Any, logger: Optional[logging.Logger] = None) -> None:
        # Ensure config is a ReadFilesConfig object, not a raw dict
        if not isinstance(config, ReadFilesConfig):
            config = ReadFilesConfig(**config)
        super().__init__(config, logger)
    
    async def execute(self, context: ContextProtocol) -> None:
        # Resolve the raw paths from configuration
        raw_paths: Union[str, List[str]] = self.config.path
        file_paths: List[str] = []

        if isinstance(raw_paths, list):
            file_paths = raw_paths
        elif isinstance(raw_paths, str):
            if "," in raw_paths:
                file_paths = [p.strip() for p in raw_paths.split(",") if p.strip()]
            else:
                file_paths = [raw_paths.strip()]
        else:
            raise ValueError(f"Unsupported type for path: {type(raw_paths)}")

        # Render template for each path
        rendered_paths: List[str] = []
        for path in file_paths:
            try:
                rendered = render_template(path, context)
                rendered_paths.append(rendered)
                self.logger.debug(f"Rendered path: '{path}' to '{rendered}'")
            except Exception as e:
                self.logger.error(f"Error rendering template for path '{path}': {e}")
                raise

        # Initialize storage based on merge_mode
        merge_mode = self.config.merge_mode.lower()
        # For single file, even with concat mode, we return a string for backward compatibility
        is_single = len(rendered_paths) == 1

        # Initialize both storage variables to avoid "possibly unbound" errors
        aggregated_result: dict = {}
        aggregated_result_list: List[str] = []
        final_content: Any = None

        # Validate merge_mode
        if merge_mode not in ["dict", "concat"]:
            raise ValueError(f"Unsupported merge_mode: {self.config.merge_mode}")

        # Iterate over each rendered file path and read the contents
        for rendered_path in rendered_paths:
            self.logger.debug(f"Attempting to read file: {rendered_path}")
            if not os.path.exists(rendered_path):
                msg = f"File not found: {rendered_path}"
                if self.config.optional:
                    self.logger.warning(msg + " (optional file, continuing)")
                    if merge_mode == "dict":
                        # Use empty string for missing optional file
                        key = os.path.basename(rendered_path)
                        aggregated_result[key] = ""
                    elif merge_mode == "concat":
                        # For single file, assign empty string; for multiple files, skip missing file
                        if is_single:
                            aggregated_result_list.append("")
                        else:
                            self.logger.debug(f"Skipping missing optional file: {rendered_path}")
                    continue
                else:
                    self.logger.error(msg)
                    raise FileNotFoundError(msg)

            try:
                with open(rendered_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.logger.info(f"Successfully read file: {rendered_path}")
            except Exception as e:
                self.logger.error(f"Error reading file {rendered_path}: {e}")
                raise

            if merge_mode == "dict":
                key = os.path.basename(rendered_path)
                aggregated_result[key] = content
            elif merge_mode == "concat":
                # For multiple files, include a header with the filename
                if is_single:
                    aggregated_result_list.append(content)
                else:
                    header = f"File: {os.path.basename(rendered_path)}"
                    aggregated_result_list.append(f"{header}\n{content}")

        # Finalize artifact based on merge_mode
        if merge_mode == "dict":
            final_content: Any = aggregated_result
        elif merge_mode == "concat":
            if is_single:
                final_content = aggregated_result_list[0] if aggregated_result_list else ""
            else:
                final_content = "\n\n".join(aggregated_result_list)

        # Store the result in context under the specified artifact key
        context[self.config.artifact] = final_content
        self.logger.info(f"Stored file content under context key '{self.config.artifact}'")
