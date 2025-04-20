from pathlib import Path

from python_code_tools.linters.base import ProjectLinter, ProjectLintResult
from python_code_tools.linters.ruff.config import get_config
from python_code_tools.linters.ruff.reporter import create_issues_summary, identify_fixed_issues, print_final_report
from python_code_tools.linters.ruff.runner import get_python_files, run_ruff_check, run_ruff_fix
from python_code_tools.linters.ruff.utils import get_file_hashes, get_modified_files


class RuffProjectLinter(ProjectLinter):
    def __init__(self, **kwargs) -> None:
        super().__init__(name="ruff-project", **kwargs)

    async def lint_project(self, project_path: str, file_patterns=None, fix=True, config=None) -> ProjectLintResult:
        path = Path(project_path)
        effective_config, config_source = await get_config(config)
        has_ruff_config = config_source != "default"

        # Properly structure the config summary as a dictionary of dictionaries
        config_summary = {"ruff": {}}
        for key, value in effective_config.items():
            config_summary["ruff"][key] = value

        py_files = await get_python_files(path, file_patterns)
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
                fixed_issues=[],
                fixed_issues_summary={},
            )

        # Initial scan - find all issues before fixing
        initial_issues = await run_ruff_check(path, py_files, effective_config)
        total_issues_count = len(initial_issues)

        # Create a copy of initial issues for tracking
        remaining_issues_list = initial_issues.copy()
        fixed_issues_list = []
        modified_files = []

        # Only run the fixer if requested and there are issues to fix
        if fix and initial_issues:
            before_hashes = await get_file_hashes(path, py_files)

            # Run the auto-fix
            await run_ruff_fix(path, py_files, effective_config)

            # Check what's changed
            after_hashes = await get_file_hashes(path, py_files)
            modified_files = get_modified_files(before_hashes, after_hashes)

            # Get remaining issues after fixing
            remaining_issues_list = await run_ruff_check(path, py_files, effective_config)

            # Identify which issues were actually fixed
            fixed_issues_list = identify_fixed_issues(initial_issues, remaining_issues_list)

        # Calculate counts
        fixed_issues_count = len(fixed_issues_list)
        remaining_issues_count = len(remaining_issues_list)

        # Debug info
        print(f"DEBUG: Initial issues found: {total_issues_count}")
        print(f"DEBUG: Issues fixed: {fixed_issues_count}")
        print(f"DEBUG: Issues remaining: {remaining_issues_count}")

        # Sanity check
        expected_total = fixed_issues_count + remaining_issues_count
        if total_issues_count != expected_total:
            print(
                f"WARNING: Issue count mismatch - initial: {total_issues_count}, "
                f"calculated total: {expected_total} (fixed: {fixed_issues_count} + remaining: {remaining_issues_count})"
            )

            # Adjust total to match reality if needed
            if expected_total > total_issues_count:
                total_issues_count = expected_total
                print(f"Adjusted total issues count to {total_issues_count}")

        # Create summaries
        fixed_summary = create_issues_summary(fixed_issues_list, "fixed_types", "total_fixed")
        files_summary = create_issues_summary(remaining_issues_list, "issue_types", "total_issues")

        print_final_report(
            total_issues_count,
            fixed_issues_count,
            remaining_issues_count,
            modified_files,
            fixed_issues_list,
            remaining_issues_list,
            files_summary,
            fixed_summary,
        )

        # Return the results with the correct counts
        return ProjectLintResult(
            issues=remaining_issues_list,
            fixed_count=fixed_issues_count,
            remaining_count=remaining_issues_count,
            modified_files=modified_files,
            project_path=str(path),
            has_ruff_config=has_ruff_config,
            config_source=config_source,
            config_summary=config_summary,
            files_summary=files_summary,
            fixed_issues=fixed_issues_list,
            fixed_issues_summary=fixed_summary,
        )
