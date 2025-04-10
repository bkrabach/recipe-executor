import os
from typing import Union, List

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template
from recipe_executor.protocols import ContextProtocol


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
    def __init__(self, config: dict, logger=None):
        # Initialize configuration and logger using the base step
        super().__init__(ReadFilesConfig(**config), logger)

    def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step: read one or more files, merge their contents as specified,
        and store the result into the context under the given artifact key.
        """
        # Normalize the input paths
        raw_paths = self.config.path
        if isinstance(raw_paths, str):
            # Check if the string contains comma-separated paths
            if "," in raw_paths:
                paths = [p.strip() for p in raw_paths.split(",") if p.strip()]
            else:
                paths = [raw_paths.strip()]
        elif isinstance(raw_paths, list):
            paths = raw_paths
        else:
            raise ValueError(f"Invalid type for path: {type(raw_paths)}")

        # Render template for each path
        rendered_paths: List[str] = []
        for path in paths:
            try:
                rendered = render_template(path, context)
                rendered_paths.append(rendered)
            except Exception as e:
                self.logger.error(f"Error rendering template for path '{path}': {e}")
                raise

        # Read file(s) and accumulate their contents
        # We store tuples of (identifier, content). For 'dict' mode, identifier is basename.
        file_contents: List[tuple] = []
        merge_mode = self.config.merge_mode

        for path in rendered_paths:
            self.logger.debug(f"Attempting to read file: {path}")

            if not os.path.exists(path):
                message = f"File not found: {path}"
                if self.config.optional:
                    self.logger.warning(message + " (optional file, handling accordingly)")
                    if merge_mode == "dict":
                        file_contents.append((os.path.basename(path), ""))
                    else:
                        # For concat mode, skip missing files
                        continue
                else:
                    raise FileNotFoundError(message)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.logger.info(f"Successfully read file: {path}")
                if merge_mode == "dict":
                    file_contents.append((os.path.basename(path), content))
                else:
                    file_contents.append((path, content))
            except Exception as e:
                self.logger.error(f"Error reading file '{path}': {e}")
                raise

        # If no content was read, handle accordingly
        if not file_contents:
            if self.config.optional:
                self.logger.info(f"No files were read; storing empty content for artifact '{self.config.artifact}'")
                final_content = {} if merge_mode == "dict" else ""
            else:
                raise FileNotFoundError(f"None of the specified files were found: {rendered_paths}")
        elif len(file_contents) == 1:
            # Single file behavior: maintain original behavior
            if merge_mode == "dict":
                final_content = {file_contents[0][0]: file_contents[0][1]}
            else:
                final_content = file_contents[0][1]
        else:
            # Multiple files handling
            if merge_mode == "dict":
                final_content = {filename: content for filename, content in file_contents}
            else:
                # Concatenate with newlines between each file's content, including a header with the file name
                content_list = []
                for identifier, content in file_contents:
                    header = os.path.basename(identifier)
                    content_list.append(f"{header}:\n{content}")
                final_content = "\n".join(content_list)

        # Store the final result into the context under the specified artifact key
        context[self.config.artifact] = final_content
        self.logger.info(f"Stored file content under artifact key '{self.config.artifact}' in context.")
