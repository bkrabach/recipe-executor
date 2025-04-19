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
        project_config, config_source = await self._read_project_config(path)
        has_ruff_config = bool(project_config)

        # Merge configurations (priority: user config > project config > default config)
        effective_config, config_summary = self._merge_configs(
            user_config=config or {},
            project_config=project_config,
        )

        # Get a list of Python files to lint
        py_files = await self._get_python_files(path, file_patterns)

        # If no Python files found, return empty result
        if not py_files:
            return ProjectLintResult(
                issues=[],
                fixed_count=0,
                remaining_count=0,
                modified_files=[],
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                config_source=config_source,
                config_summary=config_summary,
                files_summary={},
            )

        try:
            # First, check for issues without fixing them
            initial_issues = await self._run_ruff_check(path, py_files, effective_config)
            initial_issue_count = len(initial_issues)

            # Get file hashes before fixing to detect changes
            file_hashes_before = await self._get_file_hashes(path, py_files)

            # Run the fix command if requested and if there are issues
            if fix and initial_issues:
                await self._run_ruff_fix(path, py_files, effective_config)

            # Get file hashes after fixing to detect changes
            file_hashes_after = await self._get_file_hashes(path, py_files)

            # Determine which files were actually modified
            modified_files = self._get_modified_files(file_hashes_before, file_hashes_after)

            # Check for remaining issues after fixing
            remaining_issues = await self._run_ruff_check(path, py_files, effective_config)

            # Calculate fixed count
            fixed_count = initial_issue_count - len(remaining_issues)

            # Create a summary of findings by file
            files_summary = {}
            for issue in remaining_issues:
                file_path = issue.get("file", "unknown")
                if file_path not in files_summary:
                    files_summary[file_path] = {"total_issues": 0, "issue_types": {}}

                files_summary[file_path]["total_issues"] += 1

                code = issue.get("code", "unknown")
                if code not in files_summary[file_path]["issue_types"]:
                    files_summary[file_path]["issue_types"][code] = 0
                files_summary[file_path]["issue_types"][code] += 1

            return ProjectLintResult(
                issues=remaining_issues,
                fixed_count=fixed_count,
                remaining_count=len(remaining_issues),
                modified_files=modified_files,
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                config_source=config_source,
                config_summary=config_summary,
                files_summary=files_summary,
            )

        except Exception as e:
            print(f"Error during project linting: {e}")
            return ProjectLintResult(
                issues=[],
                fixed_count=0,
                remaining_count=0,
                modified_files=[],
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                config_source=config_source,
                config_summary=config_summary,
                files_summary={},
            )

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

        # Check for pyproject.toml
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

        # Check for ruff.toml (takes precedence over pyproject.toml)
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
            except Exception as e:
                print(f"Error reading .ruff.toml: {e}")

        return config, source

    def _merge_configs(
        self, user_config: Dict[str, Any], project_config: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """Merge configuration sources based on priority.

        Args:
            user_config: Configuration provided by the user
            project_config: Configuration from the project's config files

        Returns:
            Tuple of (effective configuration, configuration summary)
        """
        effective_config = {}
        config_summary = {
            "default": self.default_config.copy(),
            "project": project_config.copy(),
            "user": user_config.copy(),
        }

        # Start with default config (lowest priority)
        effective_config.update(self.default_config)

        # Project config overrides default
        effective_config.update(project_config)

        # User config has highest priority
        effective_config.update(user_config)

        return effective_config, config_summary

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
                stdout, _ = await proc.communicate()

                try:
                    # Parse JSON output to get files
                    data = json.loads(stdout.decode())
                    for item in data:
                        file_path = item.get("filename")
                        if file_path and file_path not in py_files:
                            py_files.append(file_path)
                except:
                    # Fallback to directory scanning if JSON parsing fails
                    py_files = self._find_python_files_in_dir(path)
            except:
                # Fallback to directory scanning
                py_files = self._find_python_files_in_dir(path)
        else:
            # Scan directory for Python files
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
        cmd = ["ruff", "check", "--output-format=json"]

        # Add configuration options
        if "select" in config:
            cmd.extend(["--select", config["select"]])

        if "ignore" in config and config["ignore"]:
            if isinstance(config["ignore"], list):
                cmd.extend(["--ignore", ",".join(config["ignore"])])
            else:
                cmd.extend(["--ignore", config["ignore"]])

        if "line-length" in config:
            cmd.extend(["--line-length", str(config["line-length"])])

        # Add files to check
        cmd.extend(py_files)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, _ = await proc.communicate()

            issues = []
            output = stdout.decode().strip()

            if output:
                try:
                    json_data = json.loads(output)

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

        except Exception as e:
            print(f"Error checking issues: {e}")
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
        cmd = ["ruff", "check", "--fix"]

        # Add configuration options
        if "select" in config:
            cmd.extend(["--select", config["select"]])

        if "ignore" in config and config["ignore"]:
            if isinstance(config["ignore"], list):
                cmd.extend(["--ignore", ",".join(config["ignore"])])
            else:
                cmd.extend(["--ignore", config["ignore"]])

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

        except Exception as e:
            print(f"Error fixing issues: {e}")
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
