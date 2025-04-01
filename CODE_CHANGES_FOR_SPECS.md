# Code Changes to Implement in Specs/Docs

As per the repository guidelines, code changes should be implemented through spec/doc improvements. The following changes need to be captured in specs/docs to drive code generation:

## Path Handling Improvements

### Changes needed in main.py:
1. Add support for tilde (~) expansion in file paths:
   ```python
   # First expand any user path with tilde (~)
   input_dir = os.path.expanduser(args["input_dir"])
   ```

2. Handle absolute vs. relative paths correctly:
   ```python
   # If it's an absolute path, use it directly
   # Otherwise, make it absolute relative to current directory
   if not os.path.isabs(input_dir):
       input_dir = os.path.abspath(input_dir)
   ```

### Changes needed in write_files.py:
1. Add path duplication prevention:
   ```python
   # Check if the path is already absolute
   if os.path.isabs(rel_path):
       full_path = rel_path
   else:
       # Check if rel_path already contains the output directory name to avoid duplication
       output_dir_name = os.path.basename(output_root)
       path_parts = rel_path.split(os.path.sep)
       
       if path_parts and path_parts[0] == output_dir_name:
           # If the path already starts with the output directory name, avoid duplication
           self.logger.info(f"Avoiding path duplication for {rel_path}")
           # Remove the duplicated directory from the path
           rel_path = os.path.sep.join(path_parts[1:]) if len(path_parts) > 1 else ""
   ```

2. Add special handling for recipe_executor paths:
   ```python
   # Check if the output path includes a recipe_executor path segment
   if 'recipe_executor' in rel_path:
       # This is a special case where we want to preserve the recipe_executor folder structure
       self.logger.info(f"Preserving recipe_executor path structure for {rel_path}")
       # No changes needed
       pass
   ```

## Implementation Strategy

These changes should be implemented in:

1. **Specs**: Update the component specs to include requirements for robust path handling
2. **Docs**: Update component docs to describe the path handling capabilities
3. **Recipe**: Create a recipe to make these improvements to the code that will be regenerated

## Testing Strategy

The changes should be tested with:
- Relative paths (`output`, `./output`)
- Absolute paths (`/Users/name/project/output`)
- Home directory paths (`~/project/output`)
- Paths that might cause duplication issues