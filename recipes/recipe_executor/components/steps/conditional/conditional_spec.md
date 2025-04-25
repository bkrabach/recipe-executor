# Conditional Step Type Specification

## Purpose

The Conditional step enables branching execution paths in recipes based on evaluating expressions. It serves as a key building block for creating utility recipes or non-LLM flow control.

## Core Requirements

- Evaluate conditional expressions against the current context state
- Support multiple condition types including:
  - Context value checks
  - File existence checks
  - Comparison operations
- Execute different sets of steps based on the result of the condition evaluation
- Support nested conditions and complex logical operations
- Provide clear error messages when expressions are invalid

## Configuration Structure

```json
{
  "type": "conditional",
  "config": {
    "condition": "expression_string",
    "if_true": {
      "steps": [
        /* steps to execute if true */
      ]
    },
    "if_false": {
      "steps": [
        /* steps to execute if false */
      ],
      "optional": true
    }
  }
}
```

### Configuration Fields:

- `condition`: A string containing the expression to evaluate (supports multiple expression types)
- `if_true`: Object containing steps to execute when the condition evaluates to true
- `if_false`: Optional object containing steps to execute when the condition evaluates to false

## Expression Types

The `condition` field should support:

1. **Context Value Expressions**:

   - `context["key"] == value`
   - `context["key"]["nested"] != null`

2. **File Operations**:

   - `file_exists("path/to/file.md")`
   - `all_exist(["file1.md", "file2.md"])`
   - `is_newer("source.md", "target.md")`

3. **Logical Operations**:

   - `and(expr1, expr2)`
   - `or(expr1, expr2)`
   - `not(expr)`

4. **Value Comparisons**:
   - `==`, `!=`, `>`, `<`, `>=`, `<=`
   - `contains(list, item)`
   - `startswith(string, prefix)`

## Implementation Considerations

- Support template rendering in the condition string before evaluation
- Keep expression evaluation lightweight and focused on common needs
- Allow for direct access to context values via expression syntax
- Make error messages helpful for debugging invalid expressions
- Process nested step configurations in a recursive manner
- Ensure consistent logging of condition results and execution paths

## Logging

- Debug: Log the condition being evaluated, its result, and which branch is taken
- Info: None

## Component Dependencies

### Internal Components

- **Context**: Uses context to access values for condition evaluation
- **Utils/Templates**: Uses template rendering for condition strings with variables

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Provide clear error messages for invalid expressions
- Handle missing context values gracefully (typically evaluating to false)
- Properly propagate errors from executed step branches

## Output Files

- `steps/conditional.py`
