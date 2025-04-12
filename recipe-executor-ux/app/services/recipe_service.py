import json
import logging
import os
from datetime import datetime
from typing import List, Optional

from app.models.recipe import Recipe, RecipeCreate

logger = logging.getLogger("recipe-executor-ux")


class RecipeService:
    """Service for managing recipe files"""

    def __init__(self, recipes_dir: str):
        """Initialize with the recipes directory path"""
        self.recipes_dir = recipes_dir

        # Create recipes directory if it doesn't exist
        if not os.path.exists(recipes_dir):
            os.makedirs(recipes_dir)
            logger.info(f"Created recipes directory: {recipes_dir}")

    def list_recipes(self) -> List[Recipe]:
        """List all recipes in the recipes directory"""
        recipes = []

        # Iterate through .json files in recipes directory
        for filename in os.listdir(self.recipes_dir):
            if filename.endswith(".json"):
                try:
                    recipe_path = os.path.join(self.recipes_dir, filename)
                    with open(recipe_path, "r") as f:
                        recipe_data = json.load(f)

                    # Convert to Recipe model
                    recipe = Recipe(**recipe_data)
                    recipes.append(recipe)
                except Exception as e:
                    logger.error(f"Error loading recipe {filename}: {str(e)}")

        # Sort by updated_at (newest first)
        recipes.sort(key=lambda r: r.updated_at, reverse=True)
        return recipes

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID"""
        recipe_path = os.path.join(self.recipes_dir, f"{recipe_id}.json")

        if not os.path.exists(recipe_path):
            return None

        try:
            with open(recipe_path, "r") as f:
                recipe_data = json.load(f)

            return Recipe(**recipe_data)
        except Exception as e:
            logger.error(f"Error loading recipe {recipe_id}: {str(e)}")
            return None

    def create_recipe(self, recipe_create: RecipeCreate) -> Recipe:
        """Create a new recipe"""
        # Generate a new Recipe with ID and timestamps
        recipe = Recipe.create_new(recipe_create)

        # Save to file
        recipe_path = os.path.join(self.recipes_dir, f"{recipe.id}.json")
        with open(recipe_path, "w") as f:
            f.write(recipe.json(indent=2))

        logger.info(f"Created recipe: {recipe.id} - {recipe.name}")
        return recipe

    def update_recipe(self, recipe: Recipe) -> Optional[Recipe]:
        """Update an existing recipe"""
        # Check if recipe exists
        recipe_path = os.path.join(self.recipes_dir, f"{recipe.id}.json")
        if not os.path.exists(recipe_path):
            return None

        # Update timestamp
        recipe.updated_at = datetime.now()

        # Save to file
        with open(recipe_path, "w") as f:
            f.write(recipe.json(indent=2))

        logger.info(f"Updated recipe: {recipe.id} - {recipe.name}")
        return recipe

    def delete_recipe(self, recipe_id: str) -> bool:
        """Delete a recipe"""
        recipe_path = os.path.join(self.recipes_dir, f"{recipe_id}.json")

        if not os.path.exists(recipe_path):
            return False

        try:
            os.remove(recipe_path)
            logger.info(f"Deleted recipe: {recipe_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting recipe {recipe_id}: {str(e)}")
            return False
