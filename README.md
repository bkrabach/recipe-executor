# Recipe Executor

A tool for executing recipe-like natural language instructions to generate and manipulate code and other files.

## Overview

The Recipe Executor is a flexible orchestration system that executes "recipes" - JSON-based definitions of sequential steps to perform tasks such as file reading, LLM-based content generation, and file writing. This project allows you to define complex workflows through simple recipe files.

## Key Components

- **Recipe Format**: JSON-based recipe definitions with steps
- **Step Types**: Various operations including file reading/writing, LLM generation, and sub-recipe execution
- **Context System**: Shared state for passing data between steps
- **Template Rendering**: Liquid templates for dynamic content generation

## Setup and Installation

### Prerequisites

Recommended installers:

- Linux: apt or your distribution's package manager
- macOS: [brew](https://brew.sh/)
- Windows: [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

#### Development tools

The core dependencies you need to install are:

- `make` - for scripting installation steps of the various projects within this repo
- `uv` - for managing installed versions of `python` - for installing python dependencies

Linux:

    # make is installed by default on linux
    sudo apt update && sudo apt install pipx
    pipx ensurepath
    pipx install uv

macOS:

    brew install make
    brew install uv

Windows:

    winget install ezwinports.make -e
    winget install astral-sh.uv  -e

### Setup Steps

1. Clone this repository
2. Copy the environment file and configure your API keys:
   ```bash
   cp .env.example .env
   # Edit .env to add your OPENAI_API_KEY and other optional API keys
   ```
3. Run the setup command to create a virtual environment and install dependencies:
   ```bash
   make
   ```
4. Activate the virtual environment:
   - **Linux/macOS**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```
5. Test the installation by running the example recipe:
   ```bash
   make recipe-executor-create
   ```

## Using the Makefile

The project includes several useful make commands:

- **`make`**: Sets up the virtual environment and installs all dependencies
- **`make run`**: Launches the interactive terminal UI (recommended for most users)
- **`make recipe-executor-context`**: Builds AI context files for recipe executor development
- **`make recipe-executor-create`**: Generates recipe executor code from scratch using the recipe itself
- **`make recipe-executor-create-with-desc DESC="Your product description" [IN="/path/to/input"] [OUT="/path/to/output"]`**: Generates recipe executor code with a custom product description and optional directory paths
- **`make recipe-executor-edit`**: Revises existing recipe executor code using recipes

### Interactive Terminal UI

The easiest way to use Recipe Executor is through the interactive terminal UI:

```bash
make run
```

This will present a comprehensive menu organized by functionality:

#### Code Generation
1. **Generate code from recipe-executor templates** - Create code based on your description
2. **Edit existing code using recipe-executor** - Modify and enhance existing code

#### Blueprint Operations
3. **Create component blueprint** - Generate a blueprint for a new component
4. **Generate code from blueprint** - Create code from an existing blueprint

#### Recipe Utilities
5. **Execute custom recipe file** - Run any recipe file with optional parameters
6. **List available recipes** - View all available recipes in the project

#### System Tools
7. **Rebuild AI context files** - Update the AI context for better code generation
8. **View system information** - See details about your installation and configuration
9. **Exit** - Quit the application

The UI guides you through each operation with clear prompts, helpful descriptions, and real-time feedback. Each menu option provides a dedicated interface for the specific functionality, making it easy to use all of Recipe Executor's features without remembering complex commands.

## Recent Improvements

### Enhanced Terminal UI
The new terminal-based user interface (`make run`) provides a comprehensive menu system that makes it easy to access all Recipe Executor features without remembering complex commands.

### Robust Path Handling
The path handling system has been significantly improved to support:
- Absolute paths (`/Users/name/project/output`)
- Relative paths (`output`, `./output`)
- Home directory paths with tilde expansion (`~/project/output`)
- Prevention of path duplication issues
- Safe file placement across different environments

These improvements ensure that files are always created in the expected locations, regardless of how paths are specified.

## Running Recipes

Execute a recipe using the command line interface:

```bash
python recipe_executor/main.py path/to/your/recipe.json
```

You can also pass a product description and other options:

```bash
# Simple usage with description
python recipe_executor/main.py path/to/your/recipe.json "Your product description"

# With input/output directories (using short options)
python recipe_executor/main.py path/to/your/recipe.json "Your description" -i /path/to/input -o /path/to/output

# Using home directory path with tilde
python recipe_executor/main.py path/to/your/recipe.json "Your description" -i ~/project/input -o ~/project/output

# Advanced: context variables
python recipe_executor/main.py path/to/your/recipe.json -c key=value
```

### Path Handling

Recipe Executor supports various path formats:

- **Relative paths**: `output`, `./output`, `project/output`
- **Absolute paths**: `/Users/name/project/output`
- **Home directory paths**: `~/project/output`

The system ensures files are placed in the correct locations without path duplication issues, making it safe to use in different environments.

## Project Structure

The project contains:

- **`recipe_executor/`**: Core implementation with modules for execution, context management, and steps
- **`recipes/`**: Recipe definition files that can be executed
- **Implementation Philosophy**: Code follows a minimalist, functionally-focused approach with clear error handling

## Building from Recipes

One of the most interesting aspects of this project is that it can generate its own code using recipes:

1. To generate the code from scratch:

   ```bash
   make recipe-executor-create
   ```

2. To edit/revise existing code:
   ```bash
   make recipe-executor-edit
   ```

This demonstrates the power of the Recipe Executor for code generation and maintenance tasks.
