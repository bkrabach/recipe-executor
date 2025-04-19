"""Temporary file handling utilities."""

import os
import tempfile
from pathlib import Path
from typing import IO, Any, Tuple


def create_temp_file(content: str, suffix: str = ".txt") -> Tuple[IO[Any], Path]:
    """Create a temporary file with the given content.

    Args:
        content: The content to write to the file
        suffix: The file suffix/extension

    Returns:
        A tuple containing the temporary file object and the path to the file
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    file_path = Path(temp_file.name)

    with open(file_path, "w") as f:
        f.write(content)

    return temp_file, file_path


def cleanup_temp_file(temp_file: IO[Any], file_path: Path) -> None:
    """Clean up a temporary file.

    Args:
        temp_file: The temporary file object
        file_path: The path to the file
    """
    temp_file.close()
    if os.path.exists(file_path):
        os.unlink(file_path)
