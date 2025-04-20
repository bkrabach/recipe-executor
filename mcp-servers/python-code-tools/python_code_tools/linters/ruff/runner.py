import asyncio
import glob
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


async def get_python_files(path: Path, patterns: Optional[List[str]] = None) -> List[str]:
    """Get a list of Python files to lint.

    Args:
        path: Project directory path
        file_patterns: Optional list of file patterns to include

    Returns:
        List of Python file paths
    """
    print(f"Looking for Python files in {path}")
    py_files = []

    if not patterns:
        patterns = ["**/*.py"]  # Default to all Python files
        print(f"No patterns provided, using default: {patterns}")
    else:
        print(f"Using provided patterns: {patterns}")

    # Use Python's glob to find files matching patterns
    for pattern in patterns:
        # Handle both absolute and relative paths in patterns
        if os.path.isabs(pattern):
            glob_pattern = pattern
        else:
            glob_pattern = os.path.join(str(path), pattern)

        print(f"Searching with glob pattern: {glob_pattern}")

        # Use glob.glob with recursive=True for ** patterns
        if "**" in pattern:
            matched_files = glob.glob(glob_pattern, recursive=True)
        else:
            matched_files = glob.glob(glob_pattern)

        # Convert to relative paths
        for file in matched_files:
            if file.endswith(".py"):
                try:
                    rel_path = os.path.relpath(file, str(path))
                    # Skip .venv directory and __pycache__
                    if not rel_path.startswith((".venv", "__pycache__")):
                        py_files.append(rel_path)
                except ValueError:
                    # This can happen if the file is on a different drive (Windows)
                    print(f"Skipping file not relative to project path: {file}")

    # Remove duplicates while preserving order
    unique_files = []
    seen = set()
    for file in py_files:
        if file not in seen:
            unique_files.append(file)
            seen.add(file)

    print(f"Found {len(unique_files)} Python files to lint")
    if len(unique_files) < 10:  # Only print all files if there are few
        print(f"Files to lint: {unique_files}")
    else:
        print(f"First 5 files: {unique_files[:5]}")

    return unique_files


async def run_ruff_check(path: Path, py_files: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run Ruff in check mode (no fixing).

    Args:
        path: Project directory path
        py_files: List of Python files to check
        config: Configuration to use

    Returns:
        List of issues found
    """
    # Make sure we have files to check
    if not py_files:
        print("No Python files found to check")
        return []

    # Verify the files exist
    existing_files = []
    for file_path in py_files:
        full_path = path / file_path
        if full_path.exists():
            existing_files.append(file_path)

    if not existing_files:
        print(f"None of the specified Python files exist in {path}")
        return []

    py_files = existing_files
    print(f"Found {len(py_files)} Python files to check")

    # Build the command
    cmd = ["ruff", "check", "--output-format=json"]

    # Add configuration options
    if "select" in config:
        select_value = config["select"]
        if isinstance(select_value, list):
            select_str = ",".join(select_value)
        else:
            select_str = str(select_value)
        cmd.extend(["--select", select_str])

    if "ignore" in config and config["ignore"]:
        if isinstance(config["ignore"], list):
            ignore_str = ",".join(config["ignore"])
        else:
            ignore_str = str(config["ignore"])
        cmd.extend(["--ignore", ignore_str])

    if "line-length" in config:
        cmd.extend(["--line-length", str(config["line-length"])])

    # Add files to check
    cmd.extend(py_files)

    try:
        # Now run the actual check command
        print(f"Running ruff command: {' '.join(cmd)}")
        proc = await asyncio.create_subprocess_exec(*cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_bytes, stderr_bytes = await proc.communicate()

        stdout_text = stdout_bytes.decode().strip() if stdout_bytes else ""
        stderr_text = stderr_bytes.decode().strip() if stderr_bytes else ""

        if proc.returncode != 0 and stderr_text:
            print(f"Ruff command failed with exit code {proc.returncode}: {stderr_text}")
            # Continue processing anyway - non-zero could just mean issues were found

        issues = []

        # Only try to parse JSON if we actually have output
        if stdout_text:
            try:
                json_data = json.loads(stdout_text)
                print(f"Ruff found {len(json_data)} issues")

                for item in json_data:
                    try:
                        # Get location data with proper null handling
                        location = item.get("location") or {}
                        row = location.get("row", 0) if isinstance(location, dict) else 0
                        column = location.get("column", 0) if isinstance(location, dict) else 0

                        # Get fix data with proper null handling
                        fix_data = item.get("fix") or {}
                        fix_applicable = (
                            fix_data.get("applicability", "") == "applicable" if isinstance(fix_data, dict) else False
                        )

                        # Create issue object
                        issues.append({
                            "file": item.get("filename", ""),
                            "line": row,
                            "column": column,
                            "code": item.get("code", ""),
                            "message": item.get("message", ""),
                            "fix_available": fix_applicable,
                        })
                    except Exception as e:
                        print(f"Error processing ruff issue: {e}")
                        # Skip issues we can't parse properly
                        continue
            except json.JSONDecodeError as e:
                print(f"Failed to parse Ruff JSON output: {e}")
                print(f"Raw output: {stdout_text[:200]}...")  # Print first 200 chars
                return []

        return issues

    except Exception as e:
        print(f"Error running Ruff check: {e}")
        return []


async def run_ruff_fix(path: Path, py_files: List[str], config: Dict[str, Any]) -> bool:
    """Run Ruff in fix mode.

    Args:
        path: Project directory path
        py_files: List of Python files to fix
        config: Configuration to use

    Returns:
        True if fixing succeeded, False otherwise
    """
    # Make sure we have files to check
    if not py_files:
        return False

    # Verify the files exist
    existing_files = []
    for file_path in py_files:
        full_path = path / file_path
        if full_path.exists():
            existing_files.append(file_path)

    if not existing_files:
        return False

    py_files = existing_files

    # Build the command
    cmd = ["ruff", "check", "--fix"]

    # Add configuration options
    if "select" in config:
        select_value = config["select"]
        if isinstance(select_value, list):
            select_str = ",".join(select_value)
        else:
            select_str = str(select_value)
        cmd.extend(["--select", select_str])

    if "ignore" in config and config["ignore"]:
        if isinstance(config["ignore"], list):
            ignore_str = ",".join(config["ignore"])
        else:
            ignore_str = str(config["ignore"])
        cmd.extend(["--ignore", ignore_str])

    if "line-length" in config:
        cmd.extend(["--line-length", str(config["line-length"])])

    # Add files to fix
    cmd.extend(py_files)

    try:
        proc = await asyncio.create_subprocess_exec(*cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await proc.communicate()

        return proc.returncode == 0

    except Exception:
        return False
