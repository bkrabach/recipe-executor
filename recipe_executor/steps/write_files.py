import logging
import os
from typing import List, Optional

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFileStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to '.'
    """

    artifact: str
    root: str = "."


class WriteFileStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes files to disk based on the provided artifact in the context.
    The artifact can be either a FileGenerationResult or a list of FileSpec objects.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize configuration using WriteFilesConfig
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the step: write files to disk by resolving paths using template rendering and
        creating directories as needed.

        Args:
            context (Context): Execution context containing artifacts and configuration.

        Raises:
            ValueError: If no artifact is found in the context.
            TypeError: If the artifact is not of an expected type.
            IOError: If file writing fails.
        """
        # Retrieve artifact from context
        data = context.get(self.config.artifact)

        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine file list based on artifact type
        if isinstance(data, FileGenerationResult):
            files: List[FileSpec] = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        # Check if output_dir is in the context, prioritize it over the config.root
        if "output_dir" in context:
            output_root = context["output_dir"]
            self.logger.info(f"Using output directory from context: {output_root}")
        else:
            # Render output root using the context to resolve any template variables
            output_root = render_template(self.config.root, context)
            self.logger.info(f"Using output root from config: {output_root}")

        # Process each file in the file list
        for file in files:
            # Render the file path from template variables
            rel_path = render_template(file.path, context)
            
            # Check if the path is already absolute
            if os.path.isabs(rel_path):
                full_path = rel_path
            else:
                # Check if the output path includes a recipe_executor path segment which might need to be handled differently
                if 'recipe_executor' in rel_path:
                    # This is a special case where we want to preserve the recipe_executor folder structure
                    self.logger.info(f"Preserving recipe_executor path structure for {rel_path}")
                    # No changes needed
                    pass
                elif rel_path.startswith(output_root) or os.path.abspath(rel_path) == output_root:
                    # If the path already contains the full output path, avoid duplication
                    self.logger.info(f"Path already contains full output path: {rel_path}")
                    # Use the path as is without joining with output_root
                    full_path = rel_path
                else:
                    # Check if rel_path already contains the output directory name to avoid duplication
                    output_dir_name = os.path.basename(output_root)
                    path_parts = rel_path.split(os.path.sep)
                    
                    if path_parts and path_parts[0] == output_dir_name:
                        # If the path already starts with the output directory name, avoid duplication
                        self.logger.info(f"Avoiding path duplication for {rel_path}")
                        # Remove the duplicated directory from the path
                        rel_path = os.path.sep.join(path_parts[1:]) if len(path_parts) > 1 else ""
                
                full_path = os.path.join(output_root, rel_path)

            # Create parent directories if they do not exist
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                except Exception as e:
                    self.logger.error(f"Failed to create directory {parent_dir}: {e}")
                    raise IOError(f"Error creating directory {parent_dir}: {e}")

            # Write file content to disk
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)
                self.logger.info(f"Wrote file: {full_path}")
            except Exception as e:
                self.logger.error(f"Failed to write file {full_path}: {e}")
                raise IOError(f"Error writing file {full_path}: {e}")
