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
