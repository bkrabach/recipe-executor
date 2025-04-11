#!/usr/bin/env python3
"""
Build AI Context Files Script

This script imports the collect_files module and calls its functions directly
to generate Markdown files containing code and recipe files for AI context.

This script should be placed at:
[repo_root]/tools/build_ai_context_files.py

And will be run from the repository root.
"""

import os
import sys

OUTPUT_DIR = "ai_context/generated"

# We're running from repo root, so that's our current directory
repo_root = os.getcwd()

# Add the tools directory to the Python path
tools_dir = os.path.join(repo_root, "tools")
sys.path.append(tools_dir)

# Import the collect_files module
try:
    import collect_files  # type: ignore
except ImportError:
    print(f"Error: Could not import collect_files module from {tools_dir}")
    print("Make sure this script is run from the repository root.")
    sys.exit(1)


def ensure_directory_exists(file_path) -> None:
    """Create directory for file if it doesn't exist."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def build_context_files() -> None:
    # Define the tasks to run
    tasks = [
        # Collect files from recipe_executor
        {
            "patterns": ["recipe_executor"],
            "output": f"{OUTPUT_DIR}/recipe_executor_code_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": ["README.md", "pyproject.toml", ".env.example"],
        },
        # Collect files from recipes/recipe_executor with exclusion
        {
            "patterns": ["recipes/recipe_executor"],
            "output": f"{OUTPUT_DIR}/recipe_executor_recipe_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/utilities
        {
            "patterns": ["recipes/utilities"],
            "output": f"{OUTPUT_DIR}/utilities_recipe_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
    ]

    # Execute each task
    for task in tasks:
        # Ensure the output directory exists
        ensure_directory_exists(task["output"])

        print(f"Collecting files for patterns: {task['patterns']}")
        print(f"Excluding patterns: {task['exclude']}")
        print(f"Including patterns: {task['include']}")

        # Collect the files
        files = collect_files.collect_files(task["patterns"], task["exclude"], task["include"])

        print(f"Found {len(files)} files. Writing to {task['output']}")

        # Write the results to the output file
        with open(task["output"], "w") as outfile:
            for file in files:
                rel_path = os.path.relpath(file)
                outfile.write(f"=== File: {rel_path} ===\n")
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()
                    outfile.write(content)
                except Exception as e:
                    outfile.write(f"[ERROR reading file: {e}]\n")
                outfile.write("\n\n")  # Extra newlines between files

        print(f"Completed writing to {task['output']}\n")


if __name__ == "__main__":
    # Verify we're in the repository root by checking for key directories/files
    required_paths = [os.path.join(repo_root, "tools", "collect_files.py"), os.path.join(repo_root, "recipes")]

    missing_paths = [path for path in required_paths if not os.path.exists(path)]
    if missing_paths:
        print("Warning: This script should be run from the repository root.")
        print("The following expected paths were not found:")
        for path in missing_paths:
            print(f"  - {path}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    build_context_files()
