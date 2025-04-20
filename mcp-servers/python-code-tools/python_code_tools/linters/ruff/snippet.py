"""Ruff linter implementation for single code snippets."""

import asyncio
import json
import subprocess
from typing import Any, Dict, List, Optional

from python_code_tools.linters.base import CodeLinter, CodeLintResult
from python_code_tools.utils.temp_file import cleanup_temp_file, create_temp_file


class RuffLinter(CodeLinter):
    """Code linter implementation using Ruff."""

    def __init__(self, **kwargs) -> None:
        """Initialize the Ruff linter.

        Args:
            **kwargs: Additional configuration options for Ruff
        """
        super().__init__(name="ruff", **kwargs)

    async def lint_code(self, code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None) -> CodeLintResult:
        """Lint code using Ruff and return the results.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for Ruff

        Returns:
            A CodeLintResult object containing the fixed code and issue details
        """
        temp_file, file_path = create_temp_file(code, suffix=".py")

        try:
            # First, get original issues (before fixing)
            # Convert Path to string for _get_issues
            initial_issues = await self._get_issues(str(file_path), config)
            initial_count = len(initial_issues)

            print(f"Initial scan found {initial_count} issues")

            # Keep a copy of the original code
            with open(file_path, "r") as f:
                original_code = f.read()

            # Only try to fix if requested and there are issues
            fixed_code = original_code
            remaining_issues = initial_issues
            if fix and initial_count > 0:
                # Run ruff with --fix flag - convert Path to string
                fix_success = await self._run_fix(str(file_path), config)

                if fix_success:
                    # Read the fixed code
                    with open(file_path, "r") as f:
                        fixed_code = f.read()

                    # Get remaining issues after fixing - convert Path to string
                    remaining_issues = await self._get_issues(str(file_path), config)

                print(f"After fixing, {len(remaining_issues)} issues remain")

            # Calculate fixed count
            fixed_count = initial_count - len(remaining_issues)
            remaining_count = len(remaining_issues)

            # Debug info
            print(f"DEBUG: Initial issues: {initial_count}")
            print(f"DEBUG: Fixed issues: {fixed_count}")
            print(f"DEBUG: Remaining issues: {remaining_count}")

            return CodeLintResult(
                fixed_code=fixed_code,
                issues=remaining_issues,
                fixed_count=fixed_count,
                remaining_count=remaining_count,
            )

        finally:
            # Clean up temporary file
            cleanup_temp_file(temp_file, file_path)

    async def _get_issues(self, file_path: str, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get issues from a file using ruff check with JSON output.

        Args:
            file_path: Path to the Python file
            config: Optional configuration settings for Ruff

        Returns:
            List of issues found
        """
        # Build the ruff command for check only (no fixing)
        cmd = ["ruff", "check", file_path, "--output-format=json"]

        # Add config options if provided
        if config:
            for key, value in config.items():
                if key == "select":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--select", value_str])
                elif key == "ignore":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--ignore", value_str])
                elif key == "line-length":
                    cmd.extend(["--line-length", str(value)])

        try:
            # Run the command
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await proc.communicate()

            stdout_text = stdout.decode().strip() if stdout else ""
            stderr_text = stderr.decode().strip() if stderr else ""

            if stderr_text:
                print(f"WARNING: Ruff stderr: {stderr_text}")

            issues = []

            # Parse JSON output if available
            if stdout_text:
                try:
                    data = json.loads(stdout_text)

                    for item in data:
                        # Extract location data
                        location = item.get("location") or {}
                        row = location.get("row", 0) if isinstance(location, dict) else 0
                        column = location.get("column", 0) if isinstance(location, dict) else 0

                        # Extract fix data
                        fix_data = item.get("fix") or {}
                        fix_applicable = (
                            fix_data.get("applicability", "") == "applicable" if isinstance(fix_data, dict) else False
                        )

                        # Create issue object
                        issues.append({
                            "line": row,
                            "column": column,
                            "code": item.get("code", ""),
                            "message": item.get("message", ""),
                            "fix_available": fix_applicable,
                        })
                except json.JSONDecodeError as e:
                    print(f"ERROR: Failed to parse JSON output: {e}")
                    print(f"Raw output: {stdout_text[:200]}...")

            return issues

        except Exception as e:
            print(f"ERROR: Failed to run ruff check: {e}")
            return []

    async def _run_fix(self, file_path: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Run ruff with --fix flag to automatically fix issues.

        Args:
            file_path: Path to the Python file
            config: Optional configuration settings for Ruff

        Returns:
            True if fixing succeeded, False otherwise
        """
        # Build the ruff command for fixing
        cmd = ["ruff", "check", file_path, "--fix"]

        # Add config options if provided
        if config:
            for key, value in config.items():
                if key == "select":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--select", value_str])
                elif key == "ignore":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--ignore", value_str])
                elif key == "line-length":
                    cmd.extend(["--line-length", str(value)])

        try:
            # Run the command
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await proc.communicate()

            stderr_text = stderr.decode().strip() if stderr else ""
            if stderr_text:
                print(f"WARNING: Ruff fix stderr: {stderr_text}")

            return proc.returncode == 0

        except Exception as e:
            print(f"ERROR: Failed to run ruff fix: {e}")
            return False
