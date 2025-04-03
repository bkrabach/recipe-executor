Goal:
Create a new JSON recipe file in the current folder. It should be named `create_recipe.json`.

How:
The recipe should use the `read_files` step to load a file that contains a request for a recipe to be created, obtaining the path value dynamically from the `input` context key. The default value should be an error message indicating that the file is missing. The loaded content should be stored in a variable called `recipe_idea`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- `ai_context/generated/recipe_executor_code_files.md`
- `ai_context/generated/recipe_executor_recipe_files.md`

The next step should be a `read_files` step that loads any paths from the `files` context variable, storing content in a variable called `additional_files`. These files should be considered optional.

The next step should be a `generate` step that should _start with_:

```
Create a new recipe file based on the following content:
- Recipe Idea: {{recipe_idea}}
- Context Files: {{context_files}}
{% if additional_files != '' %}
- Additional Files: {{additional_files}}
{% endif %}

Save the generated recipe file as {{target_file|default:'generated_recipe.json'}}, unless the `target_file` is set to a different value in the recipe_idea.
```

Default model for this recipe should be: `openai:o3-mini`

The final step should be a `write_files` step that saves the generated recipe file to the specified target file. The `root` should be set to: {{output_root|default:'output'}}

Make sure to use double curly braces for all template variables in the recipe for use with liquid templating.

Consider the ideas and patterns expressed in _this_ request as good practices to append to the end of the generated recipe's generation prompt.
