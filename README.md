# Recipe Executor

Recipe Executor is a tool designed to bridge natural language instructions and reliable code execution. It takes recipes written in plain English and executes them through a structured pipeline that ensures reliability and predictability.

## Features

- **Natural Language Interface**: Write recipes in plain English without special syntax
- **LLM-Powered Parsing**: Uses large language models to interpret natural language instructions
- **Reliable Execution**: Executes recipes with deterministic behavior and clear error handling
- **Modular Architecture**: Clean separation between parsing, execution, and step implementation
- **Meta-Recipes**: Support for recipes that call other recipes

## Installation

```bash
# Basic installation
pip install recipe-executor

# With OpenAI support
pip install 'recipe-executor[openai]'

# With Anthropic support
pip install 'recipe-executor[anthropic]'

# With both
pip install 'recipe-executor[openai,anthropic]'

# For development
pip install 'recipe-executor[dev]'
```

## Usage

### Command Line

```bash
# Basic usage
recipe-executor path/to/recipe.md

# With input variables
recipe-executor path/to/recipe.md --input input_file /path/to/input.txt

# With custom directories
recipe-executor path/to/recipe.md --root-dir ./my_project --recipes-dir ./my_recipes
```

### Python API

```python
import asyncio
from recipe_executor import RecipeParser, ExecutionEngine, ExecutionContext

async def main():
    # Read the recipe
    with open("path/to/recipe.md", "r") as f:
        recipe_text = f.read()

    # Parse the recipe
    parser = RecipeParser()
    recipe = await parser.parse(recipe_text)

    # Set up the execution context
    context = ExecutionContext(root_dir="./my_project", recipes_dir="./my_recipes")
    context.set_variable("input_file", "/path/to/input.txt")

    # Execute the recipe
    engine = ExecutionEngine()
    result = await engine.execute(recipe, context)

    print(f"Recipe executed successfully!")
    print(f"Result: {result}")

# Run the async function
asyncio.run(main())
```

## Example Recipe

```markdown
# Component Splitter

Read the project definition document from the input file which contains multiple components defined in separate sections.

For each component section that starts with "## Component:" or similar heading:

- Extract the component name, purpose, and specifications
- Identify dependencies mentioned in the component description
- Create a new file named with the component name in the components directory
- Include only the content specific to this component
- Add a "Context" section that includes:
  - Project-wide requirements that affect this component
  - Interfaces with dependent components
  - Any architectural constraints

Save a mapping file that tracks which components were extracted and their dependencies.

Notify me when complete with a summary of components extracted.
```

## Supported Step Types

The Recipe Executor currently supports the following step types:

1. **FILE_READ**: Read files from disk
2. **FILE_WRITE**: Write files to disk
3. **LLM_GENERATE**: Generate content using LLMs
4. **RECIPE_CALL**: Call other recipes (for meta-recipes)
5. **CONDITIONAL**: Basic conditional logic

## License

MIT License
