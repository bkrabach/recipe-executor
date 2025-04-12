# Recipe Executor UX

A modern, web-based interface for creating, managing, and executing Recipe Executor workflows. This application provides a simple and intuitive UI for working with recipes, with features for creating, editing, executing, and monitoring recipe executions.

## Features

- **Recipe Dashboard**: Browse, search, and manage your recipes
- **Recipe Editor**: Create and edit recipes with a visual editor
- **Step Library**: Add various step types with form-based configuration
- **Execution Monitor**: Track recipe execution in real-time with logs and context inspection

## Architecture

The application follows a simple, integrated architecture:

- **Backend**: Python FastAPI server that manages recipes and executions
- **Frontend**: React with TypeScript for a responsive, interactive UI
- **Integration**: Direct API communication with the server-side Recipe Executor

## Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher
- npm or yarn

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/recipe-executor-ux.git
cd recipe-executor-ux
```

### 2. Set up Python environment and install dependencies

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set up frontend dependencies

```bash
cd frontend
npm install
```

### 4. Build the frontend

```bash
# Development build with watch mode
npm run dev

# Production build
npm run build
```

### 5. Start the server

```bash
# From the project root
python -m app.main
```

The application will be available at http://localhost:8000

## Development

### Backend Development

The backend is built with FastAPI. Key files:

- `app/main.py`: Main application entry point with API routes
- `app/models/`: Data models for API responses
- `app/services/`: Business logic services

To run the backend in development mode with auto-reload:

```bash
uvicorn app.main:app --reload
```

### Frontend Development

The frontend is built with React, TypeScript, and Vite. Key directories:

- `frontend/src/components/`: React components
- `frontend/src/services/`: API service for communication with backend
- `frontend/src/types/`: TypeScript interfaces for API models

To run the frontend in development mode (with API proxying to the backend):

```bash
cd frontend
npm run dev
```

## Recipes Directory

Recipes are stored as JSON files in the `recipes` directory at the project root. Each recipe has a unique ID as its filename.

## Using Recipe Executor UX

### Creating a Recipe

1. From the dashboard, click "Create Recipe"
2. Enter a name and optional description
3. Add steps using the "Add Step" buttons
4. Configure each step's parameters
5. Click "Create Recipe" to save

### Executing a Recipe

1. Open a recipe from the dashboard
2. Click "Execute" to run the recipe
3. Optional: Add context variables for the execution
4. Monitor the execution status, logs, and results

### Viewing Execution Results

1. After starting an execution, you'll be redirected to the execution view
2. Monitor the progress in real-time
3. View logs as they are generated
4. Inspect the final context state when execution completes

## License

[MIT License](LICENSE)
