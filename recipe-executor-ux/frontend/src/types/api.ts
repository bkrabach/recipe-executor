// API Models matching our backend Pydantic models

// Step model
export interface Step {
    type: string;
    path?: string;
    artifact?: string;
    prompt?: string;
    model?: string;
    root?: string;
    recipe_path?: string;
    context_overrides?: Record<string, string>;
    substeps?: Step[];
    optional?: boolean;
    merge_mode?: string;
    [key: string]: any; // Allow additional properties
}

// Recipe models
export interface RecipeCreate {
    name: string;
    description?: string;
    steps: Step[];
    tags: string[];
}

export interface Recipe extends RecipeCreate {
    id: string;
    created_at: string;
    updated_at: string;
}

export interface RecipeList {
    recipes: Recipe[];
}

// Execution models
export interface ExecutionStatus {
    execution_id: string;
    recipe_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    start_time: string;
    end_time?: string;
    current_step?: number;
    total_steps: number;
    logs: string[];
    context?: Record<string, any>;
    error?: string;
}

// API responses
export interface ApiResponse<T> {
    data?: T;
    error?: string;
}

export interface ExecuteResponse {
    status: string;
    execution_id: string;
    message: string;
}