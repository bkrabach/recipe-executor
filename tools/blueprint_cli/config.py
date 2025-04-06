"""
Configuration module for the Blueprint CLI tool.

This module handles configuration loading and provides access to default values.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProjectConfig:
    """Configuration for a project."""

    # Primary configuration
    project_spec: str
    output_dir: str = "output"
    target_project: str = "generated_project"

    # File collections extracted from project spec
    context_files: List[Dict[str, str]] = field(default_factory=list)
    reference_docs: List[Dict[str, str]] = field(default_factory=list)

    # Processing options
    model: str = "openai:o3-mini"
    verbose: bool = False

    def __post_init__(self):
        """Initialize file references from project spec."""
        # Always include built-in context files
        self._add_built_in_context()

        # Extract file references from project spec
        if os.path.exists(self.project_spec):
            self._extract_file_references_from_spec()

    def _add_built_in_context(self):
        """Add built-in context files to the context_files list."""
        # Get the directory of this module (works regardless of installation location)
        module_dir = os.path.dirname(os.path.abspath(__file__))
        ai_context_dir = os.path.join(module_dir, "ai_context")

        # Look for implementation philosophy files
        built_in_files = [
            {
                "path": os.path.join(ai_context_dir, "IMPLEMENTATION_PHILOSOPHY.md"),
                "rationale": "Core implementation philosophy guide",
            },
            {
                "path": os.path.join(ai_context_dir, "MODULAR_DESIGN_PHILOSOPHY.md"),
                "rationale": "Modular design principles guide",
            },
        ]

        # Only add files that exist
        for file_info in built_in_files:
            if os.path.exists(file_info["path"]):
                # Check if already added
                if not any(item.get("path") == file_info["path"] for item in self.context_files):
                    self.context_files.append(file_info)

    def _extract_file_references_from_spec(self):
        """Extract file references from the project spec."""
        try:
            with open(self.project_spec, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for file references sections
            self._extract_context_files(content)
            self._extract_reference_docs(content)
        except Exception as e:
            # Just log the error and continue
            print(f"Warning: Failed to extract file references from spec: {e}")

    def _extract_context_files(self, content):
        """Extract context files from the project spec content."""
        # Look for context files section using regex
        context_section = self._extract_section(content, "Context Files", "Reference Docs")
        if context_section:
            self._parse_file_references(context_section, self.context_files)

    def _extract_reference_docs(self, content):
        """Extract reference docs from the project spec content."""
        # Look for reference docs section using regex
        ref_section = self._extract_section(content, "Reference Docs")
        if ref_section:
            self._parse_file_references(ref_section, self.reference_docs)

    def _extract_section(self, content, section_name, next_section=None):
        """Extract a section from the content."""
        # Look for the section header (different header levels)
        patterns = [
            rf"#\s+{section_name}\s*\n(.*?)(?=\n#\s+|$)",  # # Section Name
            rf"##\s+{section_name}\s*\n(.*?)(?=\n##\s+|$)",  # ## Section Name
            rf"###\s+{section_name}\s*\n(.*?)(?=\n###\s+|$)",  # ### Section Name
            rf"####\s+{section_name}\s*\n(.*?)(?=\n####\s+|$)",  # #### Section Name
            rf"\n{section_name}\s*\n[-=]+\s*\n(.*?)(?=\n\w+\s*\n[-=]+|$)",  # Section Name
            # =---------=
        ]

        # If next_section is provided, adjust patterns to stop at that section
        if next_section:
            patterns = [
                rf"#\s+{section_name}\s*\n(.*?)(?=\n#\s+{next_section}|\n#\s+|$)",
                rf"##\s+{section_name}\s*\n(.*?)(?=\n##\s+{next_section}|\n##\s+|$)",
                rf"###\s+{section_name}\s*\n(.*?)(?=\n###\s+{next_section}|\n###\s+|$)",
                rf"####\s+{section_name}\s*\n(.*?)(?=\n####\s+{next_section}|\n####\s+|$)",
                rf"\n{section_name}\s*\n[-=]+\s*\n(.*?)(?=\n{next_section}\s*\n[-=]+|\n\w+\s*\n[-=]+|$)",
            ]

        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()

        return None

    def _parse_file_references(self, section_content, target_list):
        """Parse file references from section content."""
        # Look for lines with either:
        # - path: rationale
        # - `path`: rationale
        # - • path: rationale
        # - * path: rationale
        # - - path: rationale
        patterns = [
            r"[•\*\-]?\s*(?:`([^`]+)`|(\S+)):\s*(.*?)$",  # With a colon separator
            r"[•\*\-]?\s*(?:`([^`]+)`|(\S+))\s+-\s*(.*?)$",  # With a dash separator
        ]

        for line in section_content.split("\n"):
            line = line.strip()
            if not line:
                continue

            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # Either backtick group or regular group
                    path = match.group(1) or match.group(2)
                    rationale = match.group(3).strip()

                    # Handle paths relative to the project spec
                    path = self._resolve_path(path)

                    if os.path.exists(path):
                        target_list.append({"path": path, "rationale": rationale})
                    else:
                        print(f"Warning: Referenced file not found: {path}")

                    break

    def _resolve_path(self, path):
        """
        Resolve path considering multiple possible reference points.

        Try these in order:
        1. Absolute path
        2. Relative to current working directory
        3. Relative to project spec directory
        4. Relative to sample directory (if applicable)
        """
        # Check if it's an absolute path
        if os.path.isabs(path):
            return path

        # Try relative to current working directory
        cwd_path = os.path.abspath(path)
        if os.path.exists(cwd_path):
            return cwd_path

        # Try relative to project spec directory
        spec_dir = os.path.dirname(os.path.abspath(self.project_spec))
        spec_relative_path = os.path.normpath(os.path.join(spec_dir, path))
        if os.path.exists(spec_relative_path):
            return spec_relative_path

        # Try looking in sample/docs directory if spec is in a sample directory
        if "sample" in spec_dir:
            sample_dir = os.path.join(spec_dir.split("sample")[0], "sample")
            sample_docs_path = os.path.normpath(os.path.join(sample_dir, "docs", path))
            if os.path.exists(sample_docs_path):
                return sample_docs_path

            # Also try just relative to sample directory
            sample_relative_path = os.path.normpath(os.path.join(sample_dir, path))
            if os.path.exists(sample_relative_path):
                return sample_relative_path

        # If we couldn't find it, return the path relative to project spec as a fallback
        return spec_relative_path

    def get_context_paths(self) -> List[str]:
        """Get list of context file paths."""
        return [item["path"] for item in self.context_files]

    def get_reference_paths(self) -> List[str]:
        """Get list of reference doc paths."""
        return [item["path"] for item in self.reference_docs]


def create_config_from_args(args) -> ProjectConfig:
    """
    Create a ProjectConfig from parsed command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        ProjectConfig instance
    """
    return ProjectConfig(
        project_spec=args.project_spec,
        output_dir=args.output_dir,
        target_project=args.target_project,
        model=args.model,
        verbose=args.verbose,
    )
