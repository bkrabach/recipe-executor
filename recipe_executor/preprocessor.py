"""
Recipe preprocessor for the Recipe Executor CLI tool.

This module is responsible for parsing a Markdown recipe file and converting it
into a validated Recipe model using an LLM. It builds a dynamic system prompt
based on the available step types in the registry.
"""

import logging
from typing import List, Optional

from pydantic import BaseModel, ValidationError
from pydantic_ai import Agent

from recipe_executor.models import Recipe
from recipe_executor.registry import STEP_REGISTRY
from recipe_executor.config import PREPROCESSOR_MODEL
from recipe_executor.llm import get_model


class StepSchema(BaseModel):
    """
    Schema for individual steps as output by the LLM.
    """
    type: str
    name: Optional[str] = None

    class Config:
        extra = "allow"


class RecipeSchema(BaseModel):
    """
    Schema for the overall recipe as output by the LLM.
    """
    title: str
    description: Optional[str] = None
    steps: List[StepSchema]

    class Config:
        extra = "forbid"


def build_dynamic_system_prompt() -> str:
    """
    Build a dynamic system prompt using the registered step types.

    Returns:
        A string containing system instructions for the LLM.
    """
    lines = [
        "You are a recipe parsing assistant.",
        "Convert the Markdown recipe into JSON matching the following structure:",
        "- Keys: title (str), description (optional), steps (list of structured steps)",
        "",
        "Each step must have:",
        "- type: the name of the step type",
        "- other fields depending on the step type",
        "",
        "Available step types and their expected fields:"
    ]

    for step_type, cls in STEP_REGISTRY.items():
        lines.append(f"- type: '{step_type}'")
        for field_name, field_info in cls.model_fields.items():
            if field_name == "type":
                continue
            type_name = getattr(field_info.annotation, '__name__', 'Any')
            lines.append(f"    - {field_name}: {type_name}")
        lines.append("")  # Add spacing between step definitions

    lines.append("Output only valid JSON. Do not include explanations.")
    return "\n".join(lines)


def parse_recipe(markdown_path: str) -> Recipe:
    """
    Parse a Markdown recipe file into a validated Recipe model.

    Args:
        markdown_path: The path to the Markdown file containing the recipe.

    Returns:
        A validated Recipe object.

    Raises:
        Exception: If the file cannot be read, the LLM agent fails to initialize or run,
                   or if the output does not validate.
    """
    try:
        with open(markdown_path, "r") as f:
            markdown = f.read()
    except Exception as e:
        raise Exception(f"Failed to read recipe file '{markdown_path}': {e}") from e

    system_instructions = build_dynamic_system_prompt()
    model_id = PREPROCESSOR_MODEL

    try:
        agent: Agent[None, RecipeSchema] = Agent(
            get_model(model_id),
            result_type=RecipeSchema,
            system_prompt=system_instructions
        )
    except Exception as e:
        raise Exception(f"Error initializing LLM agent: {e}") from e

    try:
        result = agent.run_sync(markdown)
    except Exception as e:
        raise Exception(f"Error during LLM parsing: {e}") from e

    if not result or result.data is None:
        raise Exception("LLM returned no result.")

    raw_recipe = result.data
    logging.debug("Preprocessor raw output: %s", raw_recipe.model_dump_json() if hasattr(raw_recipe, "json") else raw_recipe)

    parsed_steps = []

    for step_data in raw_recipe.steps:
        step_type = step_data.type
        if step_type not in STEP_REGISTRY:
            raise Exception(f"Unknown step type: '{step_type}'")

        step_cls = STEP_REGISTRY[step_type]
        try:
            step_obj = step_cls.model_validate(step_data.model_dump())
        except ValidationError as e:
            raise Exception(f"Step validation failed for type '{step_type}': {e}") from e

        parsed_steps.append(step_obj)

    return Recipe(
        title=raw_recipe.title,
        description=raw_recipe.description,
        steps=parsed_steps
    )
