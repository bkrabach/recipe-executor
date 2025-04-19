import logging
from typing import Any, Dict, List, Union

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.
    Fields:
        path (Union[str, List[str]]): Path(s) to file(s) to read (can be templated, comma-separated, or list).
        contents_key (str): Name for storing result in context.
        optional (bool): Whether to continue if any file does not exist.
        merge_mode (str): How to merge contents: 'concat' (default) or 'dict'.
    """

    path: Union[str, List[str]]
    contents_key: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve paths (as templates)
        raw_path: Union[str, List[str]] = self.config.path
        paths: List[str] = []

        if isinstance(raw_path, str):
            rendered: str = render_template(raw_path, context)
            if "," in rendered:
                split_paths = [p.strip() for p in rendered.split(",") if p.strip()]
                paths = split_paths
            else:
                paths = [rendered.strip()]
        elif isinstance(raw_path, list):
            for p in raw_path:
                rendered = render_template(str(p), context)
                if "," in rendered:
                    split_paths = [s.strip() for s in rendered.split(",") if s.strip()]
                    paths.extend(split_paths)
                else:
                    paths.append(rendered.strip())
        else:
            raise ValueError("'path' must be a string or a list of strings")

        # Remove empty/duplicate paths
        seen = set()
        deduped_paths: List[str] = []
        for path in paths:
            if path and path not in seen:
                deduped_paths.append(path)
                seen.add(path)
        paths = deduped_paths

        contents_key: str = self.config.contents_key
        optional: bool = self.config.optional
        merge_mode: str = self.config.merge_mode or "concat"

        is_multiple: bool = len(paths) > 1
        file_contents: Dict[str, str] = {}
        missing_files: List[str] = []

        # Read each file
        for path in paths:
            self.logger.debug(f"ReadFilesStep: Attempting to read file: {path}")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                file_contents[path] = content
                self.logger.info(f"ReadFilesStep: Successfully read file: {path}")
            except FileNotFoundError:
                self.logger.warning(f"ReadFilesStep: File not found: {path}")
                missing_files.append(path)
                if not optional:
                    raise FileNotFoundError(f"ReadFilesStep: Required file not found: {path}")
            except Exception as exc:
                self.logger.error(f"ReadFilesStep: Error reading file '{path}': {exc}")
                raise

        # Store result in context
        if is_multiple:
            if merge_mode == "dict":
                result = file_contents
            else:  # default: concat
                concat_list: List[str] = []
                for path in paths:
                    if path in file_contents:
                        concat_list.append(f"# {path}\n{file_contents[path]}")
                result = "\n\n".join(concat_list)
        else:
            path = paths[0] if paths else ""
            if path and path in file_contents:
                result = file_contents[path]
            else:
                result = ""

        context[contents_key] = result
        self.logger.info(f"ReadFilesStep: Stored file contents under key '{contents_key}' in context.")
