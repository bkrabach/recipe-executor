recipe_idea:
Create a new JSON receipe file for recipe executor that will all me to use read_files to load a high-level project definition file that is passed in via a context key of `input`. The default value should be an error message indicating that the file is missing.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`

The next step should be a `read_files` step that loads any paths from the `files` context variable, storing content in a variable called `additional_files`. These files should be considered optional.

Pass everything into a generate step that will create an analysis of the project and break it down into a list of components that should be considered the "right size" per component based upon the philosophies and such outlined in these files I'm sharing with you. Default value for the target file for the analysis should be `project_component_breakdown_analysis.md` and the default model for this recipe should be `openai:o3-mini`.

The final step should be a write_file step that saves the generated artifact. The root should be set to: {{output_root|default:'output'}}

save this recipe as: project_split_analysis.json
