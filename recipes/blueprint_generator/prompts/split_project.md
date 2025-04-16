## Goal

Load a breakdown analysis that contains detailed specifications for each component of a larger scope (project or component) and split it into individual components. The analysis should include all of the details necessary to implement a version of that component based upon the additional files and the philosophies outlined in the context files.

## Recipe filename

- `split_project.json`

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
# Project Splitting Task

## Goal

Split project into sub-components based on the provided breakdown analysis.

## Project Specification

<PROJECT_SPECIFICATION>
{{analysis_source}}
</PROJECT_SPECIFICATION>

## Breakdown Analysis

<BREAKDOWN_ANALYSIS>
{{input_file}}
</BREAKDOWN_ANALYSIS>

## Additional Files

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

## Task

Create detailed component specifications for each component based on the breakdown analysis and the additional files.

For each component, include the following:

- Component name and ID (from the breakdown analysis)
- Purpose and responsibilities
- Core requirements and functionalities
- API interfaces and data structures
- Dependencies (internal and external) and interactions with other components
- Implemtation considerations
- Error handling and logging specifics (not all, just non-standard)
- Testing and validation strategies

Each component specification should be comprehensive enough to allow for independent development and integration into the larger project by an independent developer that does not have access to the breakdown analysis or the additional files.

## Output format

- Each component specification should be saved in a separate file named `components/<component_id>/<component_id>_candidate_spec.md`.
- The component ID should be derived from the breakdown analysis.
```

6. Save each of the generated specification files to their requested file names. The `root` should be set to: {{output_root|default:'output'}}

7. Pass the generated files to another LLM step to create a components manifest file:

```markdown
# Components Manifest Creation Task

## Goal

Create a components manifest file that lists all of the generated component specifications.

## Component Specifications

<COMPONENT_SPECIFICATIONS>
{{generated_files}}
</COMPONENT_SPECIFICATIONS>

## Output format

- Create a JSON array of objects, each representing a component.
- Each object should include the following fields:

  - `component_id`: The ID of the component.
  - `component_name`: The name of the component.
  - `spec_file_path`: The file path to the component specification.
  - `description`: A brief description of the component's purpose and responsibilities.
  - `dependencies`: A list of internal and external dependencies, just the IDs.

- The JSON array should be saved as `components_manifest.json` (no path).
```

8. Save the components manifest file to the `output_root` directory.
