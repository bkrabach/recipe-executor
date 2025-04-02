# Test Code Generation Recipe

This recipe demonstrates a simple workflow.

```json
[
  {
    "type": "read_files",
    "path": "recipes/example_simple/specs/sample_spec.txt",
    "artifact": "spec_text"
  },
  {
    "type": "generate",
    "prompt": "Using the following specification, generate a Python script that prints 'Hello, Test!'.\n\nSpecification:\n${spec_text}",
    "model": "{{model|default:'openai:o3-mini'}}",
    "artifact": "generated_code"
  },
  {
    "type": "write_files",
    "artifact": "generated_code",
    "root": "output"
  }
]
```
