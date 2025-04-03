#!/usr/bin/env python3
"""
Execute Prompt File Utility

Takes a prompt file and a set of files to include as context,
then runs the recipe_executor with all files combined.

Usage examples:
  # Execute with a prompt file and all files in recipes/mine:
  python execute_prompt_file.py --prompt-file path/to/prompt.file --files recipes/mine

  # Execute with a comma-separated list of files:
  python execute_prompt_file.py --prompt-file path/to/prompt.file --files file1.md,file2.md,file3.md

  # Execute with a mix of files and directories:
  python execute_prompt_file.py --prompt-file path/to/prompt.file --files doc1.md,directory1,*.json

  # Execute with exclusions and inclusions:
  python execute_prompt_file.py --prompt-file path/to/prompt.file --files recipes/mine --exclude "**/test/*.json" --include "specific_one.json"

  # Dry run to see the command without executing it:
  python execute_prompt_file.py --prompt-file path/to/prompt.file --files recipes/mine --dry-run
"""

import argparse
import fnmatch
import glob
import os
import pathlib
import subprocess
import sys
from typing import List, Set, Optional


# Default exclude patterns: common directories and binary files to ignore.
DEFAULT_EXCLUDE = [".venv", "node_modules", ".git", "__pycache__", "*.pyc"]


def parse_patterns(pattern_str: str) -> List[str]:
    """Splits a comma-separated string into a list of stripped patterns."""
    return [p.strip() for p in pattern_str.split(",") if p.strip()]


def resolve_pattern(pattern: str) -> str:
    """
    Resolves a pattern that might contain relative path navigation.
    Returns the absolute path of the pattern.
    """
    # Convert the pattern to a Path object
    pattern_path = pathlib.Path(pattern)

    # Check if the pattern is absolute or contains relative navigation
    if os.path.isabs(pattern) or ".." in pattern:
        # Resolve to absolute path
        return str(pattern_path.resolve())

    # For simple patterns without navigation, return as is
    return pattern


def match_pattern(path: str, pattern: str, component_matching=False) -> bool:
    """
    Centralized pattern matching logic.

    Args:
        path: File path to match against
        pattern: Pattern to match
        component_matching: If True, matches individual path components
                           (used primarily for exclude patterns)

    Returns:
        True if path matches the pattern
    """
    # For simple exclude-style component matching
    if component_matching:
        parts = os.path.normpath(path).split(os.sep)
        for part in parts:
            if fnmatch.fnmatch(part, pattern):
                return True
        return False

    # Convert paths to absolute for consistent comparison
    abs_path = os.path.abspath(path)

    # Handle relative path navigation in the pattern
    if ".." in pattern or "/" in pattern or "\\" in pattern:
        # If pattern contains path navigation, resolve it to an absolute path
        resolved_pattern = resolve_pattern(pattern)

        # Check if this is a directory pattern with a wildcard
        if "*" in resolved_pattern:
            # Get the directory part of the pattern
            pattern_dir = os.path.dirname(resolved_pattern)
            # Get the filename pattern
            pattern_file = os.path.basename(resolved_pattern)

            # Check if the file is in or under the pattern directory
            file_dir = os.path.dirname(abs_path)
            if file_dir.startswith(pattern_dir):
                # Match the filename against the pattern
                return fnmatch.fnmatch(os.path.basename(abs_path), pattern_file)
            return False  # Not under the pattern directory
        else:
            # Direct file match
            return abs_path == resolved_pattern or fnmatch.fnmatch(abs_path, resolved_pattern)
    else:
        # Regular pattern without navigation, use relative path matching
        return fnmatch.fnmatch(path, pattern)


def should_exclude(path: str, exclude_patterns: List[str]) -> bool:
    """
    Returns True if any component of the path matches an exclude pattern.
    """
    for pattern in exclude_patterns:
        if match_pattern(path, pattern, component_matching=True):
            return True
    return False


def should_include(path: str, include_patterns: List[str]) -> bool:
    """
    Returns True if the path matches any of the include patterns.
    Handles relative path navigation in include patterns.
    """
    for pattern in include_patterns:
        if match_pattern(path, pattern):
            return True
    return False


def collect_files(patterns: List[str], exclude_patterns: List[str], include_patterns: List[str]) -> List[str]:
    """
    Collects file paths matching the given patterns, applying exclusion first.
    Files that match an include pattern are added back in.

    Returns a sorted list of absolute file paths.
    """
    collected = set()

    # Process included files with simple filenames or relative paths
    for pattern in include_patterns:
        # Check for files in the current directory first
        direct_matches = glob.glob(pattern, recursive=True)
        for match in direct_matches:
            if os.path.isfile(match):
                collected.add(os.path.abspath(match))

        # Then check for relative paths
        if ".." in pattern or os.path.isabs(pattern):
            resolved_pattern = resolve_pattern(pattern)

            # Direct file inclusion
            if "*" not in resolved_pattern and os.path.isfile(resolved_pattern):
                collected.add(resolved_pattern)
            else:
                # Pattern with wildcards
                directory = os.path.dirname(resolved_pattern)
                if os.path.exists(directory):
                    filename_pattern = os.path.basename(resolved_pattern)
                    for root, _, files in os.walk(directory):
                        for file in files:
                            if fnmatch.fnmatch(file, filename_pattern):
                                full_path = os.path.join(root, file)
                                collected.add(os.path.abspath(full_path))

    # Process the main patterns
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for path in matches:
            if os.path.isfile(path):
                process_file(path, collected, exclude_patterns, include_patterns)
            elif os.path.isdir(path):
                process_directory(path, collected, exclude_patterns, include_patterns)

    return sorted(collected)


def process_file(file_path: str, collected: Set[str], exclude_patterns: List[str], include_patterns: List[str]) -> None:
    """Process a single file"""
    abs_path = os.path.abspath(file_path)
    rel_path = os.path.relpath(file_path)

    # Skip if excluded and not specifically included
    if should_exclude(rel_path, exclude_patterns) and not should_include(rel_path, include_patterns):
        return

    collected.add(abs_path)


def process_directory(
    dir_path: str, collected: Set[str], exclude_patterns: List[str], include_patterns: List[str]
) -> None:
    """Process a directory recursively"""
    for root, dirs, files in os.walk(dir_path):
        # Filter directories based on exclude patterns, but respect include patterns
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)
                  or should_include(os.path.join(root, d), include_patterns)]

        # Process each file in the directory
        for file in files:
            full_path = os.path.join(root, file)
            process_file(full_path, collected, exclude_patterns, include_patterns)


def execute_recipe(prompt_file: str, files: List[str], dry_run: bool) -> Optional[int]:
    """
    Executes the recipe_executor with the prompt file and collected files.

    Args:
        prompt_file: Path to the prompt file
        files: List of files to include in the context
        dry_run: If True, only print the command without executing

    Returns:
        Return code from the subprocess or None if dry_run is True
    """
    # Add the prompt file as the first file in the list
    all_files = [prompt_file] + files

    # Create a comma-separated list of relative file paths
    rel_paths = [os.path.relpath(path) for path in all_files]
    file_list = ",".join(rel_paths)

    # Build the command with fixed recipe path
    recipe_path = "recipes/utilities/generate_from_files.json"
    cmd = ["python", "recipe_executor/main.py", recipe_path, "--context", f"files={file_list}"]

    # Print the command
    print("Command to execute:")
    print(" ".join(cmd))

    # Execute the command if not a dry run
    if not dry_run:
        print("\nExecuting command...")
        return subprocess.call(cmd)

    return None


def main() -> None:
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Execute recipe_executor with a prompt file and collected files as context."
    )
    parser.add_argument(
        "--prompt-file", required=True, help="Path to the prompt file to use as the primary input"
    )
    parser.add_argument(
        "--files", required=True, help="File paths or patterns to collect (can be comma-separated)"
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-separated patterns to exclude (will be combined with default excludes: "
        + ",".join(DEFAULT_EXCLUDE)
        + ")",
    )
    parser.add_argument(
        "--include", type=str, default="", help="Comma-separated patterns to include (overrides excludes if matched)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print the command without executing it"
    )
    args = parser.parse_args()

    # Validate prompt file
    if not os.path.isfile(args.prompt_file):
        print(f"Error: Prompt file '{args.prompt_file}' does not exist or is not a file.")
        sys.exit(1)

    # Parse pattern arguments and combine with default excludes
    user_exclude_patterns = parse_patterns(args.exclude)
    exclude_patterns = DEFAULT_EXCLUDE + user_exclude_patterns
    include_patterns = parse_patterns(args.include) if args.include else []

    # Handle comma-separated files patterns (with or without spaces)
    files_patterns = [pattern.strip() for pattern in args.files.split(',')]

    # Collect files from each pattern
    all_files = []
    for pattern in files_patterns:
        if not pattern:  # Skip empty patterns
            continue

        # Check if the pattern is a direct file path
        if os.path.isfile(pattern):
            all_files.append(os.path.abspath(pattern))
        # Or a directory path
        elif os.path.isdir(pattern):
            dir_files = collect_files([pattern], exclude_patterns, include_patterns)
            all_files.extend(dir_files)
        # Or a glob pattern
        else:
            glob_matches = glob.glob(pattern)
            if not glob_matches:
                print(f"Warning: Pattern '{pattern}' did not match any files or directories.")
            else:
                pattern_files = collect_files([pattern], exclude_patterns, include_patterns)
                all_files.extend(pattern_files)

    # Remove duplicates and sort
    files = sorted(list(set(all_files)))
    print(f"Found {len(files)} files matching pattern(s).")

    # Execute the recipe
    return_code = execute_recipe(args.prompt_file, files, args.dry_run)

    if args.dry_run:
        print("\nDry run completed. No command was executed.")
    else:
        print(f"\nCommand execution completed with return code: {return_code}")
        sys.exit(return_code if return_code is not None else 0)


if __name__ == "__main__":
    main()
