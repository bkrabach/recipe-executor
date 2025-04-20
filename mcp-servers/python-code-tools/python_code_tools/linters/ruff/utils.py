import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List


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


def make_path_relative(file_path: str, project_path: str) -> str:
    """Convert absolute paths to project-relative paths.

    Args:
        file_path: Absolute or relative file path
        project_path: Base project path

    Returns:
        Path relative to the project directory
    """
    try:
        # If it's already a relative path, return it
        if not os.path.isabs(file_path):
            return file_path

        # Convert absolute path to relative path
        rel_path = os.path.relpath(file_path, project_path)

        # Remove leading ./ if present
        if rel_path.startswith("./"):
            rel_path = rel_path[2:]

        return rel_path
    except Exception:
        # If any error occurs, return the original path
        return file_path


def convert_issue_paths_to_relative(issues: List[Dict[str, Any]], project_path: str) -> List[Dict[str, Any]]:
    """Convert all file paths in issues to be relative to the project path.

    Args:
        issues: List of issue dictionaries
        project_path: Base project path

    Returns:
        List of issues with relative paths
    """
    relative_issues = []
    for issue in issues:
        # Create a copy of the issue
        relative_issue = issue.copy()

        # Convert the file path if present
        if "file" in relative_issue:
            relative_issue["file"] = make_path_relative(relative_issue["file"], project_path)

        relative_issues.append(relative_issue)

    return relative_issues


def convert_summary_paths_to_relative(
    summary: Dict[str, Dict[str, Any]], project_path: str
) -> Dict[str, Dict[str, Any]]:
    """Convert all file paths in a summary dictionary to be relative to the project path.

    Args:
        summary: Dictionary of file paths to summaries
        project_path: Base project path

    Returns:
        Summary dictionary with relative paths
    """
    relative_summary = {}
    for file_path, data in summary.items():
        relative_path = make_path_relative(file_path, project_path)
        relative_summary[relative_path] = data

    return relative_summary
