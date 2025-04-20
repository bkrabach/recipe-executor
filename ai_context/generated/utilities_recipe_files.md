=== File: recipes/utilities/generate_from_files.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ files }}",
        "contents_key": "combined_input",
        "merge_mode": "concat"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "{% if combined_input != '' %}{{combined_input}}{% else %}A request was made to generate an output based upon some files that were read in, but no files were received, please respond with an `error.md` file that contains a message indicating that no files were read and that 'context.path' must contain a valid list of files.{% endif %}",
        "model": "{{model|default:'openai/o3-mini'}}",
        "output_format": "files",
        "output_key": "llm_output"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "llm_output",
        "root": "{{output_root|default:'output'}}"
      }
    }
  ]
}


