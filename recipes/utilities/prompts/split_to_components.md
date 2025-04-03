recipe_idea:
Create a new JSON receipe file for recipe executor that will all me to use read_files to load a breakdown analysis of a large project that is passed in via a context key of `input`. The default value should be an error message indicating that the file is missing. Place the contents into the context as `project_analysis`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`

The next step should be a `read_files` step that loads any paths from the `files` context variable, storing content in a variable called `additional_files`. These files should be considered optional.

The next step should be a `generate` step that should _start with_:

```
Review the project analysis and break it down into individual components that contain detailed spefications for each component (split into file per component) that includes all of the details necessary to implement a version of that component based upon the `additional_files` and the philosophies and such outlined in these files I'm sharing with you. The `additional_files` may include some of component candidate specs that have already been created, in this case you can skip those ones. If there are no more components needed for the current break down, return a file named `completed_breakdown_report` with the final list of all of the component candidate specs. Default value for the target files for the components should be `<component_id>_candidate_spec.md` and the default model for this recipe should be `openai:o3-mini`.

- Recipe Idea: {{recipe_idea}}
{% if additional_files != '' %}
- Additional Files: {{additional_files}}
{% endif %}
- Context Files: {{context_files}}

Save one file per component, as `<component_id>_candidate_spec.md`.
```

Default model for this recipe should be: `openai:o3-mini`

The final step should be a `write_files` step that saves each of the generated recipe files to their requested file names. The `root` should be set to: {{output_root|default:'output'}}

Make sure to use double curly braces for all template variables in the recipe for use with liquid templating.

Consider the ideas and patterns expressed in _this_ request as good practices to append to the end of the generated recipe's generation prompt.

save this recipe as: split_to_components.json
