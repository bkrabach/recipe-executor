"""Project-based Ruff linter implementation."""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import tomli
except ImportError:
    tomli = None

from python_code_tools.linters.base import ProjectLinter, ProjectLintResult


class RuffProjectLinter(ProjectLinter):
    """Project linter implementation using Ruff."""

    def __init__(self, **kwargs):
        """Initialize the project linter.

        Args:
            **kwargs: Additional configuration options
        """
        super().__init__(name="ruff-project", **kwargs)

        # Default configuration settings
        self.default_config = {
            "select": "E,F,W,I",  # Default rule selection
            "ignore": [],  # No ignored rules by default
            "line-length": 100,  # Default line length
        }

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

        # Read project configuration and determine config source
        project_config, config_source_str = await self._read_project_config(path)
        has_ruff_config = bool(project_config)

        # Merge configurations (priority: user config > project config > default config)
        effective_config, config_summary, active_config_source = self._merge_configs(
            user_config=config or {},
            project_config=project_config,
        )

        # Use the active source returned from _merge_configs
        config_source_str = active_config_source

        # Get a list of Python files to lint
        py_files = await self._get_python_files(path, file_patterns)

        # If no Python files found, return empty result
        if not py_files:
            print("No Python files found to lint")
            return ProjectLintResult(
                issues=[],
                fixed_count=0,
                remaining_count=0,
                modified_files=[],
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                config_source=config_source_str,
                config_summary=config_summary,
                files_summary={},
                fixed_issues=[],
                fixed_issues_summary={},
            )

        try:
            # First, check for issues without fixing them
            initial_issues = await self._run_ruff_check(path, py_files, effective_config)

            # Get file hashes before fixing to detect changes
            file_hashes_before = await self._get_file_hashes(path, py_files)

            modified_files = []
            fixed_issues = []

            # Run the fix command if requested and if there are issues
            if fix and initial_issues:
                fix_success = await self._run_ruff_fix(path, py_files, effective_config)

                # Get file hashes after fixing to detect changes
                file_hashes_after = await self._get_file_hashes(path, py_files)

                # Determine which files were actually modified
                modified_files = self._get_modified_files(file_hashes_before, file_hashes_after)

                # Check for remaining issues after fixing
                remaining_issues = await self._run_ruff_check(path, py_files, effective_config)

                # Identify which issues were fixed by comparing initial and remaining issues
                fixed_issues = self._identify_fixed_issues(initial_issues, remaining_issues)

            else:
                # If we didn't run the fix, then remaining issues are the same as initial
                remaining_issues = initial_issues.copy()

            # Calculate counts
            initial_count = len(initial_issues)
            fixed_count = len(fixed_issues)
            remaining_count = len(remaining_issues)

            # Sanity check - if something went wrong and our counts are inconsistent,
            # recalculate to make them valid
            if initial_count != (fixed_count + remaining_count):
                # The most reliable is the count of the remaining issues
                fixed_count = initial_count - remaining_count

            # Create fixed issues summary
            fixed_issues_summary = self._create_issues_summary(fixed_issues, "fixed_types", "total_fixed")

            # Create remaining issues summary
            files_summary = self._create_issues_summary(remaining_issues, "issue_types", "total_issues")

            # Generate the final report just before returning
            self._print_final_report(
                total_issue_count=initial_count,
                fixed_count=fixed_count,
                remaining_count=remaining_count,
                modified_files=modified_files,
                fixed_issues=fixed_issues,
                remaining_issues=remaining_issues,
                files_summary=files_summary,
                fixed_issues_summary=fixed_issues_summary,
            )

            return ProjectLintResult(
                issues=remaining_issues,
                fixed_count=fixed_count,
                remaining_count=remaining_count,
                modified_files=modified_files,
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                config_source=config_source_str,
                config_summary=config_summary,
                files_summary=files_summary,
                fixed_issues=fixed_issues,
                fixed_issues_summary=fixed_issues_summary,
            )

        except Exception as e:
            print(f"Error during project linting: {e}")
            import traceback

            traceback.print_exc()
            return ProjectLintResult(
                issues=[],
                fixed_count=0,
                remaining_count=0,
                modified_files=[],
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                config_source=config_source_str,
                config_summary=config_summary,
                files_summary={},
                fixed_issues=[],
                fixed_issues_summary={},
            )

    def _print_final_report(
        self,
        total_issue_count: int,
        fixed_count: int,
        remaining_count: int,
        modified_files: List[str],
        fixed_issues: List[Dict[str, Any]],
        remaining_issues: List[Dict[str, Any]],
        files_summary: Dict[str, Dict[str, Any]],
        fixed_issues_summary: Dict[str, Dict[str, Any]],
    ) -> None:
        """Print a comprehensive final report.

        Args:
            total_issue_count: Total number of issues found
            fixed_count: Number of issues fixed
            remaining_count: Number of issues remaining
            modified_files: List of files that were modified
            fixed_issues: List of issues that were fixed
            remaining_issues: List of issues remaining
            files_summary: Summary of remaining issues by file
            fixed_issues_summary: Summary of fixed issues by file
        """
        # Report on issues found, fixed, and remaining
        print(f"\nTotal issues found: {total_issue_count}")
        print(f"Fixed issues: {fixed_count}")
        print(f"Remaining issues: {remaining_count}")

        # Report on fixed issues
        if fixed_count > 0:
            print("\nFixed issues:")
            for issue in fixed_issues:
                file_path = issue.get("file", "unknown")
                code = issue.get("code", "unknown")
                message = issue.get("message", "unknown")
                line = issue.get("line", 0)
                column = issue.get("column", 0)
                print(f"- {file_path} (Line {line}, Col {column}): {code} - {message}")

            # Print summary by file
            if fixed_issues_summary:
                print("\nFixed issues by file:")
                for file_path, summary in fixed_issues_summary.items():
                    print(f"- {file_path}: {summary.get('total_fixed', 0)} issues")
                    if "fixed_types" in summary:
                        for code, count in summary["fixed_types"].items():
                            print(f"    {code}: {count}")

        # Report on remaining issues
        if remaining_count > 0:
            print("\nRemaining issues:")
            for issue in remaining_issues:
                file_path = issue.get("file", "unknown")
                code = issue.get("code", "unknown")
                message = issue.get("message", "unknown")
                line = issue.get("line", 0)
                column = issue.get("column", 0)
                print(f"- {file_path} (Line {line}, Col {column}): {code} - {message}")

            # Print summary by file
            if files_summary:
                print("\nRemaining issues by file:")
                for file_path, summary in files_summary.items():
                    print(f"- {file_path}: {summary.get('total_issues', 0)} issues")
                    if "issue_types" in summary:
                        for code, count in summary["issue_types"].items():
                            print(f"    {code}: {count}")

        # Report on modified files
        if modified_files:
            print("\nModified files:")
            for file in modified_files:
                print(f"- {file}")
        else:
            print("\nNo files were modified.")
            if fixed_count > 0:
                print("Note: Some issues were fixed in memory but changes were not written to disk.")
                print(
                    "This can happen with certain types of issues that the linter can detect but not automatically fix."
                )

    def _create_issues_summary(
        self, issues: List[Dict[str, Any]], types_key: str, total_key: str
    ) -> Dict[str, Dict[str, Any]]:
        """Create a summary of issues by file.

        Args:
            issues: List of issues to summarize
            types_key: Key to use for the types dictionary
            total_key: Key to use for the total count

        Returns:
            Dictionary mapping file paths to issue summaries
        """
        summary = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            if file_path not in summary:
                summary[file_path] = {total_key: 0, types_key: {}}

            summary[file_path][total_key] += 1

            code = issue.get("code", "unknown")
            if code not in summary[file_path][types_key]:
                summary[file_path][types_key][code] = 0
            summary[file_path][types_key][code] += 1

        return summary

    def _identify_fixed_issues(
        self, initial_issues: List[Dict[str, Any]], remaining_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify which issues were fixed by comparing initial and remaining issues.

        Args:
            initial_issues: List of issues found before fixing
            remaining_issues: List of issues found after fixing

        Returns:
            List of issues that were fixed
        """
        # Create a map of remaining issues for quick lookup
        remaining_map = {}
        for issue in remaining_issues:
            # Create a unique key for each issue
            key = f"{issue.get('file', '')}:{issue.get('line', '')}:{issue.get('column', '')}:{issue.get('code', '')}"
            remaining_map[key] = True

        # Filter out issues that don't exist in the remaining issues
        fixed_issues = []
        for issue in initial_issues:
            key = f"{issue.get('file', '')}:{issue.get('line', '')}:{issue.get('column', '')}:{issue.get('code', '')}"
            if key not in remaining_map:
                fixed_issues.append(issue)

        return fixed_issues

    async def _read_project_config(self, path: Path) -> Tuple[Dict[str, Any], str]:
        """Read Ruff configuration from the project directory.

        Args:
            path: Project directory path

        Returns:
            Tuple of (configuration settings, source description)
        """
        config = {}
        source = "none"

        if not tomli:
            return config, source

        # Check for .ruff.toml (highest priority)
        ruff_toml_path = path / ".ruff.toml"
        if ruff_toml_path.exists():
            try:
                with open(ruff_toml_path, "rb") as f:
                    ruff_config = tomli.load(f)
                    if "lint" in ruff_config:
                        config.update(ruff_config["lint"])
                    else:
                        config.update(ruff_config)
                    source = ".ruff.toml"
                    # Return immediately since this is highest priority
                    return config, source
            except Exception as e:
                print(f"Error reading .ruff.toml: {e}")

        # Check for pyproject.toml (lower priority)
        pyproject_path = path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, "rb") as f:
                    pyproject_data = tomli.load(f)
                    # Extract Ruff configuration
                    if "tool" in pyproject_data and "ruff" in pyproject_data["tool"]:
                        ruff_config = pyproject_data["tool"]["ruff"]
                        if "lint" in ruff_config:
                            config.update(ruff_config["lint"])
                        else:
                            config.update(ruff_config)
                        source = "pyproject.toml"
            except Exception as e:
                print(f"Error reading pyproject.toml: {e}")

        return config, source

    def _merge_configs(
        self, user_config: Dict[str, Any], project_config: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]], str]:
        """Select configuration source based on priority.

        Args:
            user_config: Configuration provided by the user
            project_config: Configuration from the project's config files

        Returns:
            Tuple of (effective configuration, configuration summary, config source)
        """
        # Start with an empty configuration
        effective_config = {}
        config_source = "default"

        # Select ONLY the highest priority config that's available
        if user_config:
            # User config has highest priority - use ONLY this
            effective_config = user_config.copy()
            config_source = "user"
        elif project_config:
            # Project config has second priority - use ONLY this
            effective_config = project_config.copy()
            config_source = "project"
        else:
            # Default config has lowest priority - use ONLY this
            effective_config = self.default_config.copy()
            config_source = "default"

        # Only include the active configuration in the summary
        config_summary = {config_source: effective_config.copy()}

        return effective_config, config_summary, config_source

    async def _get_python_files(self, path: Path, file_patterns: Optional[List[str]] = None) -> List[str]:
        """Get a list of Python files to lint.

        Args:
            path: Project directory path
            file_patterns: Optional list of file patterns to include

        Returns:
            List of Python file paths
        """
        py_files = []

        if file_patterns:
            # Use ruff's list command to find matching files
            cmd = ["ruff", "check", "--format", "json"]
            cmd.extend(file_patterns)
            cmd.extend(["--no-fix", "--no-cache", "--quiet"])

            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout_bytes, _ = await proc.communicate()

                stdout_text = stdout_bytes.decode().strip() if stdout_bytes else ""

                if proc.returncode != 0:
                    # Fallback to directory scanning
                    py_files = self._find_python_files_in_dir(path)
                    return py_files

                try:
                    # Parse JSON output to get files
                    if stdout_text:
                        data = json.loads(stdout_text)
                        for item in data:
                            file_path = item.get("filename")
                            if file_path and file_path not in py_files:
                                py_files.append(file_path)
                    else:
                        py_files = self._find_python_files_in_dir(path)
                except json.JSONDecodeError:
                    # Fallback to directory scanning if JSON parsing fails
                    py_files = self._find_python_files_in_dir(path)
            except Exception:
                # Fallback to directory scanning
                py_files = self._find_python_files_in_dir(path)
        else:
            # No patterns provided, scan directory for Python files
            py_files = self._find_python_files_in_dir(path)

        return py_files

    def _find_python_files_in_dir(self, path: Path) -> List[str]:
        """Find all Python files in a directory.

        Args:
            path: Project directory path

        Returns:
            List of Python file paths
        """
        py_files = []

        for root, _, files in os.walk(str(path)):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), str(path))
                    # Skip .venv directory and __pycache__
                    if not rel_path.startswith(".venv") and not rel_path.startswith("__pycache__"):
                        py_files.append(rel_path)

        return py_files

    async def _run_ruff_check(self, path: Path, py_files: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            return []

        # Verify the files exist
        existing_files = []
        for file_path in py_files:
            full_path = path / file_path
            if full_path.exists():
                existing_files.append(file_path)

        if not existing_files:
            return []

        py_files = existing_files

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
            proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout_bytes, _ = await proc.communicate()

            stdout_text = stdout_bytes.decode().strip() if stdout_bytes else ""

            issues = []

            # Only try to parse JSON if we actually have output
            if stdout_text:
                try:
                    json_data = json.loads(stdout_text)

                    for item in json_data:
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

                            # Create issue object
                            issues.append({
                                "file": item.get("filename", ""),
                                "line": row,
                                "column": column,
                                "code": item.get("code", ""),
                                "message": item.get("message", ""),
                                "fix_available": fix_applicable,
                            })
                        except Exception:
                            # Skip issues we can't parse properly
                            continue
                except json.JSONDecodeError:
                    # If JSON parsing fails, return empty list
                    return []

            return issues

        except Exception:
            return []

    async def _run_ruff_fix(self, path: Path, py_files: List[str], config: Dict[str, Any]) -> bool:
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
            proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            await proc.communicate()

            return proc.returncode == 0

        except Exception:
            return False

    async def _get_file_hashes(self, path: Path, file_paths: List[str]) -> Dict[str, str]:
        """Get MD5 hashes of files for change detection.

        Args:
            path: Project directory path
            file_paths: List of file paths

        Returns:
            Dictionary mapping file paths to MD5 hashes
        """
        import hashlib

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

    def _get_modified_files(self, before_hashes: Dict[str, str], after_hashes: Dict[str, str]) -> List[str]:
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
