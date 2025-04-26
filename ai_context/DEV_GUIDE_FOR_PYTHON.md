# Dev Guide for Python

When contributing to the Python codebase, please follow these guidelines to ensure consistency and maintainability.

- Place import statements at the top of the file, however, where appropriate, perform imports inside functions to avoid circular dependencies.
- All optional parameters should be typed as `Optional[Type]` and default to `None` unless otherwise specified.
- Set types for all variables, including `self` variables in classes.
- Use `List`, `Dict`, and other type hints from the `typing` module for type annotations, include the type of the list or dictionary.
- Initialize any variables that will be used outside of a block prior to the block, including `if`, `for`, `while`, `try`, etc. to avoid issues with variables that are possibly unbound on some code paths.
- If a variable could be `None`, verify that it is not `None` before using it.
- Assume that all dependencies mentioned in the component spec or docs are installed, do not write guards for them.
- Do not create main functions for components that do not have a main function listed in the spec.
- Use full names for variables, classes, and functions. For example, use `get_workspace` instead of `gw`.
- When creating an instance of a class based on `BaseModel` from a dictionary, use `<ClassName>.model_validate(<dict>)` instead of `<ClassName>(**<dict>)` to ensure that the model is validated.
- For `__init__.py` files, use `__all__` to define the public API of the module.
