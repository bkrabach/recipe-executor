# Protocols Component Specification

## Purpose

The Protocols component defines the shared interface contracts for core parts of the Recipe Executor system. It centralizes the definitions of how the Executor, Context, and Steps interact, matching project conventions of clear separation. By providing Protocol-based interfaces, this component ensures all implementers (and consumers) of these interfaces adhere to the same methods and signatures, thereby promoting consistency and preventing tight coupling or import cycles between components.

## Core Requirements

- Define a `ContextProtocol` that captures the required behaviors of the Context (dictionary-like access, retrieval, iteration, cloning).
- Define a `StepProtocol` that captures the execution interface for any step (the `execute(context)` method signature).
- Define an `ExecutorProtocol` that captures the interface of the executor (the `execute(recipe, context, logger)` method signature).
- Ensure these protocols are the single source of truth for their respective contracts, referenced throughout the codebase for type annotations and documentation.
- Eliminate direct references to concrete classes (e.g., `Context` or `Executor`) in other components’ interfaces by using these protocol definitions, thereby avoiding circular dependencies.
- Follow the project's minimalist design philosophy: interfaces should be concise, containing only what is necessary for inter-component communication.

## Implementation Considerations

- Use Python's `typing.Protocol` to define interfaces in a structural subtyping manner. This allows classes to implement the protocols without explicit inheritance, maintaining loose coupling.
- Mark protocol interfaces with `@runtime_checkable` to allow runtime enforcement (e.g., in tests) if needed, without impacting normal execution.
- The `ContextProtocol` should include all methods that other components (steps, executor) rely on. This includes standard mapping methods (`__getitem__`, `__setitem__`, etc.), as well as `get`, `clone`, and any other utility needed for context usage (like `keys`, `as_dict`).
- The `StepProtocol` interface is minimal by design (just the `execute` method with a `ContextProtocol` parameter), since step initialization and configuration are handled separately. This focuses the contract on execution behavior only.
- The `ExecutorProtocol` should accept a recipe in various forms (string path, JSON string, or dict) and a context implementing `ContextProtocol`. It returns `None` and is expected to raise exceptions on errors (as documented in Executor component). Logging is passed optionally.
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
- **logging** - (Required) Uses Python's standard `logging` module for type annotations of logger parameters (no logging calls are made in protocols).

### Configuration Dependencies

- None

## Error Handling

- None

## Output Files

- `protocols.py` (contains `ContextProtocol`, `StepProtocol`, `ExecutorProtocol` definitions)

## Future Considerations

- As the system evolves, additional protocols might be introduced for new interface contracts (for example, if a new component needs a defined interface).
- If stronger type enforcement is needed, consider adding abstract base classes (ABCs) in addition to protocols. However, current philosophy favors Protocol for flexibility and minimal intrusion.
- Any changes to these protocols (such as adding a method) should be done cautiously and documented clearly in `protocols_docs.md`, as they affect multiple components. All implementers would need to be updated to comply with any interface changes.
- Continue treating the `protocols_docs.md` as the authoritative reference for interface contracts – all developers (and AI recipes) should consult it when working with or implementing core interfaces.
