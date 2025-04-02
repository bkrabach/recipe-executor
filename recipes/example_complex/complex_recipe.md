# Complex Code Generation Recipe

This recipe demonstrates a multi-step workflow that:

1. Reads two specification files.
2. Uses an LLM step to generate a comprehensive Python module that integrates both core and auxiliary functionalities.
3. Writes the generated module to disk.
4. Executes a sub-recipe to generate an additional utility module.

```json
[
  {
    "type": "read_files",
    "path": "recipes/example_complex/specs/main_spec.txt",
    "artifact": "main_spec"
  },
  {
    "type": "read_files",
    "path": "recipes/example_complex/specs/auxiliary_spec.txt",
    "artifact": "aux_spec"
  },
  {
    "type": "generate",
    "prompt": "Using the following main specification:\n\n{main_spec}\n\nand the auxiliary details:\n\n{aux_spec}\n\nGenerate a comprehensive Python module that contains a main function printing 'Hello from Main!' and an auxiliary function returning a greeting. Return a JSON object with keys 'files' (a list of file objects with 'path' and 'content') and 'commentary'.",
    "model": "{{model|default:'openai:o3-mini'}}",
    "artifact": "generated_module"
  },
  {
    "type": "write_files",
    "artifact": "generated_module",
    "root": "output/main_module"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/example_complex/sub_recipe.md"
  }
]
```
