# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple, dictionary-like interface that steps and other components use to store and retrieve data (artifacts) during recipe execution, along with a separate space for configuration values.

## Core Requirements

- Maintain a store for **artifacts** (dynamic data produced and consumed by steps) and a separate store for **configuration** (static or initial settings).
- Support dictionary-like operations for artifacts:
  - Setting values by key (e.g., `context["x"] = value`).
  - Retrieving values by key (e.g., `value = context["x"]` or `context.get("x")`).
  - Checking for keys (`"x" in context`).
  - Iterating over keys (for example, `for k in context: ...`).
- Ensure that modifying the context in one step affects subsequent steps (shared mutability), while also allowing safe copying when needed.
- Provide a `clone()` method to create a deep copy of the entire context (both artifacts and configuration) for use cases like parallel execution where isolation is required.
- Remain lightweight and straightforward, following minimalist design principles (it should essentially behave like a `dict` with a config attached, without extra complexity).
- Provide a `dict()` and `json()` method to return a deep copy of the artifacts as a standard Python dictionary and a JSON string, respectively. This is useful for serialization or logging purposes.

## Implementation Considerations

- Use a Python dictionary internally to store artifacts. The keys are strings and values can be of any type (no restriction on artifact data types).
- Store configuration in a separate, internal dictionary (`_config` attribute) to distinguish it from runtime artifacts. Configuration might be populated at context creation and typically remains constant, but it's not enforced as immutable by the class.
- On initialization (`__init__`), deep copy any provided artifacts or config dictionaries. This prevents unintentional side effects if the caller modifies the dictionaries after passing them in.
- Implement the magic methods `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`, and `__len__` to mimic standard dict behavior for artifacts. Also provide a `keys()` method for convenience.
- The `get` method should allow a default value, similar to `dict.get`, to avoid raising exceptions on missing keys.
- When iterating (`__iter__` or using `keys()`), return a static list or iterator that won’t be affected by concurrent modifications (for example, by copying the key list).
- The `clone()` method should deep copy both artifacts and configuration to produce a completely independent Context. This is important for features like running sub-recipes in parallel or reusing a context as a template.
- Raise a `KeyError` with a clear message in `__getitem__` if a key is not found, to help with debugging missing artifact issues.
- Do not implement any locking or thread-safety measures; the context is intended for sequential use within the executor (concurrent modifications are handled by using `clone` for parallelism instead).
- The Context class should implement the `ContextProtocol` interface defined in the Protocols component. That means any changes to the interface (methods or behavior) should be reflected in both the class and the protocol definition. In practice, the Context class already provides all methods required by `ContextProtocol`.

## Logging

- None

## Dependency Integration Considerations

### Internal Components

- **Protocols** - (Required) The Context component conforms to the `ContextProtocol` interface, which is defined in the Protocols component. This ensures other components interact with Context through a well-defined contract.

### External Libraries

- **copy** (Python stdlib) - (Required) Uses `copy.deepcopy` for cloning internal state safely.
- **typing** - (Required) Used for type hints (e.g., `Dict[str, Any]`, `Iterator[str]`) to clarify usage.

### Configuration Dependencies

- **None.** The Context component does not rely on external configuration. It is typically configured via its constructor arguments (artifacts and config dicts) provided at runtime by Main or a calling component.

## Error Handling

- Attempts to access a missing artifact key via `context["missing_key"]` result in a `KeyError`. The error message explicitly names the missing key for clarity (e.g., `"Key 'foo' not found in Context."`).
- The `get` method returns a default (or `None` if not provided) instead of raising an error for missing keys, offering a safe way to query the context.
- Setting a key (`context["x"] = value`) has no special error cases; it will overwrite existing values if the key already exists.
- Cloning always succeeds barring extreme cases (like objects in the context that are not copyable); such cases would raise exceptions from `copy.deepcopy` which propagate up (this is acceptable, as it would be a misusage of context content types).

## Output Files

- `context.py`

## Future Considerations

- **Namespacing or Hierarchies**: In larger workflows, there might be a need to namespace context data (e.g., per step or per sub-recipe) to avoid key collisions. Future versions might introduce optional namespacing schemes or structured keys.
- **Immutable Context Option**: Possibly provide a mode or subclass for an immutable context (read-only once created) for scenarios where you want to ensure no step modifies the data.
