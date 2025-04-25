# LoopStep Component Specification

## Purpose

The LoopStep component enables recipes to iterate over a collection of items, executing a specified set of steps for each item. It serves as a fundamental building block for batch processing, enabling modular workflows that operate on multiple similar items without requiring separate recipes.

## Core Requirements

- Process each item in a collection using a specified set of steps
- Support template rendering for the `items` path to access nested data structures via dot notation (e.g., "results.data.items")
- Isolate processing of each item to prevent cross-contamination
- Store the results of processing each item in a designated collection
- Support conditional execution based on item properties
- Provide consistent error handling across all iterations
- Maintain processing state to enable resumability
- Support various collection types (arrays, objects)
- Support concurrent processing of items using configurable parallelism settings (max_concurrency > 1)
- Provide control over the number of items processed simultaneously
- Allow for staggered execution of parallel items via optional delay parameter
- Prevent nested thread pool creation that could lead to deadlocks or resource exhaustion
- Provide reliable completion of all tasks regardless of recipe structure or nesting

## Implementation Considerations

- Use template rendering to resolve the `items` path before accessing data, enabling support for nested paths
- Clone the context for each item to maintain isolation between iterations
- Use a unique context key for each processed item to prevent collisions
- Execute the specified steps for each item using the current executor
- Collect results into a unified collection once all items are processed
- Log progress for each iteration to enable monitoring
- Support proper error propagation while maintaining iteration context
- Handle empty collections gracefully
- Leverage asyncio for efficient processing
- Support structured iteration history for debugging
- Use asyncio for concurrency control and task management
- If parallel item processing is enabled (max_concurrency > 1):
  - Implement an async execution model to allow for non-blocking I/O operations
  - When executing items in parallel, properly await async operations and run sync operations directly
  - Use `Context.clone()` to create independent context copies for each item
  - Implement a configurable launch delay (using `asyncio.sleep`) for staggered start times
  - Monitor exceptions and implement fail-fast behavior
  - Provide clear logging for item lifecycle events and execution summary
  - Manage resources efficiently to prevent memory or thread leaks

## Component Dependencies

### Internal Components

- **Protocols**: Leverages ContextProtocol for context sharing, ExecutorProtocol for execution, and StepProtocol for the step interface contract
- **Step Base**: Adheres to the step execution interface via StepProtocol
- **Step Registry**: Uses the step registry to instantiate the `execute_recipe` step for each sub-step
- **Context**: Shares data via a context object implementing the ContextProtocol between the main recipe and sub-recipes
- **Executor**: Uses an executor implementing ExecutorProtocol to run the sub-recipe
- **Utils/Templates**: Uses template rendering for the `items` path and sub-step configurations

### External Libraries

- **asyncio**: Uses asyncio for asynchronous processing and managing parallel processing of loop items
- **time**: Uses `time.sleep` to implement delays between sub-step launches

### Configuration Dependencies

None

## Output Files

- `steps/loop.py` - (LoopStep implementation)

## Logging

- Debug: Log the start/end of each item processing with its index/key, log steps execution within the loop
- Info: Log high-level information about how many items are being processed and the result collection

## Error Handling

- Validate the items collection exists and is iterable before starting
- Validate that steps are properly specified
- Handle both empty collections and single items gracefully
- Provide clear error messages when an item fails processing
- Include the item key/index in error messages for easier debugging
- Allow configuration of whether to fail fast or continue on errors
