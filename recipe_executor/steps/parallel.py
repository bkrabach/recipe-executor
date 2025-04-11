import asyncio
import logging
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Attributes:
        substeps: List of sub-step configurations to execute in parallel.
                   Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc.).
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default of 0 means no explicit limit (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay (all allowed substeps start immediately).
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """ParallelStep enables the execution of multiple sub-steps concurrently.

    Each sub-step runs in its own cloned context to ensure isolation. Execution is controlled
    using asyncio concurrency primitives, with configurable concurrency and launch delays.
    Fail-fast behavior is implemented: if any sub-step fails, pending steps are cancelled and
    the error is propagated.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Parse config using the ParallelConfig model
        super().__init__(ParallelConfig(**config), logger)

    async def execute(self, context: ContextProtocol) -> None:
        self.logger.info(f"Starting ParallelStep with {len(self.config.substeps)} substeps")

        # Set up concurrency control
        semaphore: Optional[asyncio.Semaphore] = None
        if self.config.max_concurrency > 0:
            semaphore = asyncio.Semaphore(self.config.max_concurrency)
            self.logger.debug(f"Max concurrency set to {self.config.max_concurrency}")
        else:
            self.logger.debug("No max concurrency limit set; running all substeps concurrently")

        tasks: List[asyncio.Task] = []

        async def run_substep(sub_config: Dict[str, Any], sub_context: ContextProtocol, index: int) -> None:
            try:
                self.logger.debug(f"Starting substep {index} with config: {sub_config}")
                # Lookup the step type from the registry
                step_type = sub_config.get("type")
                if step_type not in STEP_REGISTRY:
                    raise ValueError(f"Substep {index}: Unknown step type '{step_type}'")

                # Instantiate the substep using the registered step class
                step_class = STEP_REGISTRY[step_type]
                substep_instance = step_class(config=sub_config, logger=self.logger)

                # Execute the substep with its own cloned context
                await substep_instance.execute(sub_context)
                self.logger.debug(f"Substep {index} completed successfully")
            except Exception as e:
                self.logger.error(f"Substep {index} failed: {e}")
                raise

        async def run_substep_with_control(sub_config: Dict[str, Any], index: int) -> None:
            # Each substep gets its own cloned context for isolation
            cloned_context = context.clone()
            if semaphore is not None:
                async with semaphore:
                    await run_substep(sub_config, cloned_context, index)
            else:
                await run_substep(sub_config, cloned_context, index)

        # Launch substeps sequentially respecting the optional delay between launches
        for index, sub_config in enumerate(self.config.substeps):
            if index > 0 and self.config.delay > 0:
                self.logger.debug(f"Delaying launch of substep {index} by {self.config.delay} seconds")
                await asyncio.sleep(self.config.delay)

            task = asyncio.create_task(run_substep_with_control(sub_config, index))
            tasks.append(task)

        # Wait for all substeps to complete with fail-fast behavior
        try:
            # Wait until all tasks complete or one fails
            results = await asyncio.gather(*tasks)
            self.logger.info(f"ParallelStep completed all {len(tasks)} substeps successfully")
        except Exception as e:
            self.logger.error("ParallelStep encountered an error; cancelling remaining substeps")
            # Cancel all pending tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            # Optionally wait for cancellation to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            raise e
