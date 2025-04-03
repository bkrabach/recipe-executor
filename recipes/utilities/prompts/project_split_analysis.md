recipe_idea: `project_split_analysis.json`

Start wtih upload of a **required** high-level project definition file. This path is passed in via a context key of `input`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`

After that, load any other files that are passed in via the `files` context variable. These files should be considered optional and stored in a variable called `additional_files`.

Use the LLM (default set to use `openai:o3-mini`) to generate a project breakdown analysis:

```markdown
Create a new project breakdown analysis based on the following content:

- Project Definition: {{input_file}}
- Context Files:
  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>
  {% if additional_files != '' %}
- Additional Files:
  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>
  {% endif %}

The project breakdown analysis should be:

- Based on the philosophies and such outlined in the context files.
- A breakdown of the project into smaller, manageable components.
- Complete, covering all required aspects of the project.
- Modular, allowing for easy implementation and testing of each component in isolation.
- Cohesive, ensuring that each component has a clear purpose and responsibility.
- Loosely coupled, minimizing dependencies between components.
- Testable, with clear guidelines for how to validate each component.
- Documented, with clear instructions for how to use and interact with each component.

For each component, the analysis should include:

- A description of the component's purpose and functionality.
- A brief overview of why this component is "right sized" and does not need to be broken down further.
- The contract for the component, including:
  - The inputs and outputs of the component.
  - The expected behavior of the component.
  - Any edge cases or special considerations for the component.
- How to test and validate the component.
- Any dependencies or interactions with other components.
- Any implmentation details or requirements such as example code, libraries, or frameworks to use.

Save this generated project breakdown analysis as `{{target_file|default:'project_component_breakdown_analysis.md'}}`, unless the `target_file` is set to a different value in the project definition.
```

The final step should be to save the generated file. The root should be set to value of `output_root` variable, defaulting to the `output` directory.
