"""Ruff linter implementation."""

import asyncio
import subprocess
from typing import Any, Dict, List, Optional

from python_code_tools.linters.base import CodeLinter, CodeLintResult
from python_code_tools.utils.temp_file import cleanup_temp_file, create_temp_file


class RuffLinter(CodeLinter):
    """Code linter implementation using Ruff."""

    def __init__(self, **kwargs):
        """Initialize the Ruff linter.

        Args:
            **kwargs: Additional configuration options for Ruff
        """
        super().__init__(name="ruff", **kwargs)

    async def lint_code(
        self, code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None
    ) -> CodeLintResult:
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
            # Build the ruff command
            cmd = ["ruff", "check", str(file_path)]

            # Add fix flag if requested
            if fix:
                cmd.append("--fix")

            # Add any config options
            if config:
                for key, value in config.items():
                    cmd.extend(["--config", f"{key}={value}"])

            # Run ruff to get issues
            issues_proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            stdout, stderr = await issues_proc.communicate()
            issues_output = stdout.decode()

            # Parse issues
            issues = self._parse_ruff_output(issues_output)

            # Read the fixed code
            with open(file_path, "r") as f:
                fixed_code = f.read()

            # Determine fixed and remaining counts
            fixed_count = 0
            remaining_count = len(issues)

            if fix and code != fixed_code:
                # If code was modified, count the difference as fixes
                original_issues_count = await self._count_issues(code)
                fixed_count = max(0, original_issues_count - remaining_count)

            return CodeLintResult(
                fixed_code=fixed_code,
                issues=issues,
                fixed_count=fixed_count,
                remaining_count=remaining_count,
            )

        finally:
            # Clean up temporary file
            cleanup_temp_file(temp_file, file_path)

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

    async def _count_issues(self, code: str) -> int:
        """Count the number of issues in the original code.

        Args:
            code: The Python code to analyze

        Returns:
            The number of issues found in the code
        """
        temp_file, file_path = create_temp_file(code, suffix=".py")

        try:
            # Run ruff without fixing to get original issue count
            result = await asyncio.create_subprocess_exec(
                "ruff", "check", str(file_path), stdout=subprocess.PIPE
            )

            stdout, _ = await result.communicate()
            output = stdout.decode()

            # Count non-empty lines in the output
            issues = [line for line in output.strip().split("\n") if line]
            return len(issues)

        except Exception:
            return 0
        finally:
            # Clean up
            cleanup_temp_file(temp_file, file_path)
