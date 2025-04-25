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
        files_key: Optional[str] - Context key holding a List[FileSpec] or single FileSpec.
        files: Optional[List[Dict[str, Any]]] - Direct list of dicts with 'path' and 'content' (or content_key/path_key).
        root: str - Base path to prepend to all output file paths (default ".").
    """

    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        files_to_write: List[Dict[str, Any]] = []
        root: str = render_template(self.config.root or ".", context)

        # Prefer files param, fallback to files_key in context
        if self.config.files is not None:
            for file_in in self.config.files:
                # Extract path
                if "path" in file_in:
                    raw_path = file_in["path"]
                elif "path_key" in file_in:
                    key = file_in["path_key"]
                    if key not in context:
                        raise KeyError(f"Path key '{key}' not found in context.")
                    raw_path = context[key]
                else:
                    raise ValueError("Each file entry must have either 'path' or 'path_key'.")
                # Render path template
                path = render_template(str(raw_path), context)

                # Extract content
                if "content" in file_in:
                    content_raw = file_in["content"]
                elif "content_key" in file_in:
                    key = file_in["content_key"]
                    if key not in context:
                        raise KeyError(f"Content key '{key}' not found in context.")
                    content_raw = context[key]
                else:
                    raise ValueError("Each file entry must have either 'content' or 'content_key'.")
                # Render content template if string
                content = render_template(content_raw, context) if isinstance(content_raw, str) else content_raw
                files_to_write.append({"path": path, "content": content})
        elif self.config.files_key is not None:
            if self.config.files_key not in context:
                raise KeyError(f"Files key '{self.config.files_key}' not found in context.")
            files_data = context[self.config.files_key]
            # Support single FileSpec or list
            files_raw: Union[FileSpec, Dict[str, Any], List[Any]] = files_data
            if isinstance(files_raw, FileSpec):
                files_raw = [files_raw]
            elif isinstance(files_raw, dict):
                # Could be a dict with path and content
                if "path" in files_raw and "content" in files_raw:
                    files_raw = [files_raw]
                else:
                    raise ValueError(f"Malformed file dict under '{self.config.files_key}'.")

            for file_item in files_raw:
                # Accept FileSpec or dict
                if isinstance(file_item, FileSpec):
                    path = render_template(file_item.path, context)
                    content = file_item.content
                elif isinstance(file_item, dict):
                    if "path" not in file_item or "content" not in file_item:
                        raise ValueError(f"Invalid file entry in list under '{self.config.files_key}': {file_item}")
                    path = render_template(str(file_item["path"]), context)
                    content = file_item["content"]
                else:
                    raise ValueError("Each file entry must be FileSpec or dict with 'path' and 'content'.")

                # Render content template if string
                content = render_template(content, context) if isinstance(content, str) else content
                files_to_write.append({"path": path, "content": content})
        else:
            raise ValueError("Either 'files' or 'files_key' must be provided in WriteFilesConfig.")

        # Write files
        for file_out in files_to_write:
            try:
                final_path = os.path.join(root, file_out["path"]) if root else file_out["path"]
                final_path = os.path.normpath(final_path)
                parent_dir = os.path.dirname(final_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                content = file_out["content"]

                # Always render template on content if it's a string (already done above)

                # Before writing, if content is dict or list, serialize to JSON
                to_write: str
                if isinstance(content, (dict, list)):
                    try:
                        to_write = json.dumps(content, ensure_ascii=False, indent=2)
                    except Exception as err:
                        raise ValueError(f"Failed to serialize content for {final_path}: {err}")
                else:
                    to_write = content
                # Logging before write
                self.logger.debug(f"[WriteFilesStep] Writing file: {final_path}\nContent:\n{to_write}")
                # Write file (UTF-8, overwrite)
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(to_write)
                self.logger.info(f"[WriteFilesStep] Wrote file: {final_path} ({len(to_write.encode('utf-8'))} bytes)")
            except Exception as err:
                self.logger.error(f"[WriteFilesStep] Error writing file '{file_out.get('path', '?')}': {err}")
                raise
