import logging
from typing import Dict, Optional

import uvicorn
from app.models.recipe import Recipe, RecipeCreate, RecipeList
from app.services.executor_service import ExecutorService
from app.services.recipe_service import RecipeService
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recipe-executor-ux")

# Create FastAPI app
app = FastAPI(title="Recipe Executor UX")

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services
recipe_service = RecipeService(recipes_dir="recipes")
executor_service = ExecutorService()


# Routes
@app.get("/")
async def index(request: Request):
    """Serve the main application HTML"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/recipes", response_model=RecipeList)
async def list_recipes():
    """List all available recipes"""
    try:
        recipes = recipe_service.list_recipes()
        return RecipeList(recipes=recipes)
    except Exception as e:
        logger.error(f"Error listing recipes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    """Get a specific recipe by ID"""
    try:
        recipe = recipe_service.get_recipe(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recipes", response_model=Recipe)
async def create_recipe(recipe: RecipeCreate):
    """Create a new recipe"""
    try:
        new_recipe = recipe_service.create_recipe(recipe)
        return new_recipe
    except Exception as e:
        logger.error(f"Error creating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/recipes/{recipe_id}", response_model=Recipe)
async def update_recipe(recipe_id: str, recipe: Recipe):
    """Update an existing recipe"""
    try:
        if recipe_id != recipe.id:
            raise HTTPException(status_code=400, detail="Recipe ID mismatch")

        updated_recipe = recipe_service.update_recipe(recipe)
        if not updated_recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return updated_recipe
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/recipes/{recipe_id}")
async def delete_recipe(recipe_id: str):
    """Delete a recipe"""
    try:
        success = recipe_service.delete_recipe(recipe_id)
        if not success:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return {"status": "success", "message": f"Recipe {recipe_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recipes/{recipe_id}/execute")
async def execute_recipe(recipe_id: str, context: Optional[Dict[str, str]] = None):
    """Execute a recipe with optional context variables"""
    try:
        recipe = recipe_service.get_recipe(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        context_dict = context or {}
        execution_id = executor_service.execute_recipe(recipe, context_dict)
        return {"status": "success", "execution_id": execution_id, "message": f"Recipe {recipe_id} execution started"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get the status of a recipe execution"""
    try:
        status = executor_service.get_execution_status(execution_id)
        if not status:
            raise HTTPException(status_code=404, detail="Execution not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution status {execution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
