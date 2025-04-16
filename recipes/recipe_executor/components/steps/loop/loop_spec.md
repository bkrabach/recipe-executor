# LoopStep Component Specification

## Purpose

The LoopStep component enables recipes to iterate over a collection of items, executing a specified set of steps for each item. It serves as a fundamental building block for batch processing, enabling modular workflows that operate on multiple similar items without requiring separate recipes.

## Core Requirements

- Process each item in a collection using a specified set of steps
- Isolate processing of each item to prevent cross-contamination
- Store the results of processing each item in a designated collection
- Support conditional execution based on item properties
- Provide consistent error handling across all iterations
- Maintain processing state to enable resumability
- Support various collection types (arrays, objects)

## Implementation Considerations

- Clone the context for each item to maintain isolation between iterations
- Use a unique context key for each processed item to prevent collisions
- Execute the specified steps for each item using the current executor
- Collect results into a unified collection once all items are processed
- Log progress for each iteration to enable monitoring
- Support proper error propagation while maintaining iteration context
- Handle empty collections gracefully
- Leverage asyncio for efficient processing
- Support structured iteration history for debugging

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for context management, ExecutorProtocol for parallel execution, and StepProtocol for the step interface
- **Step Base** – (Required) Adheres to the step execution interface via StepProtocol
- **Step Registry** – (Required) Uses the step registry to instantiate the `execute_recipe` step for each sub-step
- **Context** – (Required) Utilizes a ContextProtocol implementation (e.g. using Context.clone()) to create isolated contexts for each sub-step
- **Executor** – (Required) Uses an Executor implementing ExecutorProtocol to run each sub-recipe in a separate thread
- **Utils** – (Optional) Uses template rendering for sub-step configurationsn

### External Libraries

- **asyncio** - (Required) Uses asyncio for asynchronous processing

### Configuration Dependencies

None

## Output Files

- `steps/loop.py` - (LoopStep implementation)

## Logging

- Debug: Log the start/end of each item processing with its index/key, log steps execution within the loop
- Info: Log high-level information about how many items are being processed and the result collection
- Error: Log detailed error information including which item caused the error and at what stage

## Error Handling

- Validate the items collection exists and is iterable before starting
- Validate that steps are properly specified
- Handle both empty collections and single items gracefully
- Provide clear error messages when an item fails processing
- Include the item key/index in error messages for easier debugging
- Allow configuration of whether to fail fast or continue on errors

## Future Considerations

- Parallel processing of items with configurable concurrency
- Enhanced filtering capabilities to process only certain items
- Progress tracking for long-running loops
- Checkpointing and resumability for very large collections
- Support for early termination based on conditions
