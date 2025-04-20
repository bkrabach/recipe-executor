=== File: recipes/recipe_creator/create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{input}}",
        "contents_key": "recipe_idea"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/generated/recipe_executor_code_files.md,ai_context/generated/recipe_executor_recipe_files.md",
        "contents_key": "context_files",
        "merge_mode": "concat"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{files}}",
        "contents_key": "additional_files",
        "optional": true,
        "merge_mode": "concat"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Create a new JSON recipe file for use with recipe executor based on the following content:\n\n- Recipe Idea: {{recipe_idea}}\n- Context Files:\n  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>\n  {% if additional_files %}\n- Additional Files:\n  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>\n  {% endif %}\n\nSave the generated recipe file as {{target_file | default:'generated_recipe.json'}} unless a different name is specified in the recipe idea.",
        "model": "{{model | default:'openai/o3-mini'}}",
        "output_format": "files",
        "output_key": "generated_recipe"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_recipe",
        "root": "{{output_root | default:'output'}}"
      }
    }
  ]
}


=== File: recipes/recipe_creator/prompts/create_recipe_json.md ===
## Goal

Create a new JSON recipe file for creating new JSON recipe files, named `create_recipe_json.json`.

## How

### Input context variables

- `input`: [Required] The file path to a recipe idea file.
- `files`: [Optional] A list of additional files to include in the recipe.
- `model`: [Optional] The model to use for generating the recipe. Defaults to `openai/o3-mini`.
- `output_root`: [Optional] The root directory for saving the generated recipe file. Defaults to `output`.
- `target_file`: [Optional] The name of the file to save the generated recipe to. Defaults to `generated_recipe.json` unless the recipe idea suggests a different name.

### Steps

1. Start with read of the recipe idea file (`input` context variable).

2. Always load the following files into context as `context_files`:

- `ai_context/generated/recipe_executor_code_files.md`
- `ai_context/generated/recipe_executor_recipe_files.md`

3. Load any other files that are passed in via the `files` context variable. These files should be considered optional and stored in a variable called `additional_files`.

4. Use the LLM (default set to use `openai/o3-mini`) to generate the content for a JSON recipe file:

```markdown
Create a new JSON recipe file for use with recipe executor based on the following content:

- Recipe Idea: {{recipe_idea}}
- Context Files:
  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>
  {% if additional_files %}
- Additional Files:
  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>
  {% endif %}

Save the generated recipe file as `generated_recipe.json` unless a different name is specified in the recipe idea.
```

5. Save the generated file.

- The root should be set to value of `output_root` context variable, or `output` if not specified.


=== File: recipes/recipe_creator/prompts/recipe_creator-future_version.md ===
Create a new JSON recipe file in the current folder. It should be named `create_recipe.json`. The recipe should use the `read_files` step to load a file that contains a request for a recipe to be created, from context key `input`. This file should be configurable via context, and the default value should be an error message indicating that the file is missing. The loaded content should be stored in a variable called `input`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- `ai_context/generated/recipe_executor_code_files.md`
- `ai_context/generated/recipe_executor_recipe_files.md`

The `input` value will be of type FileSpec or List[FileSpec] from the recipe executor, you will need to unpack that value properly to use it in the next `generate` step.

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

Default model for this recipe should be: `openai/o3-mini`

The final step should be a `write_files` step that saves the generated recipe file to the specified target file. The `root` should be set to: {{output_root|default:'output'}}

Consider the ideas and patterns expressed in _this_ request as good practices to append to the end of the generated recipe's generation prompt.


=== File: recipes/recipe_creator/prompts/sample_recipe_idea.md ===
## Goal

Create a new recipe for analyzing a codebase from a file roll-up, named `analyze_codebase.json`.

## How

### Input context variables

- `input`: [Required] The file path to the codebase roll-up file(s).
- `model`: [Optional] The model to use for generating the recipe. Defaults to `openai/o3-mini`.
- `output_root`: [Optional] The root directory for saving the generated recipe file. Defaults to `output`.

### Steps

1. Start with read of the codebase roll-up file(s) (`input` context variable).

2. Use the LLM (default set to use `openai/o3-mini`) to generate the analysis:

```markdown
Anayze the codebase from the following roll-up file(s):

- Codebase Roll-up: {{codebase_rollup}}

Save the generated analysis as `<project_name>_analysis.md`.
```

3. Save the generated file.

- The root should be set to value of `output_root` context variable, or `output` if not specified.


