## Goal

Load a breakdown analysis that contains detailed specifications for each component of a larger scope (project or component) and split it into individual components. The analysis should include all of the details necessary to implement a version of that component based upon the additional files and the philosophies outlined in the context files.

## Recipe filename

- `split_to_components.json`

## How

### Input context variables

- `input`: [Required] The file path to the breakdown analysis file.
- `analysis_source`: [required] The file path to the source file for the analysis.
- `files`: [Optional] A list of additional files that were used to create the breakdown analysis.
- `model`: [Optional] The model to use for generate steps.
  - Default: `openai/o3-mini`
- `output_root`: [Optional] The root directory for saving output files.
  - Default: `output`

### Steps

1. Start with read of the breakdown analysis file (`input` context variable).

2. Load the source file for the analysis (`analysis_source` context variable) into the context as `analysis_source`.

3. Always load the following files into context as `guidance_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`

4. Load any other files that are passed in via the `files` context variable. These files should be considered optional and stored in a variable called `additional_files`.

5. Use the LLM to generate individual component specifications:

```markdown
Review the project analysis and break it down into individual components that contain detailed specifications for each component (split into file per component) that includes all of the details necessary to implement a version of that component based upon the `additional_files` and the philosophies and such outlined in these files I'm sharing with you.

- Breakdown Analysis:
  <BREAKDOWN_ANALYSIS>
  {{input_file}}
  </BREAKDOWN_ANALYSIS>

- Analysis Source:
  <ANALYSIS_SOURCE>
  {{analysis_source}}
  </ANALYSIS_SOURCE>

{% if additional_files != '' %}

- Additional Content:
  <ADDITIONAL_CONTENT>
  {{additional_files}}
  </ADDITIONAL_CONTENT>
  {% endif %}

- Guidance Philosophies (how to make decisions):
  <GUIDANCE_PHILOSOPHY>
  {{guidance_files}}
  </GUIDANCE_PHILOSOPHY>

The `additional_files` may include some of component candidate specs that have already been created, in this case you can skip those ones.

If there are no more components needed for the current break down, return a file named `completed_breakdown_report` with the final list of all of the component candidate specs.

For components, save one file per component, as `components/<component_id>/<component_id>_candidate_spec.md`.
```

6. The final step should be a `write_files` step that saves each of the generated recipe files to their requested file names. The `root` should be set to: {{output_root|default:'output'}}
