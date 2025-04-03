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
