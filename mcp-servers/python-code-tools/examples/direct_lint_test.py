#!/usr/bin/env python3
"""Direct test of the RuffProjectLinter without going through MCP."""

import asyncio
import json
import os
import sys

# Import the linter directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python_code_tools.linters.project import RuffProjectLinter


async def main():
    """Main function to test the linter directly."""
    # Use current directory as the project path
    project_path = os.getcwd()
    print(f"Using project path: {project_path}")

    # Create the linter
    linter = RuffProjectLinter()

    # Run the linter with explicit rule selection to match diagnostic
    result = await linter.lint_project(
        project_path=project_path,
        file_patterns=["**/*.py", "*.py"],
        fix=True,
        config={"select": "ALL"},  # Enable all rules to match diagnostic script
    )

    # Convert to dict for pretty printing
    result_dict = result.model_dump()

    # Print a summary
    print("\nLinter Results Summary:")
    print(f"Issues found: {len(result_dict['issues'])}")
    print(f"Fixed issues: {result_dict['fixed_count']}")
    print(f"Remaining issues: {result_dict['remaining_count']}")
    print(f"Modified files: {len(result_dict['modified_files'])}")
    print(f"Project has Ruff config: {result_dict['has_ruff_config']}")

    # Print issues by file
    if result_dict["issues"]:
        print("\nIssues by file:")
        issues_by_file = {}
        for issue in result_dict["issues"]:
            file_path = issue.get("file", "unknown")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        for file_path, issues in issues_by_file.items():
            print(f"\nFile: {file_path} - {len(issues)} issues")
            for issue in issues[:5]:  # Show up to 5 issues per file
                print(
                    f"  - Line {issue.get('line', '?')}, Col {issue.get('column', '?')}: "
                    f"{issue.get('code', '?')} - {issue.get('message', '?')}"
                )
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more issues")

    # Print modified files
    if result_dict["modified_files"]:
        print("\nModified files:")
        for file in result_dict["modified_files"][:10]:  # Show up to 10 files
            print(f"  - {file}")
        if len(result_dict["modified_files"]) > 10:
            print(f"  ... and {len(result_dict['modified_files']) - 10} more files")

    # Save the full result to a file for inspection
    with open("linter_result.json", "w") as f:
        json.dump(result_dict, f, indent=2)
    print("\nFull results saved to linter_result.json")


if __name__ == "__main__":
    asyncio.run(main())
