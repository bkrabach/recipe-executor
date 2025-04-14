# GenerateWithLLMStep Component Usage

## Importing

```python
from recipe_executor.steps.generate_llm import GenerateWithLLMStep, GenerateLLMConfig
```

## Configuration

The GenerateWithLLMStep is configured with a GenerateLLMConfig:

```python
class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str
```

## Step Registration

The GenerateWithLLMStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.generate_llm import GenerateWithLLMStep

STEP_REGISTRY["generate"] = GenerateWithLLMStep
```

## Basic Usage in Recipes

The GenerateWithLLMStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate Python code for a utility that: {{requirements}}",
      "model": "{{model|default:'openai/o3-mini'}}",
      "artifact": "generation_result"
    }
  ]
}
```

## Template-Based Prompts

The prompt can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "path": "specs/component_spec.md",
      "artifact": "spec"
    },
    {
      "type": "generate",
      "prompt": "You are an expert Python developer. Based on the following specification, generate code for a component:\n\n{{spec}}",
      "model": "{{model|default:'openai/o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Model Selection

The model identifier can also use template variables:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code based on: {{spec}}",
      "model": "{{model_provider/default:'openai'}}:{{model_name|default:'o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Artifact Keys

The artifact key can be templated to create dynamic storage locations:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code for: {{component_name}}",
      "model": "{{model|default:'openai/o3-mini'}}",
      "artifact": "{{component_name}}_result"
    }
  ]
}
```

## LLM Response Format

The response from `call_llm` is a FileGenerationResult object structure. For example:

```python
# FileGenerationResult structure
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)
```

This result contains a list of generated files (each as a FileSpec with a path and content) and an overall commentary.

## Important Notes

- The artifact key can be dynamic using template variables
- The prompt is rendered using the current context (ContextProtocol) before sending to the LLM
- The model identifier follows the format `"provider/model_name"`
- The LLM response is returned as a FileGenerationResult object (with `files` and `commentary` fields)
- LLM calls may incur costs with the respective provider
