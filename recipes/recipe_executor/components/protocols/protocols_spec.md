# Protocols Component Specification

## Purpose

The Protocols component defines the core interfaces for the Recipe Executor system. It provides a set of protocols that standardize the interactions between components, ensuring loose coupling and clear contracts for behavior. This allows for flexible implementations and easy integration of new components without modifying existing code.

## Core Requirements

- Define a `ContextProtocol` that captures the required behaviors of the Context (dictionary-like access, retrieval, iteration, cloning).
- Define a `StepProtocol` that captures the execution interface for any step (the async `execute(context)` method signature).
- Define an `ExecutorProtocol` that captures the interface of the executor (the async `execute(recipe, context)` method signature).
- Support asynchronous execution throughout the system to enable non-blocking I/O operations.
- Ensure these protocols are the single source of truth for their respective contracts, referenced throughout the codebase for type annotations and documentation.
- Eliminate direct references to concrete classes (e.g., `Context` or `Executor`) in other components’ interfaces by using these protocol definitions, thereby avoiding circular dependencies.
- Follow the project's minimalist design philosophy: interfaces should be concise, containing only what is necessary for inter-component communication.

## Implementation Considerations

- Use Python's `typing.Protocol` to define interfaces in a structural subtyping manner. This allows classes to implement the protocols without explicit inheritance, maintaining loose coupling.
- Mark protocol interfaces with `@runtime_checkable` to allow runtime enforcement (e.g., in tests) if needed, without impacting normal execution.
- See the `protocols_docs.md` file for detailed documentation on each protocol, including method signatures, expected behaviors, and examples of usage. This file serves as the authoritative reference for developers implementing or using these protocols.
- No actual business logic or data storage should exist in `protocols.py`; it strictly contains interface definitions with `...` (ellipsis) as method bodies. This keeps it aligned with the "contracts only" role of the component.
- Ensure naming and signatures exactly match those used in concrete classes to avoid confusion. For example, `ContextProtocol.clone()` returns a `ContextProtocol` to allow flexibility in context implementations.
- Keep the protocols in a single file (`protocols.py`) at the root of the package (no sub-package), consistent with single-file component convention. This file becomes a lightweight dependency for any module that needs the interfaces.

## Logging

- None

## Dependency Integration Considerations

### Internal Components

- None

### External Libraries

- **typing** - (Required) Uses Python's built-in `typing` module (particularly `Protocol` and related features) to define structural interfaces.

### Configuration Dependencies

- None

## Error Handling

- None

## Output Files

- `protocols.py` (contains `ContextProtocol`, `StepProtocol`, `ExecutorProtocol` definitions)
