from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, create_model

__all__ = ["json_object_to_pydantic_model"]


def json_object_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]:
    """
    Convert a JSON object dictionary into a dynamic Pydantic model.
    Args:
        schema: A valid JSON-Schema fragment describing an object.
        model_name: Name given to the generated model class.
    Returns:
        A subclass of `pydantic.BaseModel` suitable for validation & serialization.
    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary.")
    if "type" not in schema:
        raise ValueError('Schema missing required "type" property.')
    if schema["type"] != "object":
        raise ValueError('Root schema type must be "object".')

    properties: Dict[str, Any] = schema.get("properties", {})
    required_fields: List[str] = schema.get("required", [])

    if not isinstance(properties, dict):
        raise ValueError('Schema "properties" must be a dictionary if present.')
    if not isinstance(required_fields, list):
        raise ValueError('Schema "required" must be a list if present.')

    # Nested object counter, used for deterministic model naming
    class NestedCounter:
        def __init__(self):
            self.count = 0

        def next(self) -> int:
            self.count += 1
            return self.count

    nested_counter = NestedCounter()

    def parse_schema_field(field_schema: Dict[str, Any], field_name: str, parent_model_name: str) -> Tuple[Any, Any]:
        """
        Returns (type_annotation, default_value)
        """
        # Check for valid 'type'
        field_type = field_schema.get("type")
        if not field_type:
            raise ValueError(f'Schema for field "{field_name}" missing required "type" property.')
        # Primitive types
        if field_type == "string":
            return str, ...
        if field_type == "integer":
            return int, ...
        if field_type == "number":
            return float, ...
        if field_type == "boolean":
            return bool, ...
        if field_type == "object":
            # Recursively create nested model
            next_count = nested_counter.next()
            nested_name = f"{parent_model_name}_{field_name.capitalize()}Obj{next_count}"
            nested_model = _create_model_from_schema(field_schema, nested_name)
            return nested_model, ...
        if field_type in ("array", "list"):
            items_schema = field_schema.get("items")
            if not isinstance(items_schema, dict):
                # items must be present for arrays
                raise ValueError(f'Array field "{field_name}" missing valid "items" schema.')
            item_type, _ = parse_schema_field(items_schema, f"{field_name}_item", parent_model_name)
            return List[item_type], ...
        # Fallback for unsupported/unknown type
        return Any, ...

    def parse_optional_schema_field(
        field_schema: Dict[str, Any], is_required: bool, field_name: str, parent_model_name: str
    ) -> Tuple[Any, Any]:
        # Adjust required/optional
        type_annotation, default_val = parse_schema_field(field_schema, field_name, parent_model_name)
        if not is_required:
            type_annotation = Optional[type_annotation]
            default_val = None
        return type_annotation, default_val

    def _create_model_from_schema(object_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
        if not isinstance(object_schema, dict):
            raise ValueError("Nested schema must be a dictionary.")
        if object_schema.get("type") != "object":
            raise ValueError(f'Nested schema "{name}" type must be "object".')
        object_properties: Dict[str, Any] = object_schema.get("properties", {})
        object_required: List[str] = object_schema.get("required", [])
        if not isinstance(object_properties, dict):
            raise ValueError(f'Nested schema "{name}" "properties" must be a dictionary if present.')
        if not isinstance(object_required, list):
            raise ValueError(f'Nested schema "{name}" "required" must be a list if present.')
        fields: Dict[str, Tuple[Any, Any]] = {}
        for prop_name, prop_schema in object_properties.items():
            is_required = prop_name in object_required
            field_type, default = parse_optional_schema_field(prop_schema, is_required, prop_name, name)
            fields[prop_name] = (field_type, default)
        return create_model(name, **fields)  # type: ignore

    model: Type[BaseModel] = _create_model_from_schema(schema, model_name)
    return model
