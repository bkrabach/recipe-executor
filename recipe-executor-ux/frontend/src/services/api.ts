import { ApiResponse, ExecuteResponse, ExecutionStatus, Recipe, RecipeCreate, RecipeList } from '../types/api';

const API_BASE = '/api';

/**
 * Simple API client for the Recipe Executor backend
 */
export const api = {
    // Recipe endpoints

    /**
     * Get a list of all recipes
     */
    async getRecipes(): Promise<ApiResponse<RecipeList>> {
        try {
            const response = await fetch(`${API_BASE}/recipes`);
            if (!response.ok) {
                const errorData = await response.json();
                return { error: errorData.detail || 'Failed to fetch recipes' };
            }
            const data = await response.json();
            return { data };
        } catch (error) {
            return { error: `Error fetching recipes: ${error}` };
        }
    },

    /**
     * Get a single recipe by ID
     */
    async getRecipe(id: string): Promise<ApiResponse<Recipe>> {
        try {
            const response = await fetch(`${API_BASE}/recipes/${id}`);
            if (!response.ok) {
                const errorData = await response.json();
                return { error: errorData.detail || `Failed to fetch recipe ${id}` };
            }
            const data = await response.json();
            return { data };
        } catch (error) {
            return { error: `Error fetching recipe ${id}: ${error}` };
        }
    },

    /**
     * Create a new recipe
     */
    async createRecipe(recipe: RecipeCreate): Promise<ApiResponse<Recipe>> {
        try {
            const response = await fetch(`${API_BASE}/recipes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(recipe),
            });

            if (!response.ok) {
                const errorData = await response.json();
                return { error: errorData.detail || 'Failed to create recipe' };
            }

            const data = await response.json();
            return { data };
        } catch (error) {
            return { error: `Error creating recipe: ${error}` };
        }
    },

    /**
     * Update an existing recipe
     */
    async updateRecipe(recipe: Recipe): Promise<ApiResponse<Recipe>> {
        try {
            const response = await fetch(`${API_BASE}/recipes/${recipe.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(recipe),
            });

            if (!response.ok) {
                const errorData = await response.json();
                return { error: errorData.detail || `Failed to update recipe ${recipe.id}` };
            }

            const data = await response.json();
            return { data };
        } catch (error) {
            return { error: `Error updating recipe ${recipe.id}: ${error}` };
        }
    },

    /**
     * Delete a recipe
     */
    async deleteRecipe(id: string): Promise<ApiResponse<{ status: string }>> {
        try {
            const response = await fetch(`${API_BASE}/recipes/${id}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorData = await response.json();
                return { error: errorData.detail || `Failed to delete recipe ${id}` };
            }

            const data = await response.json();
            return { data };
        } catch (error) {
            return { error: `Error deleting recipe ${id}: ${error}` };
        }
    },

    // Execution endpoints

    /**
     * Execute a recipe
     */
    async executeRecipe(id: string, context?: Record<string, string>): Promise<ApiResponse<ExecuteResponse>> {
        try {
            const response = await fetch(`${API_BASE}/recipes/${id}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(context || {}),
            });

            if (!response.ok) {
                const errorData = await response.json();
                return { error: errorData.detail || `Failed to execute recipe ${id}` };
            }

            const data = await response.json();
            return { data };
        } catch (error) {
            return { error: `Error executing recipe ${id}: ${error}` };
        }
    },

    /**
     * Get execution status
     */
    async getExecutionStatus(executionId: string): Promise<ApiResponse<ExecutionStatus>> {
        try {
            const response = await fetch(`${API_BASE}/executions/${executionId}`);

            if (!response.ok) {
                const errorData = await response.json();
                return { error: errorData.detail || `Failed to get execution status ${executionId}` };
            }

            const data = await response.json();
            return { data };
        } catch (error) {
            return { error: `Error getting execution status ${executionId}: ${error}` };
        }
    },
};