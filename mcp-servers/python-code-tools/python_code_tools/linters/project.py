"""Project-based Ruff linter implementation with proper glob pattern handling."""

import asyncio
import glob
import json
import os
import subprocess
import sys
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
        self.debug = True  # Enable debug mode

    def log(self, message: str):
        """Log a debug message to stderr."""
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stderr)

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
        self.log(f"Starting lint_project for path: {project_path}")
        self.log(f"File patterns: {file_patterns}")
        self.log(f"Fix enabled: {fix}")

        # Ensure we have a config dictionary
        config = config or {}
        # Force ALL rule selection to match diagnostic if not already specified
        if "select" not in config:
            config["select"] = "ALL"
        self.log(f"Config: {config}")

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
        self.log(f"Has Ruff config: {has_ruff_config}")

        # Expand file patterns to get a list of Python files
        py_files = await self._expand_file_patterns(path, file_patterns)
        self.log(f"Found {len(py_files)} Python files matching patterns")

        # If no Python files found, return empty result
        if not py_files:
            self.log("No Python files found, returning empty result")
            return ProjectLintResult(
                issues=[],
                fixed_count=0,
                remaining_count=0,
                modified_files=[],
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                files_summary={},
            )

        # Direct Ruff run to see what issues are found
        # Build command with explicit file paths instead of patterns
        cmd = ["ruff", "check", "--output-format=json"]

        # Add select rules option
        if "select" in config:
            cmd.extend(["--select", config["select"]])

        # Add each file path individually
        cmd.extend(py_files)

        self.log(f"Running Ruff check command: {' '.join(cmd[:10])}... [total: {len(cmd)} args]")

        try:
            # Run the check command directly
            check_proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await check_proc.communicate()

            if stderr:
                self.log(f"Ruff stderr: {stderr.decode()}")

            check_output = stdout.decode()
            self.log(f"Ruff output length: {len(check_output)}")
            self.log(f"Ruff output sample: {check_output[:200]}")

            # Parse issues from JSON
            issues = []
            if check_output.strip():
                try:
                    json_data = json.loads(check_output)
                    self.log(f"Parsed JSON with {len(json_data)} issues")

                    # Transform JSON output to our issue format with careful null checking
                    for idx, item in enumerate(json_data):
                        try:
                            # Get location data with proper null handling
                            location = item.get("location") or {}
                            row = location.get("row", 0) if isinstance(location, dict) else 0
                            column = location.get("column", 0) if isinstance(location, dict) else 0

                            # Get fix data with proper null handling
                            fix_data = item.get("fix") or {}
                            fix_applicable = (
                                fix_data.get("applicability", "") == "applicable"
                                if isinstance(fix_data, dict)
                                else False
                            )

                            # Create safe issue object
                            issues.append({
                                "file": item.get("filename", ""),
                                "line": row,
                                "column": column,
                                "code": item.get("code", ""),
                                "message": item.get("message", ""),
                                "fix_available": fix_applicable,
                            })
                        except Exception as e:
                            self.log(f"Error processing issue {idx}: {e}")
                            self.log(f"Item data: {item}")
                            # Continue processing other issues
                            continue
                except json.JSONDecodeError as e:
                    self.log(f"JSON decode error: {e}")
                    self.log(f"Raw output: {check_output}")
                    issues = []
            else:
                self.log("No output from Ruff command")

            # Run the fix command if requested
            modified_files = []
            fixed_count = 0

            if fix and issues:
                self.log("Running fix command")
                fix_cmd = ["ruff", "check", "--fix"]

                # Add select rules option
                if "select" in config:
                    fix_cmd.extend(["--select", config["select"]])

                # Add each file path individually
                fix_cmd.extend(py_files)

                self.log(f"Fix command: {' '.join(fix_cmd[:10])}... [total: {len(fix_cmd)} args]")

                # Save list of issues before fixing
                pre_fix_issues = issues.copy()

                # Run the fix command
                fix_proc = await asyncio.create_subprocess_exec(
                    *fix_cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                fix_stdout, fix_stderr = await fix_proc.communicate()

                if fix_stderr:
                    self.log(f"Fix stderr: {fix_stderr.decode()}")

                # Check for modified files
                try:
                    # Use git status to detect modified files if this is a git repo
                    modified_files = await self._get_modified_files_git(path)
                    if not modified_files:
                        # Use stat-based detection as backup
                        modified_files = await self._get_modified_files_stat(path)
                except Exception as e:
                    self.log(f"Error detecting modified files: {e}")

                # Run check again to see what issues remain
                post_fix_proc = await asyncio.create_subprocess_exec(
                    *cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                post_stdout, _ = await post_fix_proc.communicate()
                post_output = post_stdout.decode()

                post_issues = []
                if post_output.strip():
                    try:
                        post_json = json.loads(post_output)
                        self.log(f"Post-fix: found {len(post_json)} remaining issues")

                        # Transform JSON with careful null checking
                        for idx, item in enumerate(post_json):
                            try:
                                # Get location data with proper null handling
                                location = item.get("location") or {}
                                row = location.get("row", 0) if isinstance(location, dict) else 0
                                column = location.get("column", 0) if isinstance(location, dict) else 0

                                # Get fix data with proper null handling
                                fix_data = item.get("fix") or {}
                                fix_applicable = (
                                    fix_data.get("applicability", "") == "applicable"
                                    if isinstance(fix_data, dict)
                                    else False
                                )

                                # Create safe issue object
                                post_issues.append({
                                    "file": item.get("filename", ""),
                                    "line": row,
                                    "column": column,
                                    "code": item.get("code", ""),
                                    "message": item.get("message", ""),
                                    "fix_available": fix_applicable,
                                })
                            except Exception as e:
                                self.log(f"Error processing post-fix issue {idx}: {e}")
                                # Continue processing other issues
                                continue
                    except json.JSONDecodeError:
                        self.log("Error parsing post-fix JSON")
                        post_issues = issues  # Assume nothing was fixed

                # Calculate fixed count
                fixed_count = len(pre_fix_issues) - len(post_issues)
                self.log(f"Fixed {fixed_count} issues")

                # Use post-fix issues as the remaining issues
                issues = post_issues

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

            # Debug final result
            self.log(f"Final result: {len(issues)} issues, {fixed_count} fixed")
            if issues:
                self.log(f"Sample issues: {issues[:3]}")

            return ProjectLintResult(
                issues=issues,
                fixed_count=fixed_count,
                remaining_count=len(issues),
                modified_files=modified_files,
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                files_summary=files_summary,
            )

        except Exception as e:
            import traceback

            self.log(f"Exception in lint_project: {e}")
            self.log(traceback.format_exc())

            # Return empty result on error
            return ProjectLintResult(
                issues=[],
                fixed_count=0,
                remaining_count=0,
                modified_files=[],
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                files_summary={},
            )

    async def _expand_file_patterns(self, path: Path, file_patterns: Optional[List[str]]) -> List[str]:
        """Expand glob patterns to a list of Python files.

        Args:
            path: Project directory path
            file_patterns: Optional list of glob patterns

        Returns:
            List of Python file paths relative to the project root
        """
        py_files = set()  # Use a set to avoid duplicates

        if file_patterns:
            # Process each pattern
            for pattern in file_patterns:
                # Use glob to expand the pattern
                full_pattern = os.path.join(str(path), pattern)
                self.log(f"Expanding pattern: {full_pattern}")

                matches = glob.glob(full_pattern, recursive=True)

                # Filter to only include Python files
                for match in matches:
                    if match.endswith(".py") and os.path.isfile(match):
                        # Convert to relative path
                        rel_path = os.path.relpath(match, str(path))
                        # Skip .venv directory and __pycache__
                        if not rel_path.startswith(".venv") and not rel_path.startswith("__pycache__"):
                            py_files.add(rel_path)

        # If no files found through patterns, find all Python files
        if not py_files:
            for root, _, files in os.walk(str(path)):
                for file in files:
                    if file.endswith(".py"):
                        rel_path = os.path.relpath(os.path.join(root, file), str(path))
                        # Skip .venv directory and __pycache__
                        if not rel_path.startswith(".venv") and not rel_path.startswith("__pycache__"):
                            py_files.add(rel_path)

        # Convert set to sorted list
        result = sorted(list(py_files))

        # Print some sample files
        if result:
            sample = result[:5]
            self.log(f"Sample files: {sample}")
            if len(result) > 5:
                self.log(f"... and {len(result) - 5} more files")

        return result

    async def _get_modified_files_git(self, path: Path) -> List[str]:
        """Get list of modified files using git.

        Args:
            path: Project directory path

        Returns:
            List of modified file paths
        """
        try:
            # Check if this is a git repository
            git_check = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                str(path),
                "rev-parse",
                "--is-inside-work-tree",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await git_check.communicate()

            if git_check.returncode == 0 and stdout.decode().strip() == "true":
                # Get list of modified files
                git_status = await asyncio.create_subprocess_exec(
                    "git", "-C", str(path), "status", "--porcelain", stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, _ = await git_status.communicate()

                # Parse the status output
                modified_files = []
                for line in stdout.decode().strip().split("\n"):
                    if line.strip():
                        # Git status format: XY filename
                        # X is the status in the index, Y is the status in the working tree
                        status = line[:2]
                        file_path = line[3:].strip()
                        # Only include Python files that are modified in the working tree
                        if status[1] in ["M", "A", "R", "C"] and file_path.endswith(".py"):
                            modified_files.append(file_path)

                self.log(f"Git found {len(modified_files)} modified files")
                return modified_files

            return []
        except Exception as e:
            self.log(f"Error using git to find modified files: {e}")
            return []

    async def _get_modified_files_stat(self, path: Path) -> List[str]:
        """Get list of modified files using file stats (last modified time).

        Args:
            path: Project directory path

        Returns:
            List of modified file paths
        """
        # This is a basic implementation that looks for recently modified files
        # A more accurate implementation would store file hashes before and after
        modified_files = []
        now = datetime.now().timestamp()
        one_minute_ago = now - 60  # Look for files modified in the last minute

        # Recursively scan for Python files
        for root, _, files in os.walk(str(path)):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > one_minute_ago:
                            # Get path relative to the project root
                            rel_path = os.path.relpath(file_path, str(path))
                            modified_files.append(rel_path)
                    except Exception as e:
                        self.log(f"Error checking file modification time: {e}")

        self.log(f"Stat check found {len(modified_files)} modified files")
        return modified_files
