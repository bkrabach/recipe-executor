import os
import logging
from typing import List, Union, Optional, Dict

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.utils import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path or list of paths to the file(s) to read (may be templated).
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
    A step that reads one or more files from the filesystem and stores their contents in the execution context.

    It supports both single file and multiple file operations, template-based path resolution,
    and flexible merging modes for multiple files.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to ReadFilesConfig instance
        super().__init__(ReadFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the file reading step. Resolves template-based paths, reads file(s), handles optional files,
        and stores the content into the context using the artifact key.

        Args:
            context (Context): The execution context.

        Raises:
            FileNotFoundError: If a required file does not exist.
        """
        # Resolve artifact key using template rendering
        artifact_key = render_template(self.config.artifact, context)

        # Ensure paths is a list
        paths_input = self.config.path
        if isinstance(paths_input, str):
            paths_list: List[str] = [paths_input]
        else:
            paths_list = paths_input

        # This will hold the results for multiple files
        file_contents: Union[str, Dict[str, str]] = "" if self.config.merge_mode == "concat" else {}
        multiple_files = len(paths_list) > 1

        # Temp storage for individual file contents
        contents_list: List[str] = []
        contents_dict: Dict[str, str] = {}

        for path_template in paths_list:
            # Render the file path using the context
            rendered_path = render_template(path_template, context)
            self.logger.debug(f"Attempting to read file: {rendered_path}")

            if not os.path.exists(rendered_path):
                message = f"File not found: {rendered_path}"
                if self.config.optional:
                    self.logger.warning(message + " [optional]")
                    # For optional files, handle based on merge mode
                    if multiple_files and self.config.merge_mode == "dict":
                        # Use the basename as key with empty content
                        contents_dict[os.path.basename(rendered_path)] = ""
                    elif multiple_files and self.config.merge_mode == "concat":
                        # Skip file in concatenation mode
                        continue
                    else:
                        # Single file optional: store empty string
                        file_contents = ""
                        self.logger.info(f"Stored empty content for optional file: {rendered_path}")
                        context[artifact_key] = file_contents
                        continue
                else:
                    self.logger.error(message)
                    raise FileNotFoundError(message)
            else:
                try:
                    with open(rendered_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.logger.info(f"Successfully read file: {rendered_path}")
                except Exception as e:
                    self.logger.error(f"Error reading file {rendered_path}: {str(e)}")
                    raise e

                # Process content based on merge mode
                if multiple_files:
                    if self.config.merge_mode == "dict":
                        key = os.path.basename(rendered_path)
                        contents_dict[key] = content
                    else:  # Default to 'concat'
                        # Append filename and content separated by newlines
                        formatted = f"{rendered_path}\n{content}"
                        contents_list.append(formatted)
                else:
                    # Single file; simply assign content
                    file_contents = content

        # Merge file contents if multiple files
        if multiple_files:
            if self.config.merge_mode == "dict":
                file_contents = contents_dict
            else:  # concat
                # Join each file's formatted content with double newlines
                file_contents = "\n\n".join(contents_list)

        # Store the final content under the artifact key in the context
        context[artifact_key] = file_contents
        self.logger.info(f"Stored file content under key: '{artifact_key}'")
