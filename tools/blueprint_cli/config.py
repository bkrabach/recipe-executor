import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProjectConfig:
    """Configuration for a project."""

    project_spec: str
    component_spec: Optional[str] = None
    output_dir: str = "output"
    target_project: str = "generated_project"
    guidance_files: List[Dict[str, str]] = field(default_factory=list)
    context_files: List[Dict[str, str]] = field(default_factory=list)
    reference_docs: List[Dict[str, str]] = field(default_factory=list)
    model: str = "openai:o3-mini"
    verbose: bool = False
    auto_run: bool = False

    def __post_init__(self):
        self._add_guidance_files()
        # Only auto-extract if not provided explicitly
        if os.path.exists(self.project_spec) and not (self.context_files or self.reference_docs):
            self._extract_file_references_from_spec()

    def _add_guidance_files(self):
        """Add built-in guidance files to the guidance_files list."""
        module_dir = os.path.dirname(os.path.abspath(__file__))
        ai_context_dir = os.path.join(module_dir, "ai_context")
        guidance_files = [
            {
                "path": os.path.join(ai_context_dir, "IMPLEMENTATION_PHILOSOPHY.md"),
                "rationale": "Core implementation philosophy guide",
            },
            {
                "path": os.path.join(ai_context_dir, "MODULAR_DESIGN_PHILOSOPHY.md"),
                "rationale": "Modular design principles guide",
            },
        ]
        for file_info in guidance_files:
            if os.path.exists(file_info["path"]):
                if not any(item.get("path") == file_info["path"] for item in self.context_files):
                    self.guidance_files.append(file_info)

    def _extract_file_references_from_spec(self):
        """Parse the spec into sections and extract file references."""
        try:
            with open(self.project_spec, "r", encoding="utf-8") as f:
                content = f.read()
            sections = self._parse_sections(content)
            if "Context Files" in sections:
                self._parse_file_references(sections["Context Files"], self.context_files)
            else:
                print("Warning: No 'Context Files' section found in the project spec.")
            if "Reference Docs" in sections:
                self._parse_file_references(sections["Reference Docs"], self.reference_docs)
            else:
                print("Warning: No 'Reference Docs' section found in the project spec.")
        except Exception as e:
            print(f"Warning: Failed to extract file references from spec: {e}")

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """
        Parse the document into sections based on markdown headings.
        Returns a dictionary mapping heading text to the content until the next heading.
        Raises an error if the same heading appears more than once.
        """
        sections = {}
        current_heading: Optional[str] = None
        current_lines: List[str] = []
        for line in content.splitlines():
            heading_match = re.match(r"^\s*(#{1,6})\s*(.+?)\s*$", line)
            if heading_match:
                # Save the previous section, if any.
                if current_heading is not None:
                    if current_heading in sections:
                        raise ValueError(f"Multiple '{current_heading}' sections found in the project spec.")
                    sections[current_heading] = "\n".join(current_lines).strip()
                current_heading = heading_match.group(2)
                current_lines = []
            else:
                if current_heading is not None:
                    current_lines.append(line)
        if current_heading is not None:
            if current_heading in sections:
                raise ValueError(f"Multiple '{current_heading}' sections found in the project spec.")
            sections[current_heading] = "\n".join(current_lines).strip()
        return sections

    def _parse_file_references(self, section_content: str, target_list: List[Dict[str, str]]):
        """
        Parses file references from a section. Each nonempty line must be in the format:

          - `path/to/file`: Rationale for file

        The leading dash is optional.
        Throws an error if a line does not conform.
        """
        pattern = r"^\s*(-\s*)?`([^`]+)`:\s*(.+)$"
        for line in section_content.splitlines():
            line = line.strip()
            if not line:
                continue
            match = re.match(pattern, line)
            if not match:
                raise ValueError(
                    f"Invalid file reference format: '{line}'. Expected format: `path/to/file`: Rationale for file"
                )
            file_path = match.group(2).strip()
            rationale = match.group(3).strip()
            file_path = self._resolve_path(file_path)
            if os.path.exists(file_path):
                target_list.append({"path": file_path, "rationale": rationale})
            else:
                print(f"Warning: Referenced file not found: {file_path}")

    def _resolve_path(self, path: str) -> str:
        """
        Resolve a file path relative to multiple possible locations.
        """
        if os.path.isabs(path):
            return path
        cwd_path = os.path.abspath(path)
        if os.path.exists(cwd_path):
            return cwd_path
        spec_dir = os.path.dirname(os.path.abspath(self.project_spec))
        spec_relative_path = os.path.normpath(os.path.join(spec_dir, path))
        if os.path.exists(spec_relative_path):
            return spec_relative_path
        if "sample" in spec_dir:
            sample_dir = os.path.join(spec_dir.split("sample")[0], "sample")
            sample_docs_path = os.path.normpath(os.path.join(sample_dir, "docs", path))
            if os.path.exists(sample_docs_path):
                return sample_docs_path
            sample_relative_path = os.path.normpath(os.path.join(sample_dir, path))
            if os.path.exists(sample_relative_path):
                return sample_relative_path
        return spec_relative_path

    def get_context_paths(self) -> List[str]:
        return [item["path"] for item in self.context_files]

    def get_reference_paths(self) -> List[str]:
        return [item["path"] for item in self.reference_docs]


def create_config_from_args(args) -> ProjectConfig:
    return ProjectConfig(
        project_spec=args.project_spec,
        output_dir=args.output_dir,
        target_project=args.target_project,
        model=args.model,
        verbose=args.verbose,
    )
