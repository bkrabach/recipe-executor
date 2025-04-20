from typing import Any, Dict, List


def create_issues_summary(issues: List[Dict[str, Any]], types_key: str, total_key: str) -> Dict[str, Dict[str, Any]]:
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


def identify_fixed_issues(
    initial_issues: List[Dict[str, Any]], remaining_issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Identify which issues were fixed by comparing initial and remaining issues.

    Args:
        initial_issues: List of issues found before fixing
        remaining_issues: List of issues found after fixing

    Returns:
        List of issues that were fixed
    """
    # Create a map of remaining issues for quick lookup
    # Use a more robust signature that takes into account file path and issue code
    # This fixes the problem where line numbers change due to code deletion
    remaining_map = {}
    for issue in remaining_issues:
        file_path = issue.get("file", "")
        code = issue.get("code", "")
        message = issue.get("message", "")

        # Create a composite key that identifies the issue type and content
        # but not its location (since that can change)
        key = f"{file_path}:{code}:{message}"

        if key not in remaining_map:
            remaining_map[key] = 0
        remaining_map[key] += 1

    # Find issues that were truly fixed (not just moved)
    fixed_issues = []
    for issue in initial_issues:
        file_path = issue.get("file", "")
        code = issue.get("code", "")
        message = issue.get("message", "")

        key = f"{file_path}:{code}:{message}"

        if key not in remaining_map or remaining_map[key] == 0:
            # This issue was completely fixed
            fixed_issues.append(issue)
        else:
            # This issue still exists, decrement the count
            remaining_map[key] -= 1

    return fixed_issues


def print_final_report(
    total_issue_count: int,
    fixed_count: int,
    remaining_count: int,
    modified_files: List[str],
    fixed_issues: List[Dict[str, Any]],
    remaining_issues: List[Dict[str, Any]],
    files_summary: Dict[str, Any],
    fixed_issues_summary: Dict[str, Any],
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
            print("This can happen with certain types of issues that the linter can detect but not automatically fix.")
