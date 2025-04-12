import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../services/api';
import { ExecutionStatus } from '../types/api';

const ExecutionView = () => {
    const { id } = useParams<{ id: string }>();

    const [execution, setExecution] = useState<ExecutionStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshInterval, setRefreshInterval] = useState<number | null>(null);

    const fetchExecution = async () => {
        if (!id) return;

        const response = await api.getExecutionStatus(id);

        if (response.error) {
            setError(response.error);
            if (refreshInterval) {
                clearInterval(refreshInterval);
                setRefreshInterval(null);
            }
        } else if (response.data) {
            setExecution(response.data);

            // Stop polling if execution is completed or failed
            if (response.data.status === 'completed' || response.data.status === 'failed') {
                if (refreshInterval) {
                    clearInterval(refreshInterval);
                    setRefreshInterval(null);
                }
            }
        }

        setLoading(false);
    };

    useEffect(() => {
        fetchExecution();

        // Set up polling if execution is active
        const interval = window.setInterval(fetchExecution, 2000);
        setRefreshInterval(interval);

        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    }, [id]);

    const formatDate = (dateString: string) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    const getStatusClass = (status: string): string => {
        switch (status) {
            case 'pending':
                return 'pending';
            case 'running':
                return 'running';
            case 'completed':
                return 'completed';
            case 'failed':
                return 'failed';
            default:
                return '';
        }
    };

    const getStatusText = (status: string): string => {
        switch (status) {
            case 'pending':
                return 'Pending';
            case 'running':
                return 'Running';
            case 'completed':
                return 'Completed';
            case 'failed':
                return 'Failed';
            default:
                return status;
        }
    };

    const calculateProgress = (): number => {
        if (!execution) return 0;

        const { current_step, total_steps, status } = execution;

        if (status === 'completed') return 100;
        if (status === 'pending') return 0;
        if (current_step === undefined || total_steps === 0) return 0;

        return Math.round((current_step / total_steps) * 100);
    };

    if (loading && !execution) {
        return (
            <div className="card">
                <div className="flex items-center justify-center" style={{ minHeight: '200px' }}>
                    <div className="spinner"></div>
                    <span className="ml-2">Loading execution status...</span>
                </div>
            </div>
        );
    }

    if (error || !execution) {
        return (
            <div className="card">
                <div className="text-center" style={{ color: 'var(--error-color)' }}>
                    <p>Error loading execution: {error || 'Execution not found'}</p>
                    <Link to="/recipes" className="btn btn-outline mt-4">
                        Back to Recipes
                    </Link>
                </div>
            </div>
        );
    }

    const progress = calculateProgress();

    return (
        <div>
            <div className="card-header">
                <div>
                    <h2 className="card-title">Execution {id?.substring(0, 8)}</h2>
                    <p className="text-light mt-2">
                        <Link to={`/recipes/${execution.recipe_id}`}>
                            Recipe: {execution.recipe_id}
                        </Link>
                    </p>
                </div>
                <div className="flex gap-2">
                    <Link to={`/recipes/${execution.recipe_id}`} className="btn btn-outline">
                        Back to Recipe
                    </Link>
                    {(execution.status === 'completed' || execution.status === 'failed') && (
                        <button
                            className="btn btn-primary"
                            onClick={fetchExecution}
                        >
                            Refresh
                        </button>
                    )}
                </div>
            </div>

            <div className={`execution-status ${getStatusClass(execution.status)}`}>
                <div className="flex justify-between items-center mb-2">
                    <h3>Status: {getStatusText(execution.status)}</h3>
                    {execution.status === 'running' && (
                        <div className="flex items-center">
                            <div className="spinner mr-2"></div>
                            <span>Executing...</span>
                        </div>
                    )}
                </div>

                <div className="text-sm mb-2">
                    <div>Started: {formatDate(execution.start_time)}</div>
                    {execution.end_time && <div>Ended: {formatDate(execution.end_time)}</div>}
                </div>

                <div className="progress-bar">
                    <div
                        className="progress-bar-fill"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>

                <div className="flex justify-between text-sm mt-1">
                    <div>
                        {execution.current_step !== undefined
                            ? `Step ${execution.current_step + 1} of ${execution.total_steps}`
                            : `${execution.total_steps} steps`}
                    </div>
                    <div>{progress}%</div>
                </div>

                {execution.error && (
                    <div
                        className="mt-4 p-4 rounded"
                        style={{
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            border: '1px solid var(--error-color)'
                        }}
                    >
                        <h4 className="mb-2">Error:</h4>
                        <pre style={{ whiteSpace: 'pre-wrap' }}>{execution.error}</pre>
                    </div>
                )}
            </div>

            <div className="card mt-4">
                <h3 className="mb-2">Execution Logs</h3>
                <div className="log-viewer">
                    {execution.logs.length === 0 ? (
                        <div className="text-light">No logs available</div>
                    ) : (
                        execution.logs.map((log, index) => (
                            <div key={index} className="log-entry">
                                {log}
                            </div>
                        ))
                    )}
                </div>
            </div>

            {execution.context && Object.keys(execution.context).length > 0 && (
                <div className="card mt-4">
                    <h3 className="mb-2">Execution Context</h3>
                    <pre
                        style={{
                            whiteSpace: 'pre-wrap',
                            backgroundColor: '#f8f8f8',
                            padding: '1rem',
                            borderRadius: '4px',
                            maxHeight: '400px',
                            overflow: 'auto'
                        }}
                    >
                        {JSON.stringify(execution.context, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
};

export default ExecutionView;