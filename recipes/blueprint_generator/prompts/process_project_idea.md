## Goal

Take a high-level project idea and any additional context and create more detailed project specification and recipe file to kick off the blueprint generation process.

## Recipe filename

- `process_project_idea.json`

## How

### Input context variables

- `project_idea`: [Required] The file path to the project idea file.
- `output_root`: [Optional] The root directory for saving output files.
  - Default: `output`
- `model`: [Optional] The model to be used for generating the project specification.
  - Default: `openai/gpt-4o`

### Steps

1. Load the project idea file (`project_idea` context variable) into context as `project_idea_content`.

2. Use the LLM to extract a list of context and reference files from the project idea:

```markdown
# Task

Extract a list of context and reference files from the project idea:

- Project Idea:
  <PROJECT_IDEA>
  {{project_idea_content}}
  </PROJECT_IDEA>
- Context Files: These files provide context for the project idea, such as vision documents or design philosophies.
- Reference Files: These files are referenced in the project idea, such as library documentation or code files.

# Output Format

- The output should be a JSON object with two keys:
  - `context_files`: A list of file paths for context files.
  - `reference_files`: A list of file paths for reference files.
```

3. Call the `recipes/blueprint_generator/recipes/generate_project_spec.json` recipe with the following parameters:
   - `project_idea`: The project idea file path.
   - `context_files`: The list of context files extracted from the project idea.
   - `reference_files`: The list of reference files extracted from the project idea.
   - `output_root`: The output root directory.
   - `model`: The model to be used for generating the project specification.
