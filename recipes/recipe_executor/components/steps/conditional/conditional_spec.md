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

## Implementation Considerations

- Support template rendering in the condition string before evaluation
- Keep expression evaluation lightweight and focused on common needs
- Allow for direct access to context values via expression syntax
- Make error messages helpful for debugging invalid expressions
- Process nested step configurations in a recursive manner
- Ensure consistent logging of condition results and execution paths
- Properly handle function-like logical operations that conflict with Python keywords:

  - Transform logical function calls before evaluation:

    ```python
      # First replace boolean literals
      expr = expr.replace(" true", " True").replace(" false", " False").replace(" null", " None")

      # Transform logical function calls to avoid Python keyword conflicts
      # Look for function calls with opening parenthesis to avoid replacing words inside strings
      expr = expr.replace("and(", "_and(")
      expr = expr.replace("or(", "_or(")
      expr = expr.replace("not(", "_not(")
    ```

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
