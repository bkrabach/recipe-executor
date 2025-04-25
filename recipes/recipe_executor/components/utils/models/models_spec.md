# Models-Utility Component Specification

## Purpose

Provide reusable helpers for Pydantic models, such as conversion from JSON-Schema object definitions to fully-typed
`pydantic.BaseModel` subclasses.

## Core Requirements

- `json_object_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]`
  Converts any root-level **object** (incl. nested structures & `"required"`) into a `BaseModel` created with `pydantic.create_model`.
- The schema must be a valid JSON-Schema object fragment. Chilren of the root object can be:
  - JSON-Schema primitive types: `"string"`, `"integer"`, `"number"`, `"boolean"`.
  - Compound types: `"object"`, `"array"` (alias `"list"`).
  - Unknown / unsupported `"type"` values fall back to `typing.Any`.
- All schema types must yield a valid BaseModel subclass:
  - Root object schemas become a model with fields matching properties
  - Any other root type (e.g., array, string, number) is rejected as invalid.
- Strictly validate input schemas before processing.
- Stateless, synchronous, no logging, no I/O.
- Raise `ValueError` on malformed schemas (e.g., missing `"type"`).

## Implementation Considerations

- Use **`pydantic.create_model`** for creating all models.
- Generate deterministic nested-model names using a counter for nested objects.
- Provide clear error messages for schema validation issues.

## Component Dependencies

### Internal Components

- **None**

### External Libraries

- **pydantic** – (Required) Provides `BaseModel` and `create_model`.
- **typing** – (Required) `Any`, `List`, `Optional`, `Type`.

### Configuration Dependencies

None

## Logging

None

## Error Handling

- Raise **`ValueError`** with a clear message when the input schema is invalid or unsupported.
- Include details about the specific validation error in the error message.
- Validate schema types before processing to avoid cryptic errors.

## Dependency Integration Considerations

None

## Output Files

- `utils/models.py`
