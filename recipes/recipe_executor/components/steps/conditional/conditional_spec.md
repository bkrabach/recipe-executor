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

- If expression is already a boolean or a string that can be evaluated to a boolean, use it directly as it may have been rendered by the template engine
- Include conversion of "true" and "false" strings to boolean values in any safe globals list
- Keep expression evaluation lightweight and focused on common needs
- Allow for direct access to context values via expression syntax
- Make error messages helpful for debugging invalid expressions
- Process nested step configurations in a recursive manner
- Ensure consistent logging of condition results and execution paths
- Properly handle function-like logical operations that conflict with Python keywords

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
