"""Project-based Ruff linter implementation."""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from python_code_tools.linters.base import ProjectLinter, ProjectLintResult


class RuffProjectLinter(ProjectLinter):
    """Project linter implementation using Ruff."""

    def __init__(self, **kwargs):
        """Initialize the project linter.

        Args:
            **kwargs: Additional configuration options
        """
        super().__init__(name="ruff-project", **kwargs)

    async def lint_project(
        self,
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> ProjectLintResult:
        """Lint a project directory using Ruff.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include (e.g., ["*.py", "src/**/*.py"])
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for Ruff

        Returns:
            A ProjectLintResult object containing the issues found and fix counts
        """
        # Validate that the path exists and is a directory
        path = Path(project_path)
        if not path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        if not path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        # Check if there's a pyproject.toml or ruff.toml in the project directory
        pyproject_path = path / "pyproject.toml"
        ruff_toml_path = path / "ruff.toml"
        has_ruff_config = pyproject_path.exists() or ruff_toml_path.exists()

        # Build the ruff command
        cmd = ["ruff", "check"]

        # Add file patterns if provided
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")  # Default to checking the entire directory

        # Add fix flag if requested
        if fix:
            cmd.append("--fix")

        # Add output format for easier parsing
        cmd.extend(["--output-format", "json"])

        # Add any config options
        if config:
            for key, value in config.items():
                cmd.extend(["--config", f"{key}={value}"])

        # Print command that will be executed (for debugging)
        print(f"Executing: {' '.join(cmd)} in directory {path}")

        # Get original issue count if fixing
        original_issues_count = 0
        if fix:
            original_issues_count = await self._count_issues(path, file_patterns, config)
            print(f"Original issues count: {original_issues_count}")

        # Run ruff on the project
        issues_proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(path),  # Run from the project directory
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await issues_proc.communicate()

        # Check for errors
        if issues_proc.returncode != 0 and stderr:
            error_output = stderr.decode().strip()
            if error_output:
                print(f"Ruff error: {error_output}")

        issues_output = stdout.decode()

        # Try to parse JSON output first
        try:
            json_data = json.loads(issues_output)
            # Transform JSON output to our issue format
            issues = []
            for item in json_data:
                issues.append(
                    {
                        "file": item.get("filename", ""),
                        "line": item.get("location", {}).get("row", 0),
                        "column": item.get("location", {}).get("column", 0),
                        "code": item.get("code", ""),
                        "message": item.get("message", ""),
                        "fix_available": item.get("fix", {}).get("applicability", "")
                        == "applicable",
                    }
                )
        except Exception as e:
            # Fall back to text parsing if JSON parsing fails
            print(f"JSON parsing failed: {e}, falling back to text parsing")
            issues = self._parse_ruff_output(issues_output)

        # Count remaining issues
        remaining_count = len(issues)

        # Calculate fixed count
        fixed_count = max(0, original_issues_count - remaining_count) if fix else 0

        # Get list of modified files
        modified_files = await self._get_modified_files(path) if fix else []

        # Create a summary of findings by file
        files_summary = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            if file_path not in files_summary:
                files_summary[file_path] = {"total_issues": 0, "issue_types": {}}

            files_summary[file_path]["total_issues"] += 1

            code = issue.get("code", "unknown")
            if code not in files_summary[file_path]["issue_types"]:
                files_summary[file_path]["issue_types"][code] = 0
            files_summary[file_path]["issue_types"][code] += 1

        return ProjectLintResult(
            issues=issues,
            fixed_count=fixed_count,
            remaining_count=remaining_count,
            modified_files=modified_files,
            project_path=str(path),
            has_ruff_config=has_ruff_config,
            files_summary=files_summary,
        )

    def _parse_ruff_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ruff output into structured issue data.

        Args:
            output: The stdout from running ruff

        Returns:
            A list of dictionaries containing structured issue data
        """
        issues = []

        for line in output.strip().split("\n"):
            if not line:
                continue

            try:
                # Parse standard ruff output format
                # example: file.py:10:5: E501 Line too long (88 > 79 characters)
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path, line_num, col_num, message = parts

                    # Extract the error code and description
                    message_parts = message.strip().split(" ", 1)
                    if len(message_parts) == 2:
                        code, description = message_parts

                        issues.append(
                            {
                                "file": file_path,
                                "line": int(line_num),
                                "column": int(col_num),
                                "code": code,
                                "message": description,
                            }
                        )
            except Exception:
                # Skip lines that don't match the expected format
                continue

        return issues

    async def _count_issues(
        self,
        path: Path,
        file_patterns: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count the number of issues in the project.

        Args:
            path: The project directory path
            file_patterns: Optional list of file patterns to include
            config: Optional configuration settings for Ruff

        Returns:
            The number of issues found in the project
        """
        # Build the command to count issues
        cmd = ["ruff", "check"]

        # Add file patterns if provided
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")  # Default to checking the entire directory

        # Add any config options
        if config:
            for key, value in config.items():
                cmd.extend(["--config", f"{key}={value}"])

        try:
            # Run ruff without fixing to get original issue count
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(path),  # Run from the project directory
                stdout=subprocess.PIPE,
            )

            stdout, _ = await result.communicate()
            output = stdout.decode()

            # Count non-empty lines in the output
            issues = [line for line in output.strip().split("\n") if line]
            return len(issues)

        except Exception:
            return 0

    async def _get_modified_files(self, path: Path) -> List[str]:
        """Get a list of files that were modified by Ruff's auto-fix.

        Uses git status to detect modified files, or falls back to a timestamp-based
        approach if git is not available.

        Args:
            path: The project directory path

        Returns:
            A list of modified file paths (relative to the project root)
        """
        # Try using git if available (most accurate for git projects)
        try:
            # Check if this is a git repository
            is_git_repo = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                str(path),
                "rev-parse",
                "--is-inside-work-tree",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await is_git_repo.communicate()

            if is_git_repo.returncode == 0 and stdout.decode().strip() == "true":
                # Get list of modified files
                git_status = await asyncio.create_subprocess_exec(
                    "git",
                    "-C",
                    str(path),
                    "diff",
                    "--name-only",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, _ = await git_status.communicate()

                # Filter for Python files
                modified_files = [
                    line
                    for line in stdout.decode().strip().split("\n")
                    if line.endswith(".py") and line
                ]
                return modified_files
        except Exception:
            # Git not available or error occurred, fall back to another method
            pass

        # Fallback: List Python files modified in the last minute
        # This is less accurate but works when git is not available
        modified_files = []
        current_time = datetime.now().timestamp()
        one_minute_ago = current_time - 60  # 1 minute window

        # Use os.walk to iterate through the directory tree
        for root, _, files in os.walk(str(path)):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > one_minute_ago:
                            # Convert to relative path
                            rel_path = os.path.relpath(file_path, str(path))
                            modified_files.append(rel_path)
                    except Exception:
                        continue

        return modified_files
