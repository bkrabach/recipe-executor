from typing import Any, Dict, List, Optional, Union
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils import render_template
import logging
import os


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        contents_key (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + contents
            - "dict": Store a dictionary with filenames as keys and contents as values
    """
    path: Union[str, List[str]]
    contents_key: str
    optional: bool = False
    merge_mode: str = "concat"

class ReadFilesStep(BaseStep[ReadFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        config: ReadFilesConfig = self.config
        # Resolve and normalize paths
        paths: List[str] = self._resolve_paths(config.path, context)

        contents_key: str = config.contents_key
        optional: bool = config.optional
        merge_mode: str = config.merge_mode or "concat"

        file_contents: List[str] = []
        contents_dict: Dict[str, str] = {}
        files_read: List[str] = []
        missing_files: List[str] = []

        for path in paths:
            rendered_path = render_template(path, context)
            self.logger.debug(f"ReadFilesStep: Attempting to read file: '{rendered_path}'")
            try:
                with open(rendered_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.logger.info(f"ReadFilesStep: Successfully read file: '{rendered_path}'")
                files_read.append(rendered_path)
                if merge_mode == "dict":
                    contents_dict[rendered_path] = content
                else:
                    file_contents.append(f"# ===== {rendered_path} =====\n{content}")
            except FileNotFoundError:
                self.logger.warning(f"ReadFilesStep: File not found: '{rendered_path}'")
                missing_files.append(rendered_path)
                if not optional:
                    raise FileNotFoundError(
                        f"ReadFilesStep: Required file not found: '{rendered_path}' (contents_key: '{contents_key}')"
                    )
                # optional: proceed
                if merge_mode == "dict":
                    # Omit missing file in dict mode
                    pass
                # In concat mode, skip missing file

        # Backwards compatibility: if only one file, keep old behavior for both modes
        if len(paths) == 1:
            if files_read:
                val: Union[str, Dict[str, str]]
                if merge_mode == "dict":
                    val = {files_read[0]: contents_dict[files_read[0]]}
                else:
                    val = file_contents[0]
                context[contents_key] = val
                self.logger.info(f"ReadFilesStep: Stored contents of '{files_read[0]}' under key '{contents_key}'")
            else:
                # Single file missing
                context[contents_key] = ""
                self.logger.info(
                    f"ReadFilesStep: Stored empty contents for missing file under key '{contents_key}' (file: '{paths[0]}')"
                )
            return

        # Multiple files:
        if merge_mode == "dict":
            context[contents_key] = contents_dict
            self.logger.info(
                f"ReadFilesStep: Stored contents of {len(contents_dict)} files as a dictionary under key '{contents_key}'"
            )
        else:
            # default/"concat": join all non-missing contents
            concat = "\n\n".join(file_contents)
            context[contents_key] = concat
            self.logger.info(
                f"ReadFilesStep: Stored concatenated contents of {len(files_read)} files under key '{contents_key}'"
            )

    def _resolve_paths(self, path_param: Union[str, List[str]], context: ContextProtocol) -> List[str]:
        """
        Resolve template(s) and normalize input to a list of file paths.
        """
        if isinstance(path_param, str):
            rendered = render_template(path_param, context)
            if "," in rendered:
                paths = [x.strip() for x in rendered.split(",") if x.strip()]
            else:
                paths = [rendered.strip()]
        elif isinstance(path_param, list):
            paths: List[str] = []
            for p in path_param:
                rendered = render_template(str(p), context)
                if "," in rendered:
                    paths.extend([x.strip() for x in rendered.split(",") if x.strip()])
                else:
                    paths.append(rendered.strip())
        else:
            raise ValueError("ReadFilesStep: Invalid path parameter. Must be a string or a list of strings.")
        return paths
