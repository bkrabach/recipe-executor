# ParallelStep Component Specification

## Purpose

The ParallelStep component enables the Recipe Executor to run multiple sub-recipes concurrently within a single step. It improves execution efficiency by parallelizing independent tasks while maintaining isolation between them.

## Core Requirements

- Accept a list of sub-step configurations (each sub-step is an `execute_recipe` step definition)
- Clone the current execution context for each sub-step to ensure isolation
- Execute sub-steps concurrently with a configurable maximum concurrency limit
- Support an optional delay between launching each sub-step
- Wait for all sub-steps to complete before proceeding, with appropriate timeout handling
- Implement fail-fast behavior: if any sub-step fails, stop launching new ones and report the error
- Prevent nested thread pool creation that could lead to deadlocks or resource exhaustion
- Provide reliable completion of all tasks regardless of recipe structure or nesting

## Implementation Considerations

- Use asyncio for concurrency control and task management
- Implement an async execution model to allow for non-blocking I/O operations
- When executing substeps, properly await async operations and run sync operations directly
- Add configurable timeouts to prevent indefinite waiting for task completion
- Use `Context.clone()` to create independent context copies for each sub-step
- Implement a configurable launch delay (using `asyncio.sleep`) for staggered start times
- Monitor exceptions and implement fail-fast behavior
- Provide clear logging for sub-step lifecycle events and execution summary
- Manage resources efficiently to prevent memory or thread leaks

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Uses ContextProtocol for context management, ExecutorProtocol for parallel execution, and StepProtocol for the step interface
- **Step Interface** – (Required) Adheres to the step execution interface via StepProtocol
- **Context** – (Required) Utilizes a ContextProtocol implementation (e.g. using Context.clone()) to create isolated contexts for each parallel sub-step
- **Step Registry** – (Required) Uses the step registry to instantiate the `execute_recipe` step for each sub-step
- **Executor** – (Required) Uses an Executor implementing ExecutorProtocol to run each sub-recipe in a separate thread
- **Utils** – (Optional) Uses template rendering for sub-step configurations

### External Libraries

- **ThreadPoolExecutor** – (Required) Uses `concurrent.futures.ThreadPoolExecutor` for parallel execution
- **time** – (Optional) Uses `time.sleep` to implement delays between sub-step launches

### Configuration Dependencies

None

## Output Files

- `steps/parallel.py` (ParallelStep implementation)

## Logging

- Debug: Log sub-step start/completion events, thread allocation, and configuration details
- Info: Log start and completion with a summary of the parallel execution (number of steps and success/failure counts)

## Error Handling

- Implement fail-fast behavior when any sub-step encounters an error
- Cancel pending sub-steps if an error occurs
- Include clear error context identifying which sub-step failed
- Ensure proper thread pool shutdown to prevent orphaned threads
- Propagate the original exception with contextual information about the failure

## Future Considerations

- Support arbitrary step types beyond just execute_recipe
- Aggregate results from sub-steps back into the parent context
- Dynamic concurrency control based on system load
- Configurable per-step timeouts with proper cancellation
- Task prioritization within the global executor
- Monitoring and reporting for resource usage across the task queue
