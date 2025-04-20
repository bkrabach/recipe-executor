import logging
import os
from typing import Any, Dict, List, Union

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


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
        rendered_path: Union[str, List[str]] = self._render_paths(self.config.path, context)
        paths: List[str] = self._parse_paths(rendered_path)

        if not paths:
            self.logger.info(f"No files to read for key '{self.config.contents_key}' (path: {self.config.path})")
            if self.config.merge_mode == "dict":
                context[self.config.contents_key] = {}
            else:
                context[self.config.contents_key] = ""
            return

        self.logger.debug(f"Resolved paths for reading: {paths}")

        contents_list: List[str] = []
        contents_dict: Dict[str, str] = {}
        missing_files: List[str] = []

        for path in paths:
            path_stripped: str = path.strip()
            self.logger.debug(f"Attempting to read file: {path_stripped}")
            if not os.path.isfile(path_stripped):
                if self.config.optional:
                    self.logger.warning(f"Optional file not found: {path_stripped} (step continues)")
                    missing_files.append(path_stripped)
                    continue
                else:
                    error_msg: str = f"File not found: {path_stripped} (required by read_files step)"
                    self.logger.error(error_msg)
                    raise FileNotFoundError(error_msg)
            try:
                with open(path_stripped, encoding="utf-8") as file:
                    content: str = file.read()
                self.logger.info(f"Read file successfully: {path_stripped}")
                if self.config.merge_mode == "dict":
                    contents_dict[path_stripped] = content
                else:
                    contents_list.append(content)
            except Exception as exc:
                error_msg: str = f"Failed to read file {path_stripped}: {str(exc)}"
                if self.config.optional:
                    self.logger.warning(error_msg)
                    missing_files.append(path_stripped)
                    continue
                else:
                    self.logger.error(error_msg)
                    raise

        result: Union[str, Dict[str, str]]
        if self.config.merge_mode == "dict":
            result = contents_dict
        else:
            result = "\n".join(contents_list)

        # Backwards compatibility: optional + single file
        if len(paths) == 1 and self.config.merge_mode != "dict" and self.config.optional and not contents_list:
            result = ""

        context[self.config.contents_key] = result
        self.logger.info(
            f"Stored contents under key '{self.config.contents_key}' (mode: {self.config.merge_mode}, files read: {len(contents_list)})"
        )

    def _render_paths(self, path: Union[str, List[str]], context: ContextProtocol) -> Union[str, List[str]]:
        if isinstance(path, str):
            return render_template(path, context)
        if isinstance(path, list):
            return [render_template(single_path, context) for single_path in path]
        return path

    def _parse_paths(self, rendered_path: Union[str, List[str]]) -> List[str]:
        paths: List[str] = []
        if isinstance(rendered_path, str):
            if "," in rendered_path:
                parts: List[str] = [part.strip() for part in rendered_path.split(",") if part.strip()]
                paths.extend(parts)
            elif rendered_path.strip():
                paths.append(rendered_path.strip())
        elif isinstance(rendered_path, list):
            for element in rendered_path:
                if "," in element:
                    parts: List[str] = [part.strip() for part in element.split(",") if part.strip()]
                    paths.extend(parts)
                elif element.strip():
                    paths.append(element.strip())
        return paths
