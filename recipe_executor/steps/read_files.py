import logging
import os
from typing import Dict, List, Union

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
    def __init__(self, config: dict, logger: logging.Logger):
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the read files step.
        Reads one or multiple files, resolves templated paths, and stores the contents in the context.
        """
        # Resolve path configuration from the config
        raw_paths = self.config.path
        resolved_paths: List[str] = []

        # Determine if raw_paths is a single string or list
        if isinstance(raw_paths, str):
            # Render the template first
            rendered = render_template(raw_paths, context)
            # Check if comma-separated for multiple
            if "," in rendered:
                # Split and strip whitespace
                resolved_paths = [p.strip() for p in rendered.split(",") if p.strip()]
            else:
                resolved_paths = [rendered.strip()]
        elif isinstance(raw_paths, list):
            for path in raw_paths:
                # Each path may be templated
                rendered = render_template(path, context).strip()
                if rendered:
                    resolved_paths.append(rendered)
        else:
            raise ValueError(f"Invalid type for path: {type(raw_paths)}. Must be str or List[str].")

        self.logger.debug(f"Resolved file paths: {resolved_paths}")

        file_contents: Dict[str, str] = {}
        concat_contents: List[str] = []

        # Read each file
        for path in resolved_paths:
            self.logger.debug(f"Attempting to read file: {path}")
            if not os.path.exists(path):
                msg = f"File not found: {path}"
                if self.config.optional:
                    self.logger.warning(msg + " (optional, continuing with empty content)")
                    if self.config.merge_mode == "dict":
                        # Use base name as key
                        file_contents[os.path.basename(path)] = ""
                    # For concat mode, skip adding missing file
                    continue
                else:
                    self.logger.error(msg)
                    raise FileNotFoundError(msg)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.logger.info(f"Successfully read file: {path}")
            except Exception as e:
                msg = f"Error reading file {path}: {str(e)}"
                self.logger.error(msg)
                if self.config.optional:
                    self.logger.warning(f"Continuing execution as file is optional: {path}")
                    content = ""
                else:
                    raise RuntimeError(msg) from e

            if self.config.merge_mode == "dict":
                # Use the base filename as key
                file_contents[os.path.basename(path)] = content
            else:
                # For concat, include a header with the filename
                header = f"----- {os.path.basename(path)} -----"
                concat_contents.append(header)
                concat_contents.append(content)

        # Determine output based on number of files and merge mode
        result = ""
        if len(resolved_paths) == 1:
            # For backwards compatibility, if single file, store its contents directly
            if self.config.merge_mode == "dict":
                # Even if a single file but merge_mode dict is desired
                key = os.path.basename(resolved_paths[0])
                result = {key: file_contents.get(key, "")}
            else:
                # For concat mode, if a single file, directly use its content (or empty string if missing)
                # If the file was optional and missing, content might not be in our list
                if concat_contents:
                    # Remove the header if present
                    # The expected pattern: header then content
                    if len(concat_contents) >= 2:
                        result = concat_contents[1]
                    else:
                        result = ""
                else:
                    result = ""
        else:
            # Multiple files
            if self.config.merge_mode == "dict":
                result = file_contents
            else:
                result = "\n".join(concat_contents)

        # Store the result in the context under the specified artifact key
        context[self.config.artifact] = result
        self.logger.info(f"Stored file contents under context key '{self.config.artifact}'")
