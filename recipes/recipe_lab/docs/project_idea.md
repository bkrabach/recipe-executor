## Goal

Create a web app that allows users to create and execute recipes for automating their workflows, called 'Recipe Lab'.

## Specification

### Core Requirements

- **User Interface**: A web-based interface for users to create, edit, and execute recipes.
- **Recipe Creation**: Users can create recipes using natural language or via a drag-and-drop interface.
- **Recipe Execution**: Users can execute recipes and view the results in real-time.
- **Recipe Storage**: Recipes are stored in a database for easy retrieval and sharing.
- **Recipe Composition**: The user's existing recipes can be used as building blocks for new recipes.
- **Version Control**: Users can version their recipes and revert to previous versions if needed.

### Implementation Details

- **Frontend**: Use vanilla JavaScript and HTML/CSS for the user interface. Consider use of unpkg.com or similar for loading libraries.
- **Backend**: Use python FastAPI for the backend. The backend should handle recipe execution and storage.
- **Recipe Execution**: Use the `recipe-executor` library to execute recipes.
- **Storage**: Write the recipes and any other data to a `.data` directory in the root of the backend.

## Supporting Files

### Project Context (vision docs, etc.)

- none

### Reference Files (library docs, etc.)

- `ai_context/generated/recipe_executor_code_files.md`:
  - This file contains the code files for the `recipe-executor` library.
- `ai_context/generated/recipe_executor_recipes.md`:
  - This file contains the recipes for the `recipe-executor` library.
