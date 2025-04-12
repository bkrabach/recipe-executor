import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Recipe } from '../types/api';

const RecipeList = () => {
    const [recipes, setRecipes] = useState<Recipe[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchRecipes = async () => {
            setLoading(true);
            const response = await api.getRecipes();

            if (response.error) {
                setError(response.error);
            } else if (response.data) {
                setRecipes(response.data.recipes);
            }

            setLoading(false);
        };

        fetchRecipes();
    }, []);

    const handleRecipeClick = (id: string) => {
        navigate(`/recipes/${id}`);
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    if (loading) {
        return (
            <div className="card">
                <div className="flex items-center justify-center" style={{ minHeight: '200px' }}>
                    <div className="spinner"></div>
                    <span className="ml-2">Loading recipes...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card">
                <div className="text-center" style={{ color: 'var(--error-color)' }}>
                    <p>Error loading recipes: {error}</p>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="card-header">
                <h2 className="card-title">Recipes</h2>
                <Link to="/recipes/new" className="btn btn-primary">
                    Create Recipe
                </Link>
            </div>

            {recipes.length === 0 ? (
                <div className="card">
                    <div className="text-center" style={{ padding: '2rem' }}>
                        <p>No recipes found. Create your first recipe to get started!</p>
                        <Link to="/recipes/new" className="btn btn-primary mt-4">
                            Create Recipe
                        </Link>
                    </div>
                </div>
            ) : (
                <div className="recipe-list">
                    {recipes.map((recipe) => (
                        <div
                            key={recipe.id}
                            className="card recipe-card"
                            onClick={() => handleRecipeClick(recipe.id)}
                        >
                            <div className="recipe-card-body">
                                <h3 className="card-title">{recipe.name}</h3>
                                {recipe.description && (
                                    <p className="mt-2 text-light">{recipe.description}</p>
                                )}
                                {recipe.tags.length > 0 && (
                                    <div className="recipe-tags">
                                        {recipe.tags.map((tag) => (
                                            <span key={tag} className="tag">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                                <div className="mt-2">
                                    <span className="text-sm text-light">
                                        {recipe.steps.length} step{recipe.steps.length !== 1 ? 's' : ''}
                                    </span>
                                </div>
                            </div>
                            <div className="recipe-card-footer">
                                <span className="text-sm text-light">
                                    Updated: {formatDate(recipe.updated_at)}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default RecipeList;