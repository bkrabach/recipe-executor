# recipe_executor/steps/run_recipe.py

def execute(step, context):
    """
    Execute a run_recipe step: load and run another recipe file, then return to parent.
    The sub-recipe is executed with the current context (allowing it to use and augment it).
    """
    recipe_name = step.recipe
    # Import parser and executor here to avoid circular dependencies
    from recipe_executor import parser, executor
    # Parse the sub-recipe and execute it using the same context
    sub_recipe = parser.parse_recipe(recipe_name)
    executor.execute_recipe(sub_recipe, context)
    # After execution, context now includes any outputs from the sub-recipe.
    # We return a simple acknowledgment (the parent executor may log this).
    return {"recipe_executed": recipe_name}
