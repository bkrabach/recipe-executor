# Generate Customized Project Specification Recipe

## Goal

Create a custom, project-specific recipe file to call the system project specification recipe - based on a high-level project idea.

## Task

- Create a new recipe JSON file, `recipes/call_generate_candidate_spec.json`, to be used to call the system project specification recipe, `recipes/blueprint_generator/recipes/generate_project_spec.json`.
- Extract file paths from the project idea two different categories:
  - **Context Files**: Files that provide context for the project idea, such as vision documents or design philosophies.
  - **Reference Files**: Files that are referenced in the project idea, such as library documentation or code files.

## Output Format

- The recipe file should be in JSON format.
- Save the recipe file as `recipes/call_generate_candidate_spec.json`, which will be used to generate a project-specific recipe file for calling the actual generate project specification step.

**Template for the recipe file:**

<RECIPE_TEMPLATE>>

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/blueprint_generator/recipes/generate_project_spec.json",
      "context_overrides": {
        "input": "{{project_idea}}",
        "context_files": ** INCLUDE COMMA-SEPARATED STRING OF CONTEXT FILE PATHS WITHOUT SPACES HERE **,
        "reference_files": ** INCLUDE COMMA-SEPARATED STRING OF REFERENCE FILE PATHS WITHOUT SPACES HERE **,
        "output_root": "{{output_root}}",
        "model": "{{model}}"
      }
    }
  ]
}
```

</RECIPE_TEMPLATE>
