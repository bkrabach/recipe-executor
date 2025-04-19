#!/usr/bin/env python3
"""Direct Ruff diagnostic script to check for linting issues in a project."""

import asyncio
import json
import os
import subprocess


async def run_ruff_command(cmd, cwd):
    """Run a Ruff command and return the output."""
    print(f"Running command: {' '.join(cmd)} in {cwd}")
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    stdout_data = stdout.decode("utf-8")
    stderr_data = stderr.decode("utf-8")

    print(f"Return code: {process.returncode}")
    if stderr_data:
        print(f"Stderr: {stderr_data}")

    return stdout_data


async def check_specific_file(project_path, file_path):
    """Check a specific file with Ruff."""
    print(f"\n=== Checking specific file: {file_path} ===")
    cmd = ["ruff", "check", file_path, "--output-format=json"]

    stdout = await run_ruff_command(cmd, project_path)
    if stdout.strip():
        try:
            issues = json.loads(stdout)
            print(f"Found {len(issues)} issues in {file_path}")
            for issue in issues:
                print(f"  - {issue.get('code')}: {issue.get('message')}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw output: {stdout}")
    else:
        print(f"No issues found in {file_path}")


async def check_project_with_all_rules(project_path):
    """Check the entire project with all Ruff rules enabled."""
    print("\n=== Checking entire project with ALL rules ===")
    cmd = ["ruff", "check", ".", "--select=ALL", "--output-format=json"]

    stdout = await run_ruff_command(cmd, project_path)
    if stdout.strip():
        try:
            issues = json.loads(stdout)
            print(f"Found {len(issues)} issues in project")

            # Group issues by file
            issues_by_file = {}
            for issue in issues:
                file = issue.get("filename", "unknown")
                if file not in issues_by_file:
                    issues_by_file[file] = []
                issues_by_file[file].append(issue)

            # Print issues grouped by file
            for file, file_issues in issues_by_file.items():
                print(f"\nFile: {file} - {len(file_issues)} issues")
                for issue in file_issues[:5]:  # Show up to 5 issues per file
                    print(f"  - {issue.get('code')}: {issue.get('message')}")
                if len(file_issues) > 5:
                    print(f"  ... and {len(file_issues) - 5} more issues")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw output: {stdout}")
    else:
        print("No issues found in project")


async def check_ruff_config(project_path):
    """Check what Ruff configuration exists."""
    print("\n=== Checking Ruff configuration ===")
    config_files = [
        "pyproject.toml",
        "ruff.toml",
        ".ruff.toml",
    ]

    for config_file in config_files:
        config_path = os.path.join(project_path, config_file)
        if os.path.exists(config_path):
            print(f"Found config file: {config_file}")
            with open(config_path, "r") as f:
                content = f.read()
                print(f"Content of {config_file}:")
                print("```")
                print(content)
                print("```")

    # Check environment variables
    for var in os.environ:
        if var.startswith("RUFF_"):
            print(f"Found Ruff environment variable: {var}={os.environ[var]}")


async def main():
    """Main function."""
    # Use current directory as the project path
    project_path = os.getcwd()
    print(f"Using project path: {project_path}")

    # Print Ruff version
    try:
        version_process = await asyncio.create_subprocess_exec(
            "ruff",
            "--version",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, _ = await version_process.communicate()
        print(f"Ruff version: {stdout.decode().strip()}")
    except Exception as e:
        print(f"Error getting Ruff version: {e}")

    # Check configuration
    await check_ruff_config(project_path)

    # Check problematic file directly
    problem_file = "python_code_tools/linters/project.py"
    if os.path.exists(os.path.join(project_path, problem_file)):
        await check_specific_file(project_path, problem_file)
    else:
        print(f"Problem file not found: {problem_file}")

    # Check entire project with all rules
    await check_project_with_all_rules(project_path)


if __name__ == "__main__":
    asyncio.run(main())
