import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        files_key: Optional context key holding FileSpec or list of FileSpec.
        files: Optional direct list of dicts with 'path' and 'content' (or keys).
        root: Base path for output files.
    """
    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes files to disk based on FileSpec or dict inputs.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        files_to_write: List[Dict[str, Any]] = []
        # Render root path template
        root: str = render_template(self.config.root or ".", context)

        # Direct files list takes precedence
        if self.config.files is not None:
            for entry in self.config.files:
                # Path extraction
                if "path" in entry:
                    raw_path = entry["path"]
                elif "path_key" in entry:
                    key = entry["path_key"]
                    if key not in context:
                        raise KeyError(f"Path key '{key}' not found in context.")
                    raw_path = context[key]
                else:
                    raise ValueError("Each file entry must have 'path' or 'path_key'.")
                path = render_template(str(raw_path), context)

                # Content extraction
                if "content" in entry:
                    raw_content = entry["content"]
                elif "content_key" in entry:
                    key = entry["content_key"]
                    if key not in context:
                        raise KeyError(f"Content key '{key}' not found in context.")
                    raw_content = context[key]
                else:
                    raise ValueError("Each file entry must have 'content' or 'content_key'.")

                content: Any
                if isinstance(raw_content, str):
                    content = render_template(raw_content, context)
                else:
                    content = raw_content

                files_to_write.append({"path": path, "content": content})

        elif self.config.files_key is not None:
            key = self.config.files_key
            if key not in context:
                raise KeyError(f"Files key '{key}' not found in context.")
            raw = context[key]
            # Normalize to list of specs or dicts
            if isinstance(raw, FileSpec):
                items = [raw]
            elif isinstance(raw, dict):
                if "path" in raw and "content" in raw:
                    items = [raw]
                else:
                    raise ValueError(f"Malformed file dict under '{key}'.")
            elif isinstance(raw, list):  # type: ignore
                items = raw  # type: ignore
            else:
                raise ValueError(f"Unsupported type for files_key '{key}': {type(raw)}")

            for file_item in items:
                if isinstance(file_item, FileSpec):
                    path = render_template(file_item.path, context)
                    content_raw = file_item.content
                elif isinstance(file_item, dict):
                    if "path" not in file_item or "content" not in file_item:
                        raise ValueError(f"Invalid file entry under '{key}': {file_item}")
                    path = render_template(str(file_item["path"]), context)
                    content_raw = file_item["content"]
                else:
                    raise ValueError("Each file entry must be FileSpec or dict with 'path' and 'content'.")

                if isinstance(content_raw, str):
                    content = render_template(content_raw, context)
                else:
                    content = content_raw

                files_to_write.append({"path": path, "content": content})

        else:
            raise ValueError("Either 'files' or 'files_key' must be provided in WriteFilesConfig.")

        # Write out each file
        for file_entry in files_to_write:
            try:
                relative_path = file_entry.get("path", "")
                final_path = os.path.normpath(os.path.join(root, relative_path)) if root else os.path.normpath(relative_path)
                parent = os.path.dirname(final_path)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)

                content = file_entry.get("content")
                # Serialize dict or list to JSON
                if isinstance(content, (dict, list)):
                    try:
                        to_write = json.dumps(content, ensure_ascii=False, indent=2)
                    except Exception as err:
                        raise ValueError(f"Failed to serialize content for '{final_path}': {err}")
                else:
                    to_write = content  # type: ignore

                # Debug log before write
                self.logger.debug(f"[WriteFilesStep] Writing file: {final_path}\nContent:\n{to_write}")
                # Write file
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(to_write)

                size = len(to_write.encode("utf-8")) if isinstance(to_write, str) else 0
                self.logger.info(f"[WriteFilesStep] Wrote file: {final_path} ({size} bytes)")

            except Exception as exc:
                self.logger.error(f"[WriteFilesStep] Error writing file '{file_entry.get('path', '?')}': {exc}")
                raise
