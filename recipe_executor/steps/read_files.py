import logging
from typing import Any, Dict, List, Optional, Union
import os

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
        
        config: ReadFilesConfig = self.config
        logger: logging.Logger = self.logger

        # Render template for path parameter (supports string or list)
        raw_path = config.path
        rendered_paths: List[str] = []

        # Handle string or list of paths
        if isinstance(raw_path, str):
            rendered_raw = render_template(raw_path, context)
            # Detect commas for multi-file as single string
            if "," in rendered_raw:
                rendered_paths = [p.strip() for p in rendered_raw.split(",") if p.strip()]
            else:
                rendered_paths = [rendered_raw.strip()] if rendered_raw.strip() else []
        elif isinstance(raw_path, list):
            for item in raw_path:
                path_templated = render_template(item, context)
                if path_templated.strip():
                    rendered_paths.append(path_templated.strip())
        else:
            logger.error(f"Invalid type for 'path': {type(raw_path).__name__}")
            raise TypeError(f"'path' must be a string or list of strings, got: {type(raw_path).__name__}")

        if not rendered_paths:
            logger.warning("No file paths provided after template rendering.")
        
        is_multi_file: bool = len(rendered_paths) > 1

        file_contents: List[str] = []
        file_dict: Dict[str, str] = {}
        successful_paths: List[str] = []

        for file_path in rendered_paths:
            logger.debug(f"[ReadFilesStep] Attempting to read file: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                logger.info(f"Successfully read file: {file_path}")
                if config.merge_mode == "dict":
                    file_dict[file_path] = content
                else:
                    file_contents.append(content)
                successful_paths.append(file_path)
            except FileNotFoundError:
                if config.optional:
                    logger.warning(f"File not found (optional): {file_path}")
                    continue
                else:
                    logger.error(f"File not found: {file_path}")
                    raise FileNotFoundError(f"Required file not found: {file_path}")
            except Exception as exc:
                logger.error(f"Error reading file {file_path}: {exc}")
                raise

        contents_to_store: Any = None

        if is_multi_file:
            if config.merge_mode == "dict":
                # Only include successfully read files
                contents_to_store = file_dict
            else:  # concat (default)
                # Concatenate, separated by newlines
                contents_to_store = "\n".join(file_contents)
        else:
            # Single file: preserve original behavior
            if file_contents:
                contents_to_store = file_contents[0]
            elif config.optional:
                contents_to_store = ""
            else:
                # Should not reach here unless nothing was read and optional=False, which would have errored above
                logger.error("No content read and file not optional.")
                raise FileNotFoundError("Required file not found or empty path list.")

        context[config.contents_key] = contents_to_store
        logger.info(
            f"Stored file contents under key '{config.contents_key}'"
            f" (mode: {config.merge_mode}, files: {successful_paths if successful_paths else rendered_paths})"
        )
