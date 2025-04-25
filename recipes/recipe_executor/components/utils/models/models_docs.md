# Pydantic-Model Utilities

## Importing

```python
from recipe_executor.utils.models import json_schema_object_to_pydantic_model
```

## Conversion from JSON Object to Pydantic

This utility function converts a JSON object definition into a Pydantic model. It
allows you to define an object as a JSON-Schema fragment and then generate a strongly-typed
Pydantic model that can be used for data validation and serialization.

The generated model will have fields corresponding to the properties defined in the
JSON-Schema. The types of the fields will be inferred from the JSON-Schema types.

```python
def json_object_to_pydantic_model(
    object_schema: Dict[str, Any],
    model_name: str = "SchemaModel"
) -> Type[pydantic.BaseModel]:
    """
    Convert a JSON object dictionary into a dynamic Pydantic model.

    Args:
        object_schema: A valid JSON-Schema fragment describing an object.
        model_name: Name given to the generated model class.

    Returns:
        A subclass of `pydantic.BaseModel` suitable for validation & serialization.

    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
```

Basic usage example:

```python
from recipe_executor.utils.models import json_object_to_pydantic_model

user_schema = {
    "type": "object",
    "properties": {
        "name":  {"type": "string"},
        "age":   {"type": "integer"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}

User = json_object_to_pydantic_model(user_schema, model_name="User")

instance = User(name="Alice", age=30, email="alice@example.com")
print(instance.model_dump())      # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
```

NOTE: An **object** is required at the root level of the schema. If the root type is not an object, a `ValueError` will be raised.
