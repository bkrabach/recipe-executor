import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from recipe_executor.context import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc).
        max_concurrency: Maximum number of substeps to run concurrently. Default = 0 means no explicit limit
                         (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep. Default = 0 means no delay.
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep component that enables concurrent execution of multiple sub-steps within a recipe.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[Any] = None) -> None:
        # Parse the raw config dict into a ParallelConfig instance
        super().__init__(ParallelConfig(**config), logger)

    def execute_substep(self, substep_config: Dict[str, Any], context: ContextProtocol) -> None:
        """
        Executes a single sub-step in its own cloned context.

        Args:
            substep_config (Dict[str, Any]): The configuration dictionary for the sub-step.
            context (ContextProtocol): The parent execution context.
        """
        # Create an isolated clone of the context for this sub-step
        sub_context = context.clone()

        # Retrieve the step type; it is expected to be present in the substep_config
        step_type = substep_config.get("type")
        if not step_type:
            raise ValueError("Substep configuration missing required 'type' field")

        # Look up the registered step class by type
        if step_type not in STEP_REGISTRY:
            raise ValueError(f"Step type '{step_type}' is not registered in the STEP_REGISTRY")

        step_cls = STEP_REGISTRY[step_type]
        self.logger.debug(f"Instantiating substep of type '{step_type}' with config: {substep_config}")

        # Instantiate the step using its configuration; passing shared logger for consistency
        step_instance = step_cls(substep_config, self.logger)
        self.logger.debug(f"Starting execution of substep: {substep_config}")

        # Execute the sub-step; any exception will be propagated
        step_instance.execute(sub_context)
        self.logger.debug(f"Completed execution of substep: {substep_config}")

    def execute(self, context: ContextProtocol) -> None:
        """
        Executes all sub-steps concurrently with optional delay and fail-fast behavior.

        Args:
            context (ContextProtocol): The execution context for the current recipe step.

        Raises:
            Exception: Propagates the original exception from any sub-step that fails.
        """
        self.logger.info("Starting ParallelStep execution of %d substeps", len(self.config.substeps))
        substeps = self.config.substeps

        # Determine maximum worker threads: if max_concurrency is 0 or less, run all concurrently
        max_workers = self.config.max_concurrency if self.config.max_concurrency > 0 else len(substeps)

        # List to hold the futures of the submitted substeps
        futures = []
        exception_occurred: Optional[BaseException] = None

        # Using ThreadPoolExecutor to launch substeps concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for index, substep_config in enumerate(substeps):
                # Check if any previously submitted future has failed (fail-fast behavior)
                for future in futures:
                    if future.done() and future.exception() is not None:
                        exception_occurred = future.exception()
                        break
                if exception_occurred:
                    self.logger.error("A substep failed; aborting submission of further substeps")
                    break

                self.logger.info("Launching substep %d/%d", index + 1, len(substeps))
                # Submit the substep for execution
                future = executor.submit(self.execute_substep, substep_config, context)
                futures.append(future)

                # If a delay is specified and this is not the last substep, sleep before launching the next
                if self.config.delay > 0 and index < len(substeps) - 1:
                    self.logger.debug("Delaying next substep launch by %f seconds", self.config.delay)
                    time.sleep(self.config.delay)

            # After submission, wait for all submitted substeps to complete
            for future in futures:
                try:
                    # This will raise an exception if the substep execution failed
                    future.result()
                except Exception as e:
                    self.logger.error("A substep execution error occurred", exc_info=True)
                    raise Exception("ParallelStep failed due to a substep error") from e

        self.logger.info("ParallelStep execution completed successfully")
