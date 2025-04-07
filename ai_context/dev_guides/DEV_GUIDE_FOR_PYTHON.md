# Dev Guide for Python

When contributing to the Python codebase, please follow these guidelines to ensure consistency and maintainability.

- Place import statements at the top of the file.
- All optional parameters should use `Optional` from the `typing` module.
- Set types for all variables, including `self` variables in classes.
- Use `List`, `Dict`, and other type hints from the `typing` module for type annotations, include the type of the list or dictionary.
- Initialize any variables that will be used outside of a block prior to the block, including `if`, `for`, `while`, `try`, etc.
- Assume that all dependencies mentioned in the component spec or docs are installed, do not write guards for them.
- Do not create main functions for components that do not have a main function listed in the spec.
- Use full names for variables, classes, and functions. For example, use `get_workspace` instead of `gw`.
