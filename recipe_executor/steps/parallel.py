import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition.
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default = 0 means no explicit limit.
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep executes multiple sub-recipes concurrently.

    Each sub-recipe is executed in its own cloned context.
    Fail-fast behavior is implemented to stop execution upon a substep failure.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[Any] = None) -> None:
        # Convert the config dict to ParallelConfig object
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info(f"Starting ParallelStep with {len(self.config.substeps)} substeps.")

        # Determine the maximum concurrency to use
        if self.config.max_concurrency and self.config.max_concurrency > 0:
            max_workers = self.config.max_concurrency
        else:
            max_workers = len(self.config.substeps) if self.config.substeps else 1

        futures = []
        exception_occurred = False

        def run_substep(index: int, substep: Dict[str, Any], parent_context: Context) -> None:
            substep_type = substep.get("type", "unknown")
            # Clone the parent context to ensure isolation
            cloned_context = parent_context.clone()
            self.logger.debug(f"[Substep {index}] Cloned context for substep: {substep}.")
            try:
                # Get the step class from the registry
                if substep_type not in STEP_REGISTRY:
                    raise ValueError(f"Substep type '{substep_type}' is not registered in STEP_REGISTRY.")
                step_cls = STEP_REGISTRY[substep_type]
                self.logger.debug(f"[Substep {index}] Instantiating step of type '{substep_type}'.")
                # Instantiate the step
                step_instance = step_cls(substep, self.logger)
                self.logger.info(f"[Substep {index}] Execution started for substep with config: {substep}.")
                # Execute the substep
                step_instance.execute(cloned_context)
                self.logger.info(f"[Substep {index}] Execution completed successfully.")
            except Exception as e:
                error_msg = (f"[Substep {index}] Substep execution failed for type '{substep_type}' "
                             f"with recipe_path '{substep.get('recipe_path', 'N/A')}'. Error: {str(e)}")
                self.logger.error(error_msg)
                raise Exception(error_msg) from e

        # Use ThreadPoolExecutor to execute substeps concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx, substep in enumerate(self.config.substeps):
                # Before launching a new substep, check if an error has already occurred
                if exception_occurred:
                    self.logger.debug(f"[Substep {idx}] Skipped launching due to previous errors.")
                    break
                self.logger.debug(f"[Substep {idx}] Submitting substep for execution.")
                future = executor.submit(run_substep, idx, substep, context)
                futures.append((idx, future))
                # Apply launch delay if specified and if this is not the last substep
                if self.config.delay > 0 and idx < len(self.config.substeps) - 1:
                    self.logger.debug(f"Delaying next substep launch by {self.config.delay} seconds.")
                    time.sleep(self.config.delay)

            # Monitor the futures for completion and fail-fast in case of exception
            for idx, future in futures:
                try:
                    # This will re-raise any exception encountered during execution
                    future.result()
                except Exception as e:
                    self.logger.error(f"Fail-fast: Cancelling remaining substeps due to failure in substep {idx}.")
                    exception_occurred = True
                    # Cancel any futures that haven't completed yet
                    for _, f in futures:
                        if not f.done():
                            f.cancel()
                    # Propagate the error
                    raise e

        self.logger.info(f"ParallelStep completed. All substeps finished successfully.")
