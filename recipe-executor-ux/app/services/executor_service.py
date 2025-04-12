import logging
import os
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Optional

from app.models.recipe import ExecutionStatus, Recipe

from recipe_executor.context import Context
from recipe_executor.executor import Executor

logger = logging.getLogger("recipe-executor-ux")


class ExecutorService:
    """Service for executing recipes"""

    def __init__(self):
        """Initialize the executor service"""
        self.executions: Dict[str, ExecutionStatus] = {}
        self.executor = Executor()

        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def execute_recipe(self, recipe: Recipe, context_vars: Optional[Dict[str, str]] = None) -> str:
        """
        Execute a recipe asynchronously and return the execution ID

        Args:
            recipe: The recipe to execute
            context_vars: Optional context variables

        Returns:
            str: The execution ID
        """
        # Generate unique execution ID
        execution_id = str(uuid.uuid4())

        # Setup execution status
        status = ExecutionStatus(
            execution_id=execution_id,
            recipe_id=recipe.id,
            status="pending",
            start_time=datetime.now(),
            end_time=None,
            current_step=None,
            context=None,
            error=None,
            total_steps=len(recipe.steps),
            logs=[],
        )

        # Store execution status
        self.executions[execution_id] = status

        # Start execution in background thread
        thread = threading.Thread(target=self._execute_recipe_thread, args=(execution_id, recipe, context_vars or {}))
        thread.daemon = True
        thread.start()

        return execution_id

    async def _execute_recipe_thread(self, execution_id: str, recipe: Recipe, context_vars: Dict[str, str]):
        """Background thread for recipe execution"""
        status = self.executions[execution_id]
        status.status = "running"

        # Custom logger to capture logs
        log_handler = LogCaptureHandler(status)
        custom_logger = logging.getLogger(f"execution-{execution_id}")
        custom_logger.setLevel(logging.INFO)
        custom_logger.addHandler(log_handler)

        # Convert recipe model to recipe JSON format
        recipe_dict = {"steps": [step.dict(exclude_none=True) for step in recipe.steps]}

        try:
            # Initialize context with variables
            context = Context(artifacts=context_vars)

            # Execute recipe
            custom_logger.info(f"Starting execution of recipe: {recipe.name}")

            # Track progress through steps
            for i, _ in enumerate(recipe.steps):
                status.current_step = i

                # Add small delay to simulate step progress
                time.sleep(0.1)

            # Actually execute the recipe
            await self.executor.execute(recipe_dict, context, logger=custom_logger)

            # Update status on completion
            status.status = "completed"
            status.end_time = datetime.now()
            status.context = context.as_dict()
            custom_logger.info("Recipe execution completed successfully")

        except Exception as e:
            # Update status on failure
            status.status = "failed"
            status.end_time = datetime.now()
            status.error = str(e)
            custom_logger.error(f"Recipe execution failed: {str(e)}")

    def get_execution_status(self, execution_id: str) -> Optional[ExecutionStatus]:
        """Get the status of a recipe execution"""
        return self.executions.get(execution_id)


class LogCaptureHandler(logging.Handler):
    """Custom log handler that captures logs in the execution status"""

    def __init__(self, status: ExecutionStatus):
        super().__init__()
        self.status = status

    def emit(self, record):
        log_entry = self.format(record)
        self.status.logs.append(log_entry)
