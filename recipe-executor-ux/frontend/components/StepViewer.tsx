import { useState } from 'react';
import { Step } from '../types/api';

interface StepViewerProps {
    step: Step;
    index: number;
}

const StepViewer = ({ step, index }: StepViewerProps) => {
    const [expanded, setExpanded] = useState(false);

    // Render different step types accordingly
    const renderStepDetails = () => {
        switch (step.type) {
            case 'read_files':
                return (
                    <>
                        <div className="form-group">
                            <label>Path</label>
                            <div>{Array.isArray(step.path) ? step.path.join(', ') : step.path}</div>
                        </div>
                        <div className="form-group">
                            <label>Artifact</label>
                            <div>{step.artifact}</div>
                        </div>
                        {step.optional !== undefined && (
                            <div className="form-group">
                                <label>Optional</label>
                                <div>{step.optional ? 'Yes' : 'No'}</div>
                            </div>
                        )}
                        {step.merge_mode && (
                            <div className="form-group">
                                <label>Merge Mode</label>
                                <div>{step.merge_mode}</div>
                            </div>
                        )}
                    </>
                );

            case 'write_files':
                return (
                    <>
                        <div className="form-group">
                            <label>Artifact</label>
                            <div>{step.artifact}</div>
                        </div>
                        {step.root && (
                            <div className="form-group">
                                <label>Root</label>
                                <div>{step.root}</div>
                            </div>
                        )}
                    </>
                );

            case 'generate':
                return (
                    <>
                        <div className="form-group">
                            <label>Model</label>
                            <div>{step.model}</div>
                        </div>
                        <div className="form-group">
                            <label>Artifact</label>
                            <div>{step.artifact}</div>
                        </div>
                        <div className="form-group">
                            <label>Prompt</label>
                            <pre style={{
                                whiteSpace: 'pre-wrap',
                                backgroundColor: '#f8f8f8',
                                padding: '0.5rem',
                                borderRadius: '4px',
                                maxHeight: '200px',
                                overflow: 'auto'
                            }}>
                                {step.prompt}
                            </pre>
                        </div>
                    </>
                );

            case 'execute_recipe':
                return (
                    <>
                        <div className="form-group">
                            <label>Recipe Path</label>
                            <div>{step.recipe_path}</div>
                        </div>
                        {step.context_overrides && Object.keys(step.context_overrides).length > 0 && (
                            <div className="form-group">
                                <label>Context Overrides</label>
                                <pre style={{
                                    whiteSpace: 'pre-wrap',
                                    backgroundColor: '#f8f8f8',
                                    padding: '0.5rem',
                                    borderRadius: '4px'
                                }}>
                                    {JSON.stringify(step.context_overrides, null, 2)}
                                </pre>
                            </div>
                        )}
                    </>
                );

            case 'parallel':
                return (
                    <>
                        <div className="form-group">
                            <label>Substeps</label>
                            <div>{step.substeps?.length || 0} substep(s)</div>
                        </div>
                        {step.max_concurrency !== undefined && (
                            <div className="form-group">
                                <label>Max Concurrency</label>
                                <div>{step.max_concurrency || 'No limit'}</div>
                            </div>
                        )}
                        {step.delay !== undefined && (
                            <div className="form-group">
                                <label>Delay</label>
                                <div>{step.delay}s</div>
                            </div>
                        )}
                        {expanded && step.substeps && step.substeps.length > 0 && (
                            <div className="ml-4 mt-4 border-l-2 pl-4" style={{ borderColor: 'var(--border-color)' }}>
                                <h4 className="mb-2">Substeps:</h4>
                                {step.substeps.map((substep, subIndex) => (
                                    <StepViewer key={subIndex} step={substep} index={subIndex} />
                                ))}
                            </div>
                        )}
                    </>
                );

            default:
                return (
                    <div className="form-group">
                        <pre style={{
                            whiteSpace: 'pre-wrap',
                            backgroundColor: '#f8f8f8',
                            padding: '0.5rem',
                            borderRadius: '4px'
                        }}>
                            {JSON.stringify(step, null, 2)}
                        </pre>
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
                <button
                    className="btn btn-sm btn-outline"
                    onClick={() => setExpanded(!expanded)}
                >
                    {expanded ? 'Collapse' : 'Expand'}
                </button>
            </div>

            {expanded && renderStepDetails()}
        </div>
    );
};

export default StepViewer;