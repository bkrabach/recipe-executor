import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import yaml

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        content_key (str): Name under which to store file content in the context.
        optional (bool): Whether to continue if a file is not found (default: False).
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filename headers + content
            - "dict": Store a dictionary with file paths as keys and content as values
    """
    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    Step that reads one or more files from disk and stores their content in the execution context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        cfg = self.config
        raw_path = cfg.path
        paths: List[str] = []

        # Resolve and normalize paths (with template rendering)
        if isinstance(raw_path, str):
            rendered = render_template(raw_path, context)
            # Split comma-separated string into list
            if "," in rendered:
                parts = [p.strip() for p in rendered.split(",") if p.strip()]
                paths.extend(parts)
            else:
                paths.append(rendered)
        elif isinstance(raw_path, list):
            for entry in raw_path:
                if not isinstance(entry, str):
                    raise ValueError(f"Invalid path entry type: {entry!r}")
                rendered = render_template(entry, context)
                paths.append(rendered)
        else:
            raise ValueError(f"Invalid type for path: {type(raw_path)}")

        results: List[Any] = []
        result_map: Dict[str, Any] = {}

        for path in paths:
            self.logger.debug(f"Reading file at path: {path}")
            if not os.path.exists(path):
                msg = f"File not found: {path}"
                if cfg.optional:
                    self.logger.warning(f"Optional file missing, skipping: {path}")
                    continue
                raise FileNotFoundError(msg)

            # Read file content as UTF-8 text
            with open(path, mode="r", encoding="utf-8") as f:
                text = f.read()

            # Attempt to deserialize structured formats
            ext = os.path.splitext(path)[1].lower()
            content: Any = text
            try:
                if ext == ".json":
                    content = json.loads(text)
                elif ext in (".yaml", ".yml"):
                    content = yaml.safe_load(text)
            except Exception as exc:
                self.logger.warning(f"Failed to parse structured data from {path}: {exc}")
                content = text

            self.logger.info(f"Successfully read file: {path}")
            results.append(content)
            result_map[path] = content

        # Merge results according to merge_mode
        final_content: Any
        if not results:
            # No file was read
            if len(paths) <= 1:
                final_content = ""  # Single (missing) file yields empty string
            elif cfg.merge_mode == "dict":
                final_content = {}  # Dict of zero entries
            else:
                final_content = ""  # Concat yields empty string
        elif len(results) == 1:
            # Only one file read => return its content directly
            final_content = results[0]
        else:
            # Multiple files read
            if cfg.merge_mode == "dict":
                final_content = result_map
            else:
                # Default: concat mode, include header with filename
                segments: List[str] = []
                for p in paths:
                    if p in result_map:
                        raw = result_map[p]
                        # Convert raw back to text if it was structured
                        segment = raw if isinstance(raw, str) else json.dumps(raw)
                        segments.append(f"{p}\n{segment}")
                final_content = "\n".join(segments)

        # Store the merged content in context
        context[cfg.content_key] = final_content
        self.logger.info(f"Stored file content under key '{cfg.content_key}'")
