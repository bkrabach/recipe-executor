from typing import List, Dict, Any, Optional
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel. Each substep should be an execute_recipe step definition.
        max_concurrency: Maximum number of substeps to run concurrently. Default = 0 means no explicit limit.
        delay: Optional delay (in seconds) between launching each substep. Default = 0 means no delay.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep executes multiple sub-steps concurrently within a single step.

    It clones the provided context for each sub-step, executes sub-steps concurrently using a ThreadPoolExecutor,
    supports an optional delay between launching each sub-step, implements fail-fast behavior, and waits for all
    sub-steps to complete before proceeding.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Initialize with ParallelConfig created from the provided dict config
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info("Starting ParallelStep execution.")
        substeps = self.config.substeps
        if not substeps:
            self.logger.info("No substeps provided. Exiting ParallelStep.")
            return

        # Determine max_workers based on configuration
        max_workers = self.config.max_concurrency if self.config.max_concurrency > 0 else len(substeps)

        futures = []
        executor = ThreadPoolExecutor(max_workers=max_workers)
        error_occurred = None

        try:
            for index, sub_config in enumerate(substeps):
                # If an error has already occurred, do not launch further substeps (fail-fast behavior)
                if error_occurred:
                    self.logger.error("Fail-fast: Aborting launch of further substeps due to earlier error.")
                    break

                # Clone the context for isolation
                cloned_context = context.clone()

                # Determine sub-step type and ensure it is registered
                step_type = sub_config.get("type")
                if step_type not in STEP_REGISTRY:
                    raise ValueError(f"Sub-step type '{step_type}' is not registered in STEP_REGISTRY.")

                sub_step_class = STEP_REGISTRY[step_type]
                sub_step = sub_step_class(sub_config, self.logger)

                self.logger.debug(f"Launching sub-step {index + 1}/{len(substeps)} of type '{step_type}'.")

                # Define the runner function for the sub-step
                def run_sub_step(step=sub_step, ctx=cloned_context, idx=index):
                    self.logger.debug(f"Sub-step {idx + 1} started.")
                    step.execute(ctx)
                    self.logger.debug(f"Sub-step {idx + 1} completed.")

                # Submit the sub-step for execution
                future = executor.submit(run_sub_step)
                futures.append(future)

                # Optional delay between launching each sub-step
                if self.config.delay > 0 and index < len(substeps) - 1:
                    self.logger.debug(f"Delaying launch of next sub-step by {self.config.delay} seconds.")
                    time.sleep(self.config.delay)

            # Wait for all futures to complete, handling any exception immediately (fail-fast behavior)
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    error_occurred = exc
                    self.logger.error(f"A sub-step raised an exception: {exc}. Cancelling pending substeps.")
                    # Cancel pending substeps
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    # Shutdown executor immediately, cancelling futures if supported
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise exc
        finally:
            executor.shutdown(wait=True)

        self.logger.info(f"ParallelStep completed: {len(substeps)} substeps executed.")
