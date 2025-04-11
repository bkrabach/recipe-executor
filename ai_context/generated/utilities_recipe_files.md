=== File: recipes/utilities/create_recipe_json.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{input}}",
      "artifact": "recipe_idea"
    },
    {
      "type": "read_files",
      "path": [
        "ai_context/generated/recipe_executor_code_files.md",
        "ai_context/generated/recipe_executor_recipe_files.md"
      ],
      "artifact": "context_files",
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "Create a new JSON recipe file for use with recipe executor based on the following content:\n\n- Recipe Idea: {{recipe_idea}}\n- Context Files:\n  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>\n  {% if additional_files != '' %}\n- Additional Files:\n  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>\n  {% endif %}\n\nSave the generated recipe file as `generated_recipe.json` unless a different name is specified in the recipe idea.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_recipe"
    },
    {
      "type": "write_files",
      "artifact": "generated_recipe",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/utilities/generate_from_files.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{ files }}",
      "artifact": "combined_input",
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "{% if combined_input != '' %}{{combined_input}}{% else %}A request was made to generate a response based upon some files that were read in, but no files were received, please respond with an `error.md` file that contains a message indicating that no files were read and that 'context.path' must contain a valid list of files.{% endif %}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "llm_response"
    },
    {
      "type": "write_files",
      "artifact": "llm_response",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/utilities/prompts/create_recipe_json.md ===
## Goal

Create a new JSON recipe file for creating new JSON recipe files, named `create_recipe_json.json`.

## How

Start wtih upload of a **required** recipe idea file. This path is passed in via a context key of `input`.

The next step should load the following files into context as `context_files`:

- `ai_context/generated/recipe_executor_code_files.md`
- `ai_context/generated/recipe_executor_recipe_files.md`

After that, load any other files that are passed in via the `files` context variable. These files should be considered optional and stored in a variable called `additional_files`.

Use the LLM (default set to use `openai:o3-mini`) to generate the content for a JSON recipe file:

```markdown
Create a new JSON recipe file for use with recipe executor based on the following content:

- Recipe Idea: {{recipe_idea}}
- Context Files:
  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>
  {% if additional_files != '' %}
- Additional Files:
  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>
  {% endif %}

Save the generated recipe file as `generated_recipe.json` unless a different name is specified in the recipe idea.
```

The final step should be to save the generated file. The root should be set to value of `output_root` variable, defaulting to the `output` directory.


=== File: recipes/utilities/prompts/recipe_creator-future_version.md ===
Create a new JSON recipe file in the current folder. It should be named `create_recipe.json`. The recipe should use the `read_files` step to load a file that contains a request for a recipe to be created, from context key `input`. This file should be configurable via context, and the default value should be an error message indicating that the file is missing. The loaded content should be stored in a variable called `input`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- `ai_context/generated/recipe_executor_code_files.md`
- `ai_context/generated/recipe_executor_recipe_files.md`

The `input` value will be of type FileGenerationResult from the recipe executor, you will need to unpack that value properly to use it in the next `generate` step.

Pass the loaded content to a `generate` step that extracts values to `recipe_idea`, `additional_files`, and `target_file` from the loaded content if such values are present. If the values are not present, assume the request is actually the recipe idea and set `recipe_idea` to the loaded content. The `additional_files` value should be a comma-separated list of files to be loaded into context, and the `target_file` value should be the name of the file to save the generated recipe to.

The next step should be another `generate` step that should _start with_:

```
Create a new recipe file based on the following content:
- Recipe Idea: {recipe_idea}
- Context Files: {context_files}
{% if additional_files != '' %}
- Additional Files: {additional_files}
{% endif %}

Save the generated recipe file as {{target_file|default:'generated_recipe.json'}}.
```

Default model for this recipe should be: `openai:o3-mini`

The final step should be a `write_files` step that saves the generated recipe file to the specified target file. The `root` should be set to: {{output_root|default:'output'}}

Consider the ideas and patterns expressed in _this_ request as good practices to append to the end of the generated recipe's generation prompt.


