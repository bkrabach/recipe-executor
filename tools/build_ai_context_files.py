#!/usr/bin/env python3
"""
Build AI Context Files Script

This script imports the collect_files module and calls its functions directly
 to generate Markdown files containing code and recipe files for AI context.

This script should be placed at:
[repo_root]/tools/build_ai_context_files.py

And will be run from the repository root.
"""

import argparse
import os
import sys
from datetime import datetime

OUTPUT_DIR = "ai_context/generated"

# We're running from repo root, so that's our current directory
global repo_root
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build AI Context Files script that collects project files into markdown."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Always overwrite files, even if content unchanged",
    )
    return parser.parse_args()


def ensure_directory_exists(file_path) -> None:
    """Create directory for file if it doesn't exist."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def build_context_files(force=False) -> None:
    # Define the tasks to run
    tasks = [
        # Collect files from recipe_executor
        {
            "patterns": ["recipe_executor"],
            "output": f"{OUTPUT_DIR}/recipe_executor_code_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": ["README.md", "pyproject.toml", ".env.example"],
        },
        # Collect files from recipes/recipe_executor
        {
            "patterns": ["recipes/recipe_executor"],
            "output": f"{OUTPUT_DIR}/recipe_executor_recipe_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/recipe_creator
        {
            "patterns": ["recipes/recipe_creator"],
            "output": f"{OUTPUT_DIR}/recipe_creator_recipe_files.md",
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
        # Collect files from mcp-servers/python-code-tools
        {
            "patterns": ["mcp-servers/python-code-tools"],
            "output": f"{OUTPUT_DIR}/python_code_tools_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/examples_*
        {
            "patterns": ["recipes/example_*"],
            "output": f"{OUTPUT_DIR}/recipe_examples_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/blueprint_generator
        {
            "patterns": ["recipes/blueprint_generator"],
            "output": f"{OUTPUT_DIR}/blueprint_generator_files.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
    ]

    # Execute each task
    for task in tasks:
        patterns = task["patterns"]
        output = task["output"]
        exclude = task["exclude"]
        include = task["include"]

        # Ensure the output directory exists
        ensure_directory_exists(output)

        print(f"Collecting files for patterns: {patterns}")
        print(f"Excluding patterns: {exclude}")
        print(f"Including patterns: {include}")

        # Collect the files
        files = collect_files.collect_files(patterns, exclude, include)
        print(f"Found {len(files)} files.")

        # Build header
        now = datetime.now()
        hour12 = now.hour % 12 or 12
        date_str = f"{now.month}/{now.day}/{now.year}, {hour12}:{now.minute:02d}:{now.second:02d} {'AM' if now.hour < 12 else 'PM'}"
        header = f"# AI Context Files\nDate: {date_str}\nFiles: {len(files)}\n\n"

        # Build content body
        content_body = ""
        for file in files:
            rel_path = os.path.relpath(file)
            content_body += f"=== File: {rel_path} ===\n"
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content_body += f.read()
            except Exception as e:
                content_body += f"[ERROR reading file: {e}]\n"
            content_body += "\n\n"

        new_content = header + content_body

        # Compare with existing file if not forcing
        if os.path.exists(output) and not force:
            try:
                with open(output, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                existing_body = existing_content.split("\n\n", 1)[1] if "\n\n" in existing_content else ""
                new_body = new_content.split("\n\n", 1)[1] if "\n\n" in new_content else ""
                if existing_body == new_body:
                    print(f"No changes for {output}, skipping write.")
                    continue
            except Exception as e:
                print(f"Warning: unable to compare existing file {output}: {e}")

        # Write the file (new or forced update)
        with open(output, "w", encoding="utf-8") as outfile:
            outfile.write(new_content)
        print(f"Written to {output}\n")


def main():
    args = parse_args()

    # Verify we're in the repository root by checking for key directories/files
    required_paths = [
        os.path.join(repo_root, "tools", "collect_files.py"),
        os.path.join(repo_root, "recipes"),
    ]

    missing_paths = [path for path in required_paths if not os.path.exists(path)]
    if missing_paths:
        print("Warning: This script should be run from the repository root.")
        print("The following expected paths were not found:")
        for path in missing_paths:
            print(f"  - {path}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    build_context_files(force=args.force)


if __name__ == "__main__":
    main()
