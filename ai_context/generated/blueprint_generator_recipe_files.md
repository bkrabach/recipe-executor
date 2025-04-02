=== File: recipes/blueprint_generator/build_blueprint.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{candidate_spec_path}}",
      "artifact": "candidate_spec"
    },
    {
      "type": "read_file",
      "path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
      "artifact": "component_docs_spec_guide"
    },
    {
      "type": "read_file",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "read_file",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer analyzing a candidate specification. Extract key information needed for component generation.\n\nCandidate Specification:\n{{candidate_spec}}\n\nExtract these fields only if not already provided:\n- component_id: {{component_id|default:''}}\n- component_name: {{component_name|default:''}}\n- module_path: {{module_path|default:''}}\n- component_type: {{component_type|default:''}}\n- key_dependencies: {{key_dependencies|default:''}}\n- related_docs: {{related_docs|default:''}}\n\nIf component_name is not provided and not in the spec, derive a clean title-case name from component_id.\n\nFor related_docs, identify any documentation files this component might need based on its dependencies, like 'context_docs', 'utils_docs', etc.\n\nProvide a JSON object with these fields, using reasonable defaults when information is not clear.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "extracted_info"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/blueprint_generator/recipes/create_package.json",
      "context_overrides": {
        "candidate_spec": "{{candidate_spec}}",
        "component_id": "{{component_id|default:extracted_info.component_id}}",
        "component_name": "{{component_name|default:extracted_info.component_name}}",
        "module_path": "{{module_path|default:extracted_info.module_path}}",
        "component_type": "{{component_type|default:extracted_info.component_type}}",
        "key_dependencies": "{{key_dependencies|default:extracted_info.key_dependencies}}",
        "related_docs": "{{related_docs|default:extracted_info.related_docs}}",
        "target_project": "{{target_project|default:''}}",
        "component_path": "{{component_path|default:''}}",
        "output_root": "{{output_root|default:'output'}}",
        "project_recipe_path": "recipes/{{target_project}}"
      }
    }
  ]
}


=== File: recipes/blueprint_generator/evaluate_candidate_spec.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{candidate_spec_path}}",
      "artifact": "candidate_spec"
    },
    {
      "type": "read_file",
      "path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
      "artifact": "component_docs_spec_guide"
    },
    {
      "type": "read_file",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "read_file",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer evaluating a candidate component specification to determine if it has enough context for effective implementation. You'll analyze the candidate specification and identify any areas that need clarification or additional information.\n\nCandidate Specification:\n{{candidate_spec}}\n\nUse the following guides as your evaluation criteria:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nPerform a systematic evaluation of the candidate specification with these steps:\n\n1. Identify the component name and type (if possible)\n2. Determine if a clear purpose statement exists\n3. Check if core requirements are well-defined and specific\n4. Assess if implementation considerations are provided\n5. Evaluate whether component dependencies are properly identified\n6. Check if error handling approaches are specified\n7. Look for any information about future considerations\n\nFor each aspect, provide:\n- A score from 1-5 (1=Missing/Insufficient, 5=Excellent)\n- Brief explanation of the score\n- Specific clarification questions if the score is 3 or lower\n\nFormat your response with these sections:\n1. Overall Assessment - Brief overview with readiness determination\n2. Scoring Summary - Table with scores for each aspect\n3. Detailed Analysis - Detailed assessment of each aspect with clarification questions\n4. Improvement Recommendations - List of questions to improve the specification\n\nBe constructive but thorough in your assessment.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "evaluation_result"
    },
    {
      "type": "generate",
      "prompt": "Format the specification evaluation as a proper markdown file with informative title and sections.\n\nEvaluation Result:\n{{evaluation_result}}\n\nFormat your response as a FileGenerationResult with a single file. The file name should include the component name if it could be identified from the specification, otherwise use 'component'.\n\nIf the evaluation determined that the specification needs significant clarification, suffix the file name with '_needs_clarification.md'. If the specification was deemed sufficient, suffix the file name with '_evaluation_summary.md'. Example: 'llm_component_evaluation_summary.md'.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "formatted_evaluation"
    },
    {
      "type": "write_files",
      "artifact": "formatted_evaluation",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/blueprint_generator/examples/README.md ===
# Component Blueprint Generator Examples

This directory contains example candidate specifications that can be used to test and demonstrate the Component Blueprint Generator system.

## Auth Component Example

The `auth_candidate_spec.md` file provides a sample candidate specification for an authentication component that integrates with Auth0 in production and provides a mock implementation for development environments.

### Using the Example

#### 1. Evaluate the Candidate Specification

First, evaluate the candidate specification to check for completeness and identify areas that need clarification:

```bash
python recipe_executor/main.py recipes/blueprint_generator/evaluate_candidate_spec.json \
  --context candidate_spec_path=recipes/blueprint_generator/examples/auth_candidate_spec.md \
  --context component_id=auth \
  --context output_root=output/blueprints
```

**NOTE**: If you wish to use a different model for evaluation, you can specify it in the command line by passing the `model` context parameter and value. For example, to use the `azure:o3-mini` model:

```bash
python recipe_executor/main.py recipes/blueprint_generator/evaluate_candidate_spec.json \
  --context candidate_spec_path=recipes/blueprint_generator/examples/auth_candidate_spec.md \
  --context component_id=auth \
  --context output_root=output/blueprints \
  --context model="azure:o3-mini"
```

This will generate an evaluation report in the `output` directory, which will highlight areas where the specification is strong and where it needs improvement.

#### 2. Generate Clarification Questions

If the evaluation indicates that the specification needs improvement, generate specific clarification questions:

```bash
python recipe_executor/main.py recipes/blueprint_generator/generate_clarification_questions.json \
  --context candidate_spec_path=recipes/blueprint_generator/examples/auth_candidate_spec.md \
  --context component_id=auth \
  --context output_root=output/blueprints
```

This will create a structured document with targeted questions organized by category that can help improve the specification.

#### 3. Generate the Complete Blueprint

Once you've reviewed the evaluation and potentially improved the specification based on the clarification questions, generate the complete component blueprint:

```bash
python recipe_executor/main.py recipes/blueprint_generator/build_blueprint.json \
  --context candidate_spec_path=recipes/blueprint_generator/examples/auth_candidate_spec.md \
  --context component_id=auth \
  --context component_name="Authentication" \
  --context target_project=example_project \
  --context output_root=output/blueprints
```

**Expected Outputs**

After running the full workflow, you should find these files in the `output` directory:

1. **Evaluation Report**: `auth_evaluation_summary.md` or `auth_needs_clarification.md`
2. **Clarification Questions**: `auth_clarification_questions.md`
3. **Blueprint Files**:
   - `example_project/components/auth` - All the files needed to drop into your project recipe `components` directory
     - `example_project/components/auth/auth_spec.md`
     - `example_project/components/auth/auth_docs.md`
     - `example_project/components/auth/auth_create.json`
     - `example_project/components/auth/auth_edit.json`
   - `example_project/reports/auth_blueprint_summary.md` - Summary of the generated blueprint

**Next Steps**

1. Review the evaluation and clarification questions
2. Improve the candidate specification based on the feedback
3. Regenerate the blueprint with the improved specification
4. Use the generated `authentication_create.json` recipe to implement the actual component:

#### 4. Implementing the Component Using Generated Files

After generating the blueprint, use the files to implement the component:

```bash
# First, create the component using the generated recipe
python recipe_executor/main.py output/example_project/components/auth/auth_create.json \
  --context output_root=src
```

This command will:

- Use the documentation from `output/example_project/components/auth/auth_docs.md` for guidance
- Read the formal specification from `output/example_project/components/auth/auth_spec.md`
- Generate implementation code for both Auth0 and mock authentication
- Write the files to the appropriate locations in your project
- Create all necessary classes, functions, and utilities defined in the spec

The implementation will include:

- FastAPI middleware for authentication
- JWT token verification for Auth0
- Mock authentication service for development
- User information extraction from tokens
- Role-based access control utilities
- Configuration management with environment variables
- Proper error handling and logging

To test the implementation, follow the examples provided in the documentation file. If you need to make changes to the implementation later, use the edit recipe:

```bash
python recipe_executor/main.py output/example_project/components/auth/auth_edit.json \
  --context output_root=src
```

## Creating Your Own Examples

To create your own example candidate specifications:

1. Create a markdown file with your component specification
2. Place it in this examples directory
3. Follow the same workflow as described above, updating the paths as needed

The more detail you provide in your candidate specification, the more complete the generated blueprint will be. However, the system is designed to help identify gaps, so even incomplete specifications can be a good starting point.


=== File: recipes/blueprint_generator/examples/auth_candidate_spec.md ===
# Authentication Component Specification

## Overview

We need an authentication component for our FastAPI service that will handle user authentication using Auth0 in production environments. It should also provide a mock implementation for development and testing environments that simulates the same behavior without requiring an actual Auth0 connection.

## Features

- Authenticate users via Auth0 in production
- Provide a mock authentication service for development
- Verify JWT tokens
- Extract user information from tokens
- Support role-based access control

## Implementation Details

The component should provide FastAPI middleware and dependency functions for protecting routes. It should verify tokens from Auth0 and extract user claims. The mock implementation should generate tokens that have the same structure and can be verified locally.

We should support different roles like "admin", "user", etc. and have decorators or utilities to check permissions.

## Dependencies

- FastAPI
- Auth0 Python SDK
- PyJWT

## Configuration

The component should be configurable via environment variables:

- AUTH_MODE: "auth0" or "mock"
- AUTH0_DOMAIN
- AUTH0_API_AUDIENCE
- AUTH0_ALGORITHMS

## Expected API

```python
# Example usage
from auth import requires_auth, get_user, requires_role

@app.get("/protected")
@requires_auth
def protected_route():
    user = get_user()
    return {"message": f"Hello, {user.name}"}

@app.get("/admin")
@requires_role("admin")
def admin_route():
    return {"message": "Admin access granted"}
```


=== File: recipes/blueprint_generator/generate_clarification_questions.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{candidate_spec_path}}",
      "artifact": "candidate_spec"
    },
    {
      "type": "read_file",
      "path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
      "artifact": "component_docs_spec_guide"
    },
    {
      "type": "read_file",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "read_file",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer helping to improve a candidate component specification by generating clarification questions. Based on the candidate specification and understanding of effective component design, create a comprehensive set of questions that would help make the specification complete and implementable.\n\nCandidate Specification:\n{{candidate_spec}}\n\nUse the following guides to understand what information is needed in an effective specification:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nGenerate clarification questions organized into these categories:\n\n1. Purpose and Scope\n- Questions about the component's primary responsibility\n- Questions about boundaries and what's out of scope\n- Questions about the problem being solved\n\n2. Functional Requirements\n- Questions about specific capabilities needed\n- Questions about user/system interactions\n- Questions about expected inputs and outputs\n\n3. Technical Requirements\n- Questions about implementation constraints\n- Questions about performance requirements\n- Questions about security considerations\n\n4. Integration and Dependencies\n- Questions about how it interacts with other components\n- Questions about external dependencies\n- Questions about interface requirements\n\n5. Error Handling and Edge Cases\n- Questions about failure scenarios\n- Questions about edge cases\n- Questions about recovery mechanisms\n\nIn each category, provide 3-5 specific questions that would help improve the specification. Make the questions clear, specific, and directly relevant to the candidate specification. For each question, briefly explain why this information is important for implementation.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "clarification_questions"
    },
    {
      "type": "generate",
      "prompt": "Format the clarification questions as a structured markdown document that can be shared with stakeholders.\n\nClarification Questions:\n{{clarification_questions}}\n\nCandidate Specification:\n{{candidate_spec}}\n\nCreate a document with these sections:\n1. Introduction - Brief explanation of the purpose of this document and the component being specified\n2. Current Specification - A summary of the current candidate specification\n3. Key Areas Needing Clarification - Overview of the major gaps identified\n4. Detailed Questions - The clarification questions organized by category\n5. Next Steps - Guidance on how to use these questions to improve the specification\n\nFormat your response as a FileGenerationResult with a single file named '<component_id>_component_clarification_questions.md' (use the component name if it can be identified).",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "formatted_questions"
    },
    {
      "type": "write_files",
      "artifact": "formatted_questions",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/blueprint_generator/includes/create_recipe_template.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/{{component_id}}/{{component_id}}_spec.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/{{component_id}}/{{component_id}}_docs.md",
      "artifact": "usage_docs"
    },
    {
      "type": "read_file",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "read_file",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "{{model|default:'openai:o3-mini'}}",
        "output_root": "{{output_root|default:'.'}}",
        "component_id": "{{component_id}}",
        "output_path": "{{target_project}}/{{component_id}}",
        "language": "{{language|default:'python'}}",
        "spec": "{{spec}}",
        "usage_docs": "{{usage_docs}}",
        "additional_content": "<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% if related_docs %}<RELATED_DOCS>\n{{related_docs}}\n</RELATED_DOCS>{% endif %}"
      }
    }
  ]
}


=== File: recipes/blueprint_generator/includes/docs_template.md ===
# {component_name} Component Usage

## Importing

<!-- Show how to import the component. Keep it simple and direct. -->

```python
from {package}.{module} import {component_name}
```

## Initialization

<!-- Document initialization with all relevant parameters. Include docstring and examples. -->

```python
def __init__(self, {param1}: {type1}, {param2}: {type2} = {default2}, ...) -> None:
    """
    Initialize the {component_name} with the specified parameters.

    Args:
        {param1} ({type1}): {param1_description}
        {param2} ({type2}, optional): {param2_description}. Defaults to {default2}.
        ...
    """
```

Examples:

```python
# Basic initialization
{component_instance} = {component_name}({basic_params})

# With optional parameters
{component_instance} = {component_name}({full_params})

# Other common initialization patterns
{component_instance} = {component_name}({alt_params})
```

## Core API

<!-- Document each public method with signature, description, parameters, return values, exceptions, and examples. -->

### {method1_name}

```python
def {method1_name}(self, {param1}: {type1}, {param2}: {type2} = {default2}, ...) -> {return_type1}:
    """
    {method1_description}

    Args:
        {param1} ({type1}): {param1_description}
        {param2} ({type2}, optional): {param2_description}. Defaults to {default2}.
        ...

    Returns:
        {return_type1}: {return_description1}

    Raises:
        {exception1}: {exception1_description}
        {exception2}: {exception2_description}
    """
```

Example:

```python
# Usage example
result = {component_instance}.{method1_name}({example_params1})
```

### {method2_name}

```python
def {method2_name}(self, {param1}: {type1}, ...) -> {return_type2}:
    """
    {method2_description}

    Args:
        {param1} ({type1}): {param1_description}
        ...

    Returns:
        {return_type2}: {return_description2}

    Raises:
        {exception1}: {exception1_description}
    """
```

Example:

```python
# Usage example
result = {component_instance}.{method2_name}({example_params2})
```

## Common Usage Patterns

<!-- Provide examples of typical usage scenarios. Include code samples that demonstrate:
     - Basic usage
     - Advanced/complex usage
     - Integration with common workflows -->

### {usage_pattern1_name}

```python
# Example of {usage_pattern1_name}
{usage_pattern1_code}
```

### {usage_pattern2_name}

```python
# Example of {usage_pattern2_name}
{usage_pattern2_code}
```

## Integration with Other Components

<!-- Show how this component works with other components in the system.
     Include real-world examples of component combinations. -->

```python
# Example of integration with {related_component1}
{component_instance} = {component_name}({params})
{related_instance} = {related_component1}({related_params})

# Integration code
{integration_code}
```

## Important Notes

<!-- Highlight critical information users need to know, such as:
     - Performance considerations
     - Thread safety concerns
     - Common pitfalls to avoid
     - Best practices -->

- {important_note1}
- {important_note2}
- {important_note3}


=== File: recipes/blueprint_generator/includes/edit_recipe_template.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{target_project}}/components/{{component_id}}/{{component_id}}.py",
      "artifact": "existing_code"
    },
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/components/{{component_id}}/{{component_id}}_spec.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/components/{{component_id}}/{{component_id}}_docs.md",
      "artifact": "usage_docs"
    },
    {
      "type": "read_file",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "read_file",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "{{model|default:'openai:o3-mini'}}",
        "output_root": "{{output_root|default:'.'}}",
        "component_id": "{{component_id}}",
        "output_path": "{{target_project}}/{{component_id}}",
        "language": "{{language|default:'python'}}",
        "spec": "{{spec}}",
        "usage_docs": "{{usage_docs}}",
        "existing_code": "{{existing_code}}",
        "additional_content": "<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% if related_docs %}<RELATED_DOCS>\n{{related_docs}}\n</RELATED_DOCS>{% endif %}"
      }
    }
  ]
}


=== File: recipes/blueprint_generator/includes/spec_template.md ===
# {component_name} Component Specification

## Purpose

<!-- Provide 2-3 clear sentences that describe what this component does and its role in the system.
Focus on responsibilities, not implementation details. -->

{purpose_statement}

## Core Requirements

<!-- List 3-8 essential capabilities this component must provide.
Each bullet should be specific, verifiable, and focused on what, not how.
Bullets should be collectively exhaustive, covering all needed functionality. -->

- {requirement_1}
- {requirement_2}
- {requirement_3}
- ...

## Implementation {implementation_section_type}

<!-- Choose the appropriate section type:
"Implementation Considerations" for general guidance
"Implementation Details" for specific code examples
"Implementation Hints" for targeted tips -->
<!-- Provide 3-7 bullet points of guidance on implementation approach.
Suggest approaches without dictating exact implementations.
Highlight constraints, challenges, or trade-offs. -->

- {consideration_1}
- {consideration_2}
- {consideration_3}
- ...

## Component Dependencies

<!-- For each dependency, clearly indicate whether it's required or optional,
and explain how this component uses or interacts with it. -->

### Internal Components

<!-- List other components in this system that this component depends on. -->

- **{internal_component_1}** - (Required) {description_1}
- **{internal_component_2}** - (Optional) {description_2}
<!-- Or "None" if no internal dependencies -->

### External Libraries

<!-- List external libraries or frameworks this component needs. -->

- **{external_library_1}** - (Required) {description_1}
- **{external_library_2}** - (Optional) {description_2}
<!-- Or "None" if no external dependencies -->

### Configuration Dependencies

<!-- List environment variables, config files, or settings this component requires. -->

- **{config_dependency_1}** - (Required) {description_1}
- **{config_dependency_2}** - (Optional) {description_2}
<!-- Or "None" if no configuration dependencies -->

## Output Files

<!-- List each file that should be generated from this spec.
Include full relative path and brief description of each file's purpose. -->

- `{file_path_1}` - {file_description_1}
- `{file_path_2}` - {file_description_2}

## Logging

<!-- Specify log levels and messages this component should produce.
If component doesn't require logging, explicitly state "None". -->

- Debug: {debug_logging_requirements}
- Info: {info_logging_requirements}
- Error: {error_logging_requirements}
<!-- Or "None" if no logging requirements -->

## Error Handling

<!-- Describe expected errors and how they should be handled.
Include validation requirements and error reporting mechanisms. -->

- {error_handling_1}
- {error_handling_2}
- {error_handling_3}

## Future Considerations

<!-- List potential future enhancements or extensions.
If none are anticipated, explicitly state "None". -->

- {future_consideration_1}
- {future_consideration_2}
- {future_consideration_3}
<!-- Or "None" if no future considerations -->

## Dependency Integration Considerations

<!-- Provide details on integrating with complex dependencies.
If no special integration considerations exist, explicitly state "None". -->

### {dependency_name}

{integration_details}

<!-- Or simply "None" if no integration considerations -->


=== File: recipes/blueprint_generator/recipes/create_docs.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/blueprint_generator/includes/docs_template.md",
      "artifact": "docs_template"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer creating component documentation. Based on the component specification and information, create comprehensive usage documentation following the template structure.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nModule Path: {{module_path|default:''}}\nComponent Type: {{component_type|default:''}}\n\nDocumentation Template:\n{{docs_template}}\n\nUse the following guides for context:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\nIMPORTANT GUIDELINES:\n1. Create complete, detailed documentation for the component\n2. Include clear examples, method documentation, and integration guidance\n3. Within the documentation, use the component_id (\"{{component_id}}\") as the base name for all classes, modules, and file references unless explicitly overridden in the candidate spec\n4. Format your response as a FileGenerationResult with a single file named \"{{component_id}}_docs.md\"\n\nDo not include the component name or other text in the filename - it must be exactly \"{{component_id}}_docs.md\".",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_doc"
    },
    {
      "type": "write_files",
      "artifact": "generated_doc",
      "root": "{{output_root|default:'output'}}/{{target_project}}/components/{{component_id}}"
    }
  ]
}


=== File: recipes/blueprint_generator/recipes/create_package.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/blueprint_generator/recipes/create_docs.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/blueprint_generator/recipes/create_spec.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/blueprint_generator/recipes/create_recipes.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/blueprint_generator/recipes/finalize_blueprint.json"
    }
  ]
}


=== File: recipes/blueprint_generator/recipes/create_recipes.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/blueprint_generator/includes/create_recipe_template.json",
      "artifact": "create_recipe_template"
    },
    {
      "type": "read_file",
      "path": "recipes/blueprint_generator/includes/edit_recipe_template.json",
      "artifact": "edit_recipe_template"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer creating recipe files for component generation and editing. Based on the component specification and template recipes, create the final recipe files.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Documentation:\n{{generated_doc}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nTarget Project: {{target_project}}\nProject Recipe Path: {{project_recipe_path}}\n\nCreate Recipe Template:\n{{create_recipe_template}}\n\nEdit Recipe Template:\n{{edit_recipe_template}}\n\n# IMPORTANT GUIDELINES\n\n1. Use the templates as your starting point and maintain their overall structure\n\n2. For additional file includes and related docs:\n   - Analyze the component specification to identify related components or documentation it might need\n   - Include read_file steps for any relevant documents (like utils_docs for a component that uses utilities)\n   - Format additional content using XML-style tags (like <CONTEXT_DOCS>content</CONTEXT_DOCS>)\n   - Follow the pattern seen in executor_create.json, llm_create.json, etc.\n\n3. For context overrides:\n   - Keep all existing context variables provided in the template\n   - Add component-specific variables as needed\n   - Use the pattern: \"additional_content\": \"<TAG_NAME>\\n{{artifact_name}}\\n</TAG_NAME>\"\n\n4. Naming and paths:\n   - Use exactly '{{component_id}}_create.json' and '{{component_id}}_edit.json' for filenames\n   - Ensure all paths use correct variables: {{project_recipe_path}}, {{component_id}}, etc.\n\nFormat your response as a FileGenerationResult with two files:\n1. '{{component_id}}_create.json' - The create recipe\n2. '{{component_id}}_edit.json' - The edit recipe",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "recipe_files"
    },
    {
      "type": "write_files",
      "artifact": "recipe_files",
      "root": "{{output_root|default:'output'}}/{{target_project}}/components/{{component_id}}"
    }
  ]
}


=== File: recipes/blueprint_generator/recipes/create_spec.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/blueprint_generator/includes/spec_template.md",
      "artifact": "spec_template"
    },
    {
      "type": "read_file",
      "path": "{{output_root|default:'output'}}/{{target_project}}/components/{{component_id}}/{{component_id}}_docs.md",
      "artifact": "generated_docs",
      "optional": true
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer creating a formal component specification. Based on the candidate specification and component information, create a detailed specification document following the template structure.\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nModule Path: {{module_path|default:''}}\nComponent Type: {{component_type|default:''}}\nKey Dependencies: {{key_dependencies|default:''}}\n\nSpecification Template:\n{{spec_template}}\n\nUse the following guides for context:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{component_docs_spec_guide}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nIMPORTANT GUIDELINES:\n1. Create a complete, detailed specification for the component\n2. Within the specification, use the component_id (\"{{component_id}}\") as the base name for all classes, modules, and file references unless explicitly overridden in the candidate spec\n3. Format your response as a FileGenerationResult with a single file named \"{{component_id}}_spec.md\"\n\nDo not include the component name or other text in the filename - it must be exactly \"{{component_id}}_spec.md\".{% if generated_docs %}\n\nHere are the component docs so that you can see what is already being covered:\n<COMPONENT_DOCS>\n{{generated_docs}}\n</COMPONENT_DOCS>{% endif %}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_spec"
    },
    {
      "type": "write_files",
      "artifact": "generated_spec",
      "root": "{{output_root|default:'output'}}/{{target_project}}/components/{{component_id}}"
    }
  ]
}


=== File: recipes/blueprint_generator/recipes/finalize_blueprint.json ===
{
  "steps": [
    {
      "type": "generate",
      "prompt": "You are an expert developer finalizing a component blueprint. Review all the generated artifacts and create a summary report that describes what has been created and how to use these artifacts to generate the component.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Documentation:\n{{generated_doc}}\n\nComponent Recipe Files:\n{{recipe_files}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nTarget Project: {{target_project}}\n\nCreate a summary report as a properly formatted markdown file with the title '{{component_id}}_blueprint_summary.md' that includes:\n1. An overview of the component\n2. A list of all generated files with their locations\n3. Instructions for using the recipes to generate the component\n4. Any special considerations or next steps\n\nThis report should serve as a guide for someone who wants to use these blueprint files to generate the actual component code.\n\nFormat your response as a FileGenerationResult with a single file named '{{component_id}}_blueprint_summary.md'.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "formatted_summary"
    },
    {
      "type": "write_files",
      "artifact": "formatted_summary",
      "root": "{{output_root|default:'output'}}/{{target_project}}/reports"
    }
  ]
}


