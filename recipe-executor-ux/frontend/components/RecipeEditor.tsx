import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../services/api';
import { Recipe, RecipeCreate, Step } from '../types/api';
import StepEditor from './StepEditor';

const DEFAULT_STEPS: Record<string, Partial<Step>> = {
    read_files: {
        type: 'read_files',
        path: '',
        artifact: '',
        optional: false,
        merge_mode: 'concat'
    },
    write_files: {
        type: 'write_files',
        artifact: '',
        root: '.'
    },
    generate: {
        type: 'generate',
        prompt: '',
        model: 'openai:o3-mini',
        artifact: 'generated_code'
    },
    execute_recipe: {
        type: 'execute_recipe',
        recipe_path: '',
        context_overrides: {}
    },
    parallel: {
        type: 'parallel',
        substeps: [],
        max_concurrency: 0,
        delay: 0
    }
};

const RecipeEditor = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const isEdit = !!id;

    // Form state
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [steps, setSteps] = useState<Step[]>([]);
    const [tags, setTags] = useState<string[]>([]);
    const [tagInput, setTagInput] = useState('');

    // UI state
    const [loading, setLoading] = useState(isEdit);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRecipe = async () => {
            if (!id) return;

            setLoading(true);
            const response = await api.getRecipe(id);

            if (response.error) {
                setError(response.error);
            } else if (response.data) {
                const recipe = response.data;
                setName(recipe.name);
                setDescription(recipe.description || '');
                setSteps(recipe.steps);
                setTags(recipe.tags);
            }

            setLoading(false);
        };

        if (isEdit) {
            fetchRecipe();
        }
    }, [id, isEdit]);

    const handleAddStep = (type: string) => {
        const newStep: Step = {
            ...DEFAULT_STEPS[type],
            type
        } as Step;

        setSteps([...steps, newStep]);
    };

    const handleUpdateStep = (index: number, updatedStep: Step) => {
        const newSteps = [...steps];
        newSteps[index] = updatedStep;
        setSteps(newSteps);
    };

    const handleRemoveStep = (index: number) => {
        setSteps(steps.filter((_, i) => i !== index));
    };

    const handleMoveStep = (index: number, direction: 'up' | 'down') => {
        if (
            (direction === 'up' && index === 0) ||
            (direction === 'down' && index === steps.length - 1)
        ) {
            return;
        }

        const newSteps = [...steps];
        const targetIndex = direction === 'up' ? index - 1 : index + 1;

        // Swap steps
        [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];

        setSteps(newSteps);
    };

    const handleAddTag = () => {
        if (!tagInput.trim()) return;

        if (!tags.includes(tagInput.trim())) {
            setTags([...tags, tagInput.trim()]);
        }

        setTagInput('');
    };

    const handleRemoveTag = (tag: string) => {
        setTags(tags.filter((t) => t !== tag));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!name.trim()) {
            alert('Recipe name is required');
            return;
        }

        setSaving(true);

        try {
            if (isEdit && id) {
                // Update existing recipe
                const recipeData: Recipe = {
                    id,
                    name: name.trim(),
                    description: description.trim() || undefined,
                    steps,
                    tags,
                    created_at: new Date().toISOString(), // Will be overwritten by server
                    updated_at: new Date().toISOString() // Will be overwritten by server
                };

                const response = await api.updateRecipe(recipeData);

                if (response.error) {
                    setError(response.error);
                    setSaving(false);
                    return;
                }

                navigate(`/recipes/${id}`);
            } else {
                // Create new recipe
                const recipeData: RecipeCreate = {
                    name: name.trim(),
                    description: description.trim() || undefined,
                    steps,
                    tags
                };

                const response = await api.createRecipe(recipeData);

                if (response.error) {
                    setError(response.error);
                    setSaving(false);
                    return;
                }

                navigate(`/recipes/${response.data?.id}`);
            }
        } catch (err) {
            setError('An unexpected error occurred');
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <div className="flex items-center justify-center" style={{ minHeight: '200px' }}>
                    <div className="spinner"></div>
                    <span className="ml-2">Loading recipe...</span>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="card-header">
                <h2 className="card-title">{isEdit ? 'Edit Recipe' : 'Create Recipe'}</h2>
            </div>

            {error && (
                <div
                    className="card mb-4"
                    style={{
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid var(--error-color)'
                    }}
                >
                    <p style={{ color: 'var(--error-color)' }}>{error}</p>
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div className="card mb-4">
                    <div className="form-group">
                        <label htmlFor="name">Recipe Name</label>
                        <input
                            id="name"
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Enter recipe name"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="description">Description (Optional)</label>
                        <textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Describe the purpose of this recipe"
                        />
                    </div>

                    <div className="form-group">
                        <label>Tags</label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={tagInput}
                                onChange={(e) => setTagInput(e.target.value)}
                                placeholder="Enter tag"
                                style={{ flex: 1 }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        handleAddTag();
                                    }
                                }}
                            />
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={handleAddTag}
                            >
                                Add Tag
                            </button>
                        </div>

                        {tags.length > 0 && (
                            <div className="recipe-tags mt-2">
                                {tags.map((tag) => (
                                    <span key={tag} className="tag">
                                        {tag}
                                        <button
                                            type="button"
                                            onClick={() => handleRemoveTag(tag)}
                                            style={{
                                                marginLeft: '4px',
                                                background: 'none',
                                                border: 'none',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            ×
                                        </button>
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="card mb-4">
                    <h3 className="mb-4">Recipe Steps</h3>

                    {steps.length === 0 ? (
                        <p className="text-light mb-4">No steps added yet. Add steps using the buttons below.</p>
                    ) : (
                        steps.map((step, index) => (
                            <StepEditor
                                key={index}
                                step={step}
                                index={index}
                                onUpdate={(updatedStep) => handleUpdateStep(index, updatedStep)}
                                onRemove={() => handleRemoveStep(index)}
                                onMove={(direction) => handleMoveStep(index, direction)}
                                isFirst={index === 0}
                                isLast={index === steps.length - 1}
                            />
                        ))
                    )}

                    <div className="mt-4">
                        <h4 className="mb-2">Add Step</h4>
                        <div className="flex flex-wrap gap-2">
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={() => handleAddStep('read_files')}
                            >
                                Add Read Files
                            </button>
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={() => handleAddStep('write_files')}
                            >
                                Add Write Files
                            </button>
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={() => handleAddStep('generate')}
                            >
                                Add Generate
                            </button>
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={() => handleAddStep('execute_recipe')}
                            >
                                Add Execute Recipe
                            </button>
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={() => handleAddStep('parallel')}
                            >
                                Add Parallel
                            </button>
                        </div>
                    </div>
                </div>

                <div className="flex gap-2 justify-end">
                    <button
                        type="button"
                        className="btn btn-outline"
                        onClick={() => navigate(isEdit ? `/recipes/${id}` : '/recipes')}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={saving}
                    >
                        {saving ? (
                            <>
                                <div className="spinner mr-2"></div>
                                Saving...
                            </>
                        ) : (
                            isEdit ? 'Update Recipe' : 'Create Recipe'
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default RecipeEditor;