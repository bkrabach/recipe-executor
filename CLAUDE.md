# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important: Recipe-Based Code Generation

- Code in `recipe-executor` is generated using its own recipes in `recipes/recipe_executor/`
- To modify code properly, edit the recipe files rather than the generated code directly
- Generate/regenerate code using `make recipe-executor-create` or `make recipe-executor-edit`

## Build/Test/Lint Commands

- Install dependencies: `make install` (uses uv)
- Lint code: `make lint` (runs uvx ruff check --no-cache --fix .)
- Format code: `make format` (runs uvx ruff format --no-cache .)
- Type check: `make type-check` (runs pyright)
- Run all tests: `make test` or `make pytest`
- Run a single test: `uv run pytest tests/path/to/test_file.py::TestClass::test_function -v`
- Upgrade dependency lock: `make lock-upgrade`

## Code Style Guidelines

- Use Python type hints consistently including for self in class methods
- Import statements at top of files, organized by standard lib, third-party, local
- Use descriptive variable/function names (e.g., `get_workspace` not `gw`)
- Use `Optional` from typing for optional parameters
- Initialize variables outside code blocks before use
- All code must work with Python 3.11+
- Use Pydantic for data validation and settings
