import { useState } from 'react';
import { Step } from '../types/api';

interface StepEditorProps {
    step: Step;
    index: number;
    onUpdate: (step: Step) => void;
    onRemove: () => void;
    onMove: (direction: 'up' | 'down') => void;
    isFirst: boolean;
    isLast: boolean;
}

const StepEditor = ({
    step,
    index,
    onUpdate,
    onRemove,
    onMove,
    isFirst,
    isLast
}: StepEditorProps) => {
    const [expanded, setExpanded] = useState(true);

    const handleChange = (field: string, value: any) => {
        onUpdate({
            ...step,
            [field]: value
        });
    };

    const renderContextOverrides = () => {
        const overrides = step.context_overrides || {};

        return (
            <div className="form-group">
                <label>Context Overrides</label>
                <div>
                    {Object.keys(overrides).length === 0 && (
                        <div className="text-light mb-2">No context overrides defined.</div>
                    )}

                    {Object.entries(overrides).map(([key, value]) => (
                        <div key={key} className="flex gap-2 mb-2">
                            <input
                                type="text"
                                value={key}
                                onChange={(e) => {
                                    const newOverrides = { ...overrides };
                                    delete newOverrides[key];
                                    newOverrides[e.target.value] = value;
                                    handleChange('context_overrides', newOverrides);
                                }}
                                placeholder="Key"
                                style={{ flex: 1 }}
                            />
                            <input
                                type="text"
                                value={value}
                                onChange={(e) => {
                                    const newOverrides = { ...overrides };
                                    newOverrides[key] = e.target.value;
                                    handleChange('context_overrides', newOverrides);
                                }}
                                placeholder="Value"
                                style={{ flex: 2 }}
                            />
                            <button
                                type="button"
                                className="btn btn-sm btn-outline btn-danger"
                                onClick={() => {
                                    const newOverrides = { ...overrides };
                                    delete newOverrides[key];
                                    handleChange('context_overrides', newOverrides);
                                }}
                            >
                                Remove
                            </button>
                        </div>
                    ))}

                    <button
                        type="button"
                        className="btn btn-sm btn-outline"
                        onClick={() => {
                            const newKey = `key_${Object.keys(overrides).length}`;
                            handleChange('context_overrides', {
                                ...overrides,
                                [newKey]: ''
                            });
                        }}
                    >
                        Add Override
                    </button>
                </div>
            </div>
        );
    };

    const renderSubsteps = () => {
        const substeps = step.substeps || [];

        const addSubstep = (type: string) => {
            const newSubstep: Step = {
                type,
                // Add default fields based on type
                ...(type === 'execute_recipe' ? { recipe_path: '', context_overrides: {} } : {})
            };

            handleChange('substeps', [...substeps, newSubstep]);
        };

        const updateSubstep = (index: number, updatedSubstep: Step) => {
            const newSubsteps = [...substeps];
            newSubsteps[index] = updatedSubstep;
            handleChange('substeps', newSubsteps);
        };

        const removeSubstep = (index: number) => {
            handleChange('substeps', substeps.filter((_, i) => i !== index));
        };

        return (
            <div className="form-group">
                <label>Substeps</label>
                <div>
                    {substeps.length === 0 && (
                        <div className="text-light mb-2">No substeps defined.</div>
                    )}

                    {substeps.map((substep, idx) => (
                        <div
                            key={idx}
                            className="mb-2 p-2 border rounded"
                            style={{ borderColor: 'var(--border-color)' }}
                        >
                            <div className="flex justify-between items-center mb-2">
                                <h4>{idx + 1}. {substep.type}</h4>
                                <button
                                    type="button"
                                    className="btn btn-sm btn-outline btn-danger"
                                    onClick={() => removeSubstep(idx)}
                                >
                                    Remove
                                </button>
                            </div>

                            {substep.type === 'execute_recipe' && (
                                <div>
                                    <div className="form-group">
                                        <label>Recipe Path</label>
                                        <input
                                            type="text"
                                            value={substep.recipe_path || ''}
                                            onChange={(e) => {
                                                updateSubstep(idx, {
                                                    ...substep,
                                                    recipe_path: e.target.value
                                                });
                                            }}
                                            placeholder="Path to recipe"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Context Overrides</label>
                                        <div>
                                            {Object.entries(substep.context_overrides || {}).map(([key, value]) => (
                                                <div key={key} className="flex gap-2 mb-2">
                                                    <input
                                                        type="text"
                                                        value={key}
                                                        onChange={(e) => {
                                                            const newOverrides = { ...substep.context_overrides };
                                                            delete newOverrides[key];
                                                            newOverrides[e.target.value] = value;
                                                            updateSubstep(idx, {
                                                                ...substep,
                                                                context_overrides: newOverrides
                                                            });
                                                        }}
                                                        placeholder="Key"
                                                        style={{ flex: 1 }}
                                                    />
                                                    <input
                                                        type="text"
                                                        value={value}
                                                        onChange={(e) => {
                                                            updateSubstep(idx, {
                                                                ...substep,
                                                                context_overrides: {
                                                                    ...substep.context_overrides,
                                                                    [key]: e.target.value
                                                                }
                                                            });
                                                        }}
                                                        placeholder="Value"
                                                        style={{ flex: 2 }}
                                                    />
                                                    <button
                                                        type="button"
                                                        className="btn btn-sm btn-outline btn-danger"
                                                        onClick={() => {
                                                            const newOverrides = { ...substep.context_overrides };
                                                            delete newOverrides[key];
                                                            updateSubstep(idx, {
                                                                ...substep,
                                                                context_overrides: newOverrides
                                                            });
                                                        }}
                                                    >
                                                        Remove
                                                    </button>
                                                </div>
                                            ))}

                                            <button
                                                type="button"
                                                className="btn btn-sm btn-outline"
                                                onClick={() => {
                                                    const newKey = `key_${Object.keys(substep.context_overrides || {}).length}`;
                                                    updateSubstep(idx, {
                                                        ...substep,
                                                        context_overrides: {
                                                            ...substep.context_overrides,
                                                            [newKey]: ''
                                                        }
                                                    });
                                                }}
                                            >
                                                Add Override
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}

                    <button
                        type="button"
                        className="btn btn-sm btn-outline"
                        onClick={() => addSubstep('execute_recipe')}
                    >
                        Add Execute Recipe Substep
                    </button>
                </div>
            </div>
        );
    };

    // Render form fields based on step type
    const renderStepFields = () => {
        switch (step.type) {
            case 'read_files':
                return (
                    <>
                        <div className="form-group">
                            <label>Path</label>
                            <input
                                type="text"
                                value={Array.isArray(step.path) ? step.path.join(', ') : step.path || ''}
                                onChange={(e) => {
                                    // Check if it contains commas
                                    const value = e.target.value;
                                    if (value.includes(',')) {
                                        handleChange('path', value.split(',').map(p => p.trim()));
                                    } else {
                                        handleChange('path', value);
                                    }
                                }}
                                placeholder="File path or comma-separated paths"
                            />
                        </div>
                        <div className="form-group">
                            <label>Artifact</label>
                            <input
                                type="text"
                                value={step.artifact || ''}
                                onChange={(e) => handleChange('artifact', e.target.value)}
                                placeholder="Context key to store content"
                            />
                        </div>
                        <div className="form-group">
                            <label>Optional</label>
                            <select
                                value={step.optional ? 'true' : 'false'}
                                onChange={(e) => handleChange('optional', e.target.value === 'true')}
                            >
                                <option value="false">No</option>
                                <option value="true">Yes</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Merge Mode</label>
                            <select
                                value={step.merge_mode || 'concat'}
                                onChange={(e) => handleChange('merge_mode', e.target.value)}
                            >
                                <option value="concat">Concatenate</option>
                                <option value="dict">Dictionary</option>
                            </select>
                        </div>
                    </>
                );

            case 'write_files':
                return (
                    <>
                        <div className="form-group">
                            <label>Artifact</label>
                            <input
                                type="text"
                                value={step.artifact || ''}
                                onChange={(e) => handleChange('artifact', e.target.value)}
                                placeholder="Context key with file content"
                            />
                        </div>
                        <div className="form-group">
                            <label>Root</label>
                            <input
                                type="text"
                                value={step.root || '.'}
                                onChange={(e) => handleChange('root', e.target.value)}
                                placeholder="Root directory"
                            />
                        </div>
                    </>
                );

            case 'generate':
                return (
                    <>
                        <div className="form-group">
                            <label>Model</label>
                            <input
                                type="text"
                                value={step.model || 'openai:o3-mini'}
                                onChange={(e) => handleChange('model', e.target.value)}
                                placeholder="Model identifier (e.g., openai:o3-mini)"
                            />
                        </div>
                        <div className="form-group">
                            <label>Artifact</label>
                            <input
                                type="text"
                                value={step.artifact || 'generated_code'}
                                onChange={(e) => handleChange('artifact', e.target.value)}
                                placeholder="Context key to store result"
                            />
                        </div>
                        <div className="form-group">
                            <label>Prompt</label>
                            <textarea
                                value={step.prompt || ''}
                                onChange={(e) => handleChange('prompt', e.target.value)}
                                placeholder="Prompt for the model"
                                style={{ minHeight: '150px' }}
                            />
                        </div>
                    </>
                );

            case 'execute_recipe':
                return (
                    <>
                        <div className="form-group">
                            <label>Recipe Path</label>
                            <input
                                type="text"
                                value={step.recipe_path || ''}
                                onChange={(e) => handleChange('recipe_path', e.target.value)}
                                placeholder="Path to recipe file"
                            />
                        </div>
                        {renderContextOverrides()}
                    </>
                );

            case 'parallel':
                return (
                    <>
                        <div className="form-group">
                            <label>Max Concurrency</label>
                            <input
                                type="number"
                                value={step.max_concurrency || 0}
                                onChange={(e) => handleChange('max_concurrency', parseInt(e.target.value) || 0)}
                                placeholder="0 for unlimited"
                            />
                            <span className="text-light text-sm">0 means unlimited</span>
                        </div>
                        <div className="form-group">
                            <label>Delay</label>
                            <input
                                type="number"
                                value={step.delay || 0}
                                onChange={(e) => handleChange('delay', parseFloat(e.target.value) || 0)}
                                step="0.1"
                                placeholder="Delay in seconds"
                            />
                            <span className="text-light text-sm">Delay between substeps in seconds</span>
                        </div>
                        {renderSubsteps()}
                    </>
                );

            default:
                return (
                    <div className="form-group">
                        <label>Step Configuration</label>
                        <textarea
                            value={JSON.stringify(step, null, 2)}
                            onChange={(e) => {
                                try {
                                    const parsed = JSON.parse(e.target.value);
                                    onUpdate(parsed);
                                } catch (error) {
                                    // Ignore parse errors while typing
                                }
                            }}
                            style={{ fontFamily: 'monospace', minHeight: '200px' }}
                        />
                    </div>
                );
        }
    };

    return (
        <div className="step-editor mb-4">
            <div className="step-header">
                <h4>
                    {index + 1}. {step.type}
                </h4>
                <div className="step-actions">
                    <button
                        type="button"
                        className="btn btn-sm btn-outline"
                        onClick={() => setExpanded(!expanded)}
                    >
                        {expanded ? 'Collapse' : 'Expand'}
                    </button>
                    {!isFirst && (
                        <button
                            type="button"
                            className="btn btn-sm btn-outline"
                            onClick={() => onMove('up')}
                        >
                            ↑
                        </button>
                    )}
                    {!isLast && (
                        <button
                            type="button"
                            className="btn btn-sm btn-outline"
                            onClick={() => onMove('down')}
                        >
                            ↓
                        </button>
                    )}
                    <button
                        type="button"
                        className="btn btn-sm btn-outline btn-danger"
                        onClick={onRemove}
                    >
                        Remove
                    </button>
                </div>
            </div>

            {expanded && renderStepFields()}
        </div>
    );
};

export default StepEditor;