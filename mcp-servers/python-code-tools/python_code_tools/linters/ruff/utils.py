# filepath: mcp-servers/python-code-tools/python_code_tools/linters/ruff/utils.py
import hashlib
from pathlib import Path
from typing import Dict, List


async def get_file_hashes(path: Path, file_paths: List[str]) -> Dict[str, str]:
    """Get MD5 hashes of files for change detection.

    Args:
        path: Project directory path
        file_paths: List of file paths

    Returns:
        Dictionary mapping file paths to MD5 hashes
    """

    hashes = {}

    for file_path in file_paths:
        abs_path = path / file_path
        try:
            with open(abs_path, "rb") as f:
                content = f.read()
                hashes[file_path] = hashlib.md5(content).hexdigest()
        except Exception:
            # Skip files we can't read
            pass

    return hashes


def get_modified_files(before_hashes: Dict[str, str], after_hashes: Dict[str, str]) -> List[str]:
    """Determine which files were modified by comparing hashes.

    Args:
        before_hashes: File hashes before modification
        after_hashes: File hashes after modification

    Returns:
        List of modified file paths
    """
    modified_files = []

    for file_path, before_hash in before_hashes.items():
        if file_path in after_hashes:
            after_hash = after_hashes[file_path]
            if before_hash != after_hash:
                modified_files.append(file_path)

    return modified_files
