"""Base interfaces for code linters."""

import abc
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LintResult(BaseModel):
    """Result model for code linting."""

    issues: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of issues found in the code"
    )
    fixed_count: int = Field(0, description="Number of issues that were automatically fixed")
    remaining_count: int = Field(0, description="Number of issues that could not be fixed")


class CodeLintResult(LintResult):
    """Result model for single code snippet linting."""

    fixed_code: str = Field(..., description="The code after linting and fixing (if enabled)")


class ProjectLintResult(LintResult):
    """Result model for project linting."""

    modified_files: List[str] = Field(
        default_factory=list, description="List of files that were modified by auto-fixes"
    )
    project_path: str = Field(..., description="Path to the project directory that was linted")
    has_ruff_config: bool = Field(
        False, description="Whether the project has a ruff configuration file"
    )
    files_summary: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Summary of issues by file"
    )


class BaseLinter(abc.ABC):
    """Abstract base class for all linters."""

    def __init__(self, name: str, **kwargs):
        """Initialize the linter.

        Args:
            name: The name of the linter
            **kwargs: Additional configuration options
        """
        self.name = name
        self.config = kwargs


class CodeLinter(BaseLinter):
    """Abstract base class for code snippet linters."""

    @abc.abstractmethod
    async def lint_code(
        self, code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None
    ) -> CodeLintResult:
        """Lint the provided code snippet and return the results.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A CodeLintResult object containing the fixed code and issue details
        """
        pass


class ProjectLinter(BaseLinter):
    """Abstract base class for project directory linters."""

    @abc.abstractmethod
    async def lint_project(
        self,
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> ProjectLintResult:
        """Lint a project directory and return the results.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A ProjectLintResult object containing issues found and fix details
        """
        pass
