=== File: recipes/component_blueprint_generator/build_blueprint.json ===
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
"artifact": "COMPONENT_DOCS_SPEC_GUIDE"
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
"recipe_path": "recipes/component_blueprint_generator/create.json",
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

=== File: recipes/component_blueprint_generator/create.json ===
{
"steps": [
{
"type": "read_file",
"path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
"artifact": "COMPONENT_DOCS_SPEC_GUIDE"
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
"recipe_path": "recipes/component_blueprint_generator/recipes/create_spec.json"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/recipes/create_docs.json"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/recipes/create_recipes.json"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/recipes/finalize_blueprint.json"
}
]
}

=== File: recipes/component_blueprint_generator/evaluate_candidate_spec.json ===
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
"artifact": "COMPONENT_DOCS_SPEC_GUIDE"
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
"prompt": "You are an expert developer evaluating a candidate component specification to determine if it has enough context for effective implementation. You'll analyze the candidate specification and identify any areas that need clarification or additional information.\n\nCandidate Specification:\n{{candidate_spec}}\n\nUse the following guides as your evaluation criteria:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{COMPONENT_DOCS_SPEC_GUIDE}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nPerform a systematic evaluation of the candidate specification with these steps:\n\n1. Identify the component name and type (if possible)\n2. Determine if a clear purpose statement exists\n3. Check if core requirements are well-defined and specific\n4. Assess if implementation considerations are provided\n5. Evaluate whether component dependencies are properly identified\n6. Check if error handling approaches are specified\n7. Look for any information about future considerations\n\nFor each aspect, provide:\n- A score from 1-5 (1=Missing/Insufficient, 5=Excellent)\n- Brief explanation of the score\n- Specific clarification questions if the score is 3 or lower\n\nFormat your response with these sections:\n1. Overall Assessment - Brief overview with readiness determination\n2. Scoring Summary - Table with scores for each aspect\n3. Detailed Analysis - Detailed assessment of each aspect with clarification questions\n4. Improvement Recommendations - List of questions to improve the specification\n\nBe constructive but thorough in your assessment.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "evaluation_result"
},
{
"type": "generate",
"prompt": "Format the specification evaluation as a proper markdown file with informative title and sections.\n\nEvaluation Result:\n{{evaluation_result}}\n\nFormat your response as a FileGenerationResult with a single file. The file path should include the component name if it could be identified from the specification, otherwise use 'component'.\n\nIf the evaluation determined that the specification needs significant clarification, name the file 'clarification_questions.md'. If the specification was deemed sufficient, name the file 'evaluation_summary.md'.",
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

=== File: recipes/component_blueprint_generator/examples/README.md ===

# Component Blueprint Generator Examples

This directory contains example candidate specifications that can be used to test and demonstrate the Component Blueprint Generator system.

## Auth Component Example

The `auth_candidate_spec.md` file provides a sample candidate specification for an authentication component that integrates with Auth0 in production and provides a mock implementation for development environments.

### Using the Example

#### 1. Evaluate the Candidate Specification

First, evaluate the candidate specification to check for completeness and identify areas that need clarification:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/evaluate_candidate_spec.json \
  --context candidate_spec_path=recipes/component_blueprint_generator/examples/auth_candidate_spec.md \
  --context output_root=output
```

This will generate an evaluation report in the `output` directory, which will highlight areas where the specification is strong and where it needs improvement.

#### 2. Generate Clarification Questions

If the evaluation indicates that the specification needs improvement, generate specific clarification questions:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/generate_clarification_questions.json \
  --context candidate_spec_path=recipes/component_blueprint_generator/examples/auth_candidate_spec.md \
  --context output_root=output
```

This will create a structured document with targeted questions organized by category that can help improve the specification.

#### 3. Generate the Complete Blueprint

Once you've reviewed the evaluation and potentially improved the specification based on the clarification questions, generate the complete component blueprint:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/build_blueprint.json \
  --context candidate_spec_path=recipes/component_blueprint_generator/examples/auth_candidate_spec.md \
  --context component_id=auth \
  --context component_name="Authentication" \
  --context target_project=example_project \
  --context output_root=output
```

### Expected Outputs

After running the full workflow, you should find these files in the `output` directory:

1. **Evaluation Report**: `auth_evaluation_summary.md` or `clarification_questions.md`
2. **Clarification Questions**: `auth_specification_clarification_questions.md`
3. **Blueprint Files**:
   - `example_project/specs/auth.md` - Formal specification
   - `example_project/docs/auth.md` - Usage documentation
   - `example_project/recipes/auth_create.json` - Recipe for creating the component
   - `example_project/recipes/auth_edit.json` - Recipe for editing the component
   - `example_project/auth_blueprint_summary.md` - Summary of the generated blueprint

### Next Steps

1. Review the evaluation and clarification questions
2. Improve the candidate specification based on the feedback
3. Regenerate the blueprint with the improved specification
4. Use the generated `auth_create.json` recipe to implement the actual component:

```bash
python recipe_executor/main.py output/example_project/recipes/auth_create.json \
  --context output_root=src
```

#### 4. Implementing the Component Using Generated Files

After generating the blueprint, use the files to implement the component:

```bash
# First, create the component using the generated recipe
python recipe_executor/main.py output/example_project/recipes/auth_create.json \
  --context output_root=src
```

This command will:

- Read the formal specification from `output/example_project/specs/auth.md`
- Use the documentation from `output/example_project/docs/auth.md` for guidance
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
python recipe_executor/main.py output/example_project/recipes/auth_edit.json \
  --context output_root=src
```

## Creating Your Own Examples

To create your own example candidate specifications:

1. Create a markdown file with your component specification
2. Place it in this examples directory
3. Follow the same workflow as described above, updating the paths as needed

The more detail you provide in your candidate specification, the more complete the generated blueprint will be. However, the system is designed to help identify gaps, so even incomplete specifications can be a good starting point.

=== File: recipes/component_blueprint_generator/examples/auth_candidate_spec.md ===

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

=== File: recipes/component_blueprint_generator/generate_clarification_questions.json ===
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
"artifact": "COMPONENT_DOCS_SPEC_GUIDE"
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
"prompt": "You are an expert developer helping to improve a candidate component specification by generating clarification questions. Based on the candidate specification and understanding of effective component design, create a comprehensive set of questions that would help make the specification complete and implementable.\n\nCandidate Specification:\n{{candidate_spec}}\n\nUse the following guides to understand what information is needed in an effective specification:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{COMPONENT_DOCS_SPEC_GUIDE}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nGenerate clarification questions organized into these categories:\n\n1. Purpose and Scope\n- Questions about the component's primary responsibility\n- Questions about boundaries and what's out of scope\n- Questions about the problem being solved\n\n2. Functional Requirements\n- Questions about specific capabilities needed\n- Questions about user/system interactions\n- Questions about expected inputs and outputs\n\n3. Technical Requirements\n- Questions about implementation constraints\n- Questions about performance requirements\n- Questions about security considerations\n\n4. Integration and Dependencies\n- Questions about how it interacts with other components\n- Questions about external dependencies\n- Questions about interface requirements\n\n5. Error Handling and Edge Cases\n- Questions about failure scenarios\n- Questions about edge cases\n- Questions about recovery mechanisms\n\nIn each category, provide 3-5 specific questions that would help improve the specification. Make the questions clear, specific, and directly relevant to the candidate specification. For each question, briefly explain why this information is important for implementation.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "clarification_questions"
},
{
"type": "generate",
"prompt": "Format the clarification questions as a structured markdown document that can be shared with stakeholders.\n\nClarification Questions:\n{{clarification_questions}}\n\nCandidate Specification:\n{{candidate_spec}}\n\nCreate a document with these sections:\n1. Introduction - Brief explanation of the purpose of this document and the component being specified\n2. Current Specification - A summary of the current candidate specification\n3. Key Areas Needing Clarification - Overview of the major gaps identified\n4. Detailed Questions - The clarification questions organized by category\n5. Next Steps - Guidance on how to use these questions to improve the specification\n\nFormat your response as a FileGenerationResult with a single file named 'component_specification_clarification_questions.md' (or use the component name if it can be identified).",
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

=== File: recipes/component_blueprint_generator/includes/create_recipe_template.json ===
{
"steps": [
{
"type": "read_file",
"path": "{{project_recipe_path}}/specs/{{component_id}}.md",
"artifact": "spec"
},
{
"type": "read_file",
"path": "{{project_recipe_path}}/docs/{{component_id}}.md",
"artifact": "usage_docs",
"optional": true
},
{
"type": "read_file",
"path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
"artifact": "implementation_philosophy",
"optional": true
},
{
"type": "read_file",
"path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
"artifact": "modular_design_philosophy",
"optional": true
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

=== File: recipes/component_blueprint_generator/includes/docs_template.md ===

# {{component_name}} Component Usage

## Importing

```python
from {{module_path}} import {{component_name}}
```

## Initialization

[Description of initialization]

```python
# Example initialization
```

## Core API

### [Method/Function 1]

```python
def method_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    [Method description]

    Args:
        param1: [Parameter description]
        param2: [Parameter description]

    Returns:
        [Return value description]

    Raises:
        [Exception]: [Exception description]
    """
```

Example:

```python
# Usage example
```

### [Method/Function 2]

...

## Integration with Other Components

[Description of how this component interacts with others]

```python
# Integration example
```

## Important Notes

1. [Important note 1]
2. [Important note 2]
3. ...

=== File: recipes/component_blueprint_generator/includes/edit_recipe_template.json ===
{
"steps": [
{
"type": "read_file",
"path": "{{target_project}}/{{component_id}}.py",
"artifact": "existing_code",
"optional": true
},
{
"type": "read_file",
"path": "{{project_recipe_path}}/specs/{{component_id}}.md",
"artifact": "spec"
},
{
"type": "read_file",
"path": "{{project_recipe_path}}/docs/{{component_id}}.md",
"artifact": "usage_docs",
"optional": true
},
{
"type": "read_file",
"path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
"artifact": "implementation_philosophy",
"optional": true
},
{
"type": "read_file",
"path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
"artifact": "modular_design_philosophy",
"optional": true
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

=== File: recipes/component_blueprint_generator/includes/spec_template.md ===

# {{component_name}} Component Specification

## Purpose

[Brief description of the component's purpose and role in the system]

## Core Requirements

- [Requirement 1]
- [Requirement 2]
- [Requirement 3]
- ...

## Implementation Considerations

- [Implementation consideration 1]
- [Implementation consideration 2]
- [Implementation consideration 3]
- ...

## Component Dependencies

The {{component_name}} component depends on:

- [Dependency 1] - [Description of relationship]
- [Dependency 2] - [Description of relationship]
- ...

## Error Handling

- [Error handling approach 1]
- [Error handling approach 2]
- ...

## Future Considerations

- [Future consideration 1]
- [Future consideration 2]
- ...

=== File: recipes/component_blueprint_generator/recipes/create_docs.json ===
{
"steps": [
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/docs_template.md",
"artifact": "docs_template"
},
{
"type": "generate",
"prompt": "You are an expert developer creating component documentation. Based on the component specification and information, create comprehensive usage documentation following the template structure.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nModule Path: {{module_path|default:''}}\nComponent Type: {{component_type|default:''}}\n\nDocumentation Template:\n{{docs_template}}\n\nUse the following guides for context:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{COMPONENT_DOCS_SPEC_GUIDE}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\nIMPORTANT GUIDELINES:\n1. Create complete, detailed documentation for the component\n2. Include clear examples, method documentation, and integration guidance\n3. Within the documentation, use the component_id (\"{{component_id}}\") as the base name for all classes, modules, and file references unless explicitly overridden in the candidate spec\n4. Format your response as a FileGenerationResult with a single file named \"{{component_id}}.md\"\n\nDo not include the component name or other text in the filename - it must be exactly \"{{component_id}}.md\".",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "generated_doc"
},
{
"type": "write_files",
"artifact": "generated_doc",
"root": "{{output_root|default:'output'}}/{{target_project}}/docs"
}
]
}

=== File: recipes/component_blueprint_generator/recipes/create_recipes.json ===
{
"steps": [
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/create_recipe_template.json",
"artifact": "create_recipe_template"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/edit_recipe_template.json",
"artifact": "edit_recipe_template"
},
{
"type": "generate",
"prompt": "You are an expert developer creating recipe files for component generation and editing. Based on the component specification and template recipes, create the final recipe files.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Documentation:\n{{generated_doc}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nTarget Project: {{target_project}}\nProject Recipe Path: {{project_recipe_path}}\n\nCreate Recipe Template:\n{{create_recipe_template}}\n\nEdit Recipe Template:\n{{edit_recipe_template}}\n\n# IMPORTANT GUIDELINES\n\n1. Use the templates as your starting point and maintain their overall structure\n\n2. For additional file includes and related docs:\n - Analyze the component specification to identify related components or documentation it might need\n - Include read_file steps for any relevant documents (like utils_docs for a component that uses utilities)\n - Format additional content using XML-style tags (like <CONTEXT_DOCS>content</CONTEXT_DOCS>)\n - Follow the pattern seen in executor_create.json, llm_create.json, etc.\n\n3. For context overrides:\n - Keep all existing context variables provided in the template\n - Add component-specific variables as needed\n - Use the pattern: \"additional_content\": \"<TAG_NAME>\\n{{artifact_name}}\\n</TAG_NAME>\"\n\n4. Naming and paths:\n - Use exactly '{{component_id}}_create.json' and '{{component_id}}_edit.json' for filenames\n - Ensure all paths use correct variables: {{project_recipe_path}}, {{component_id}}, etc.\n\nFormat your response as a FileGenerationResult with two files:\n1. '{{component_id}}_create.json' - The create recipe\n2. '{{component_id}}_edit.json' - The edit recipe",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "recipe_files"
},
{
"type": "write_files",
"artifact": "recipe_files",
"root": "{{output_root|default:'output'}}/{{target_project}}/recipes"
}
]
}

=== File: recipes/component_blueprint_generator/recipes/create_spec.json ===
{
"steps": [
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/spec_template.md",
"artifact": "spec_template"
},
{
"type": "generate",
"prompt": "You are an expert developer creating a formal component specification. Based on the candidate specification and component information, create a detailed specification document following the template structure.\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nModule Path: {{module_path|default:''}}\nComponent Type: {{component_type|default:''}}\nKey Dependencies: {{key_dependencies|default:''}}\n\nSpecification Template:\n{{spec_template}}\n\nUse the following guides for context:\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{COMPONENT_DOCS_SPEC_GUIDE}}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nIMPORTANT GUIDELINES:\n1. Create a complete, detailed specification for the component\n2. Within the specification, use the component_id (\"{{component_id}}\") as the base name for all classes, modules, and file references unless explicitly overridden in the candidate spec\n3. Format your response as a FileGenerationResult with a single file named \"{{component_id}}.md\"\n\nDo not include the component name or other text in the filename - it must be exactly \"{{component_id}}.md\".",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "generated_spec"
},
{
"type": "write_files",
"artifact": "generated_spec",
"root": "{{output_root|default:'output'}}/{{target_project}}/specs"
}
]
}

=== File: recipes/component_blueprint_generator/recipes/finalize_blueprint.json ===
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
"root": "{{output_root|default:'output'}}/{{target_project}}"
}
]
}
