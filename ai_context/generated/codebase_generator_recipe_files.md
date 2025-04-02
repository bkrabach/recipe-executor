=== File: recipes/codebase_generator/generate_code.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "read_files",
      "path": "ai_context/dev_guides/DEV_GUIDE_FOR_{{language | upcase}}.md",
      "artifact": "dev_guide",
      "optional": true
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer. Based on the following specification{% if existing_code %} and existing code{% endif %}, generate {{language|default:'python'}} code for the {{component_id}} component of a larger project.\n\nSpecification:\n{{spec}}\n\n{% if existing_code %}<EXISTING_CODE>\n{{existing_code}}\n</EXISTING_CODE>\n\n{% endif %}{% if usage_docs %}<USAGE_DOCUMENTATION>\n{{usage_docs}}\n</USAGE_DOCUMENTATION>\n{% endif %}{% if additional_content %}{{additional_content}}\n{% endif %}\nEnsure the code follows the specification exactly, implements all required functionality, and adheres to the implementation philosophy described in the tags. Include appropriate error handling and type hints. The implementation should be minimal but complete.\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n{% if dev_guide != '' %}<DEV_GUIDE>{{dev_guide}}</DEV_GUIDE>\n{% endif %}\nGenerate the appropriate file(s): {{output_path|default:'/'}}{{component_id}}.<ext>, etc.\n\n",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_code"
    },
    {
      "type": "write_files",
      "artifact": "generated_code",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


