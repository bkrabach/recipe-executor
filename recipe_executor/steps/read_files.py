import os
from typing import Any, List, Union

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found. Defaults to False.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + content
            - "dict": Store a dictionary with filenames as keys and contents as values
    """
    path: Union[str, List[str]]
    artifact: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    Step to read one or more files from the filesystem and store their contents in the execution context.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        # Convert dict to ReadFilesConfig
        super().__init__(ReadFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Reads file(s) from the filesystem based on the resolved path(s) and stores the results
        in the context under the configured artifact key.

        For a single file, the content is stored directly as a string. For multiple files, the
        behavior depends on the merge_mode:
          - "concat": Concatenates file contents with newlines between filenames and content
          - "dict": Stores a dict with the file's basename as the key and file content as the value

        Args:
            context (Context): The execution context

        Raises:
            FileNotFoundError: If a required file is missing
            ValueError: If an unsupported merge_mode is provided
        """
        # Resolve the file paths using the context
        raw_paths = self.config.path
        resolved_paths: List[str] = []

        if isinstance(raw_paths, str):
            # Render the template on the entire string
            rendered = render_template(raw_paths, context)
            # If comma is present, treat it as multiple paths
            if "," in rendered:
                resolved_paths = [part.strip() for part in rendered.split(",") if part.strip()]
            else:
                resolved_paths = [rendered.strip()]
        elif isinstance(raw_paths, list):
            for path_entry in raw_paths:
                rendered = render_template(path_entry, context)
                if rendered:
                    resolved_paths.append(rendered.strip())
        else:
            raise ValueError(f"Invalid type for path: {type(raw_paths)}. Must be str or list of str.")

        # Data structure to hold file contents
        file_contents = {}
        concat_list = []

        for file_path in resolved_paths:
            self.logger.debug(f"Attempting to read file: {file_path}")
            if not os.path.exists(file_path):
                if self.config.optional:
                    self.logger.warning(f"Optional file not found: {file_path}")
                    # Depending on merge_mode, record an empty content
                    if self.config.merge_mode == "dict":
                        file_contents[os.path.basename(file_path)] = ""
                    # For concat, we skip adding missing file's content
                    continue
                else:
                    raise FileNotFoundError(f"Required file not found: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.logger.info(f"Successfully read file: {file_path}")
            except Exception as e:
                raise RuntimeError(f"Error reading file {file_path}: {e}")

            if self.config.merge_mode == "dict":
                key = os.path.basename(file_path)
                file_contents[key] = content
            elif self.config.merge_mode == "concat":
                concat_list.append(f"{file_path}\n{content}")
            else:
                raise ValueError(f"Unsupported merge_mode: {self.config.merge_mode}")

        # Determine final content
        if self.config.merge_mode == "concat":
            if len(resolved_paths) == 1 and not self.config.optional:
                # Backwards compatibility: single file returns raw content
                # But only if the file was successfully read
                # If file was missing and optional then file would be skipped, so we join concat_list
                final_content = concat_list[0] if concat_list else ""
            else:
                final_content = "\n".join(concat_list)
        else:  # merge_mode is "dict"
            final_content = file_contents

        # Store the result in the context under the rendered artifact key
        artifact_key = render_template(self.config.artifact, context)
        context[artifact_key] = final_content
        self.logger.info(f"Stored file content under key '{artifact_key}' in context.")


# If step registry is used, register the step
try:
    from recipe_executor.steps.registry import STEP_REGISTRY
    STEP_REGISTRY["read_files"] = ReadFilesStep
except ImportError:
    # In case the registry is not available in some contexts
    pass
