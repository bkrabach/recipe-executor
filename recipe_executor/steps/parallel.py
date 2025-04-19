import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol, StepProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0


class ParallelStep(BaseStep[ParallelConfig]):
    def __init__(
        self,
        logger: logging.Logger,
        config: Dict[str, Any],
    ) -> None:
        super().__init__(logger, ParallelConfig(**config))
        self._executor: Optional[ThreadPoolExecutor] = None

    async def execute(self, context: ContextProtocol) -> None:
        max_concurrency: int = self.config.max_concurrency or len(self.config.substeps)
        delay: float = self.config.delay or 0
        substeps: List[Dict[str, Any]] = self.config.substeps

        self.logger.info(
            f"[ParallelStep] Starting parallel execution: {len(substeps)} substeps, "
            f"max_concurrency={max_concurrency}, delay={delay}"  # noqa: E501
        )
        # No nested thread pools: only create one shared thread pool per parallel block
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=max_concurrency)

        loop = asyncio.get_event_loop()
        tasks: List[asyncio.Task] = []
        errors: List[Exception] = []
        completed: int = 0
        task_cancelled = False

        async def run_substep(index: int, step_def: Dict[str, Any]) -> None:
            nonlocal completed
            # Clone the context for this substep
            sub_context: ContextProtocol = context.clone()
            step_type: str = step_def["type"]
            step_config: Dict[str, Any] = step_def.get("config", {})
            # Only allow execute_recipe for now
            if step_type != "execute_recipe":
                raise RuntimeError(f"Only 'execute_recipe' sub-steps are supported (got '{step_type}')")
            try:
                self.logger.debug(f"[ParallelStep] [substep {index}] Starting")
                step_class = STEP_REGISTRY[step_type]
                step: StepProtocol = step_class(self.logger, step_config)
                # Support both async and sync execute
                maybe_coro = step.execute(sub_context)
                if asyncio.iscoroutine(maybe_coro):
                    await maybe_coro
                else:
                    maybe_coro  # Run if not coroutine (if someone implemented sync execute)
                self.logger.debug(f"[ParallelStep] [substep {index}] Completed")
            except Exception as exc:
                # Attach substep index for error context
                raise RuntimeError(f"[ParallelStep] Substep {index} failed: {exc}") from exc
            finally:
                completed += 1

        # Task launcher wrapper to enforce delay and fail-fast
        async def launcher() -> None:
            nonlocal errors, task_cancelled
            semaphore = asyncio.Semaphore(max_concurrency)

            async def wrap_run(i: int, defn: Dict[str, Any]) -> None:
                try:
                    async with semaphore:
                        await run_substep(i, defn)
                except Exception as err:
                    errors.append(err)
                    self.logger.error(f"[ParallelStep] [substep {i}] Error: {err}")
                    # Fail-fast: cancel all other tasks that haven't started
                    task_cancelled = True
                    for task in tasks:
                        if not task.done():
                            task.cancel()

            for i, step_def in enumerate(substeps):
                if task_cancelled or errors:
                    break
                tasks.append(asyncio.create_task(wrap_run(i, step_def)))
                if delay > 0 and i < len(substeps) - 1:
                    await asyncio.sleep(delay)

        try:
            await launcher()
            # Wait all tasks -- good/bad results or cancelled
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            # Always shutdown executor to avoid leaks
            if self._executor:
                self._executor.shutdown(wait=True, cancel_futures=True)
                self._executor = None

        error_count = len(errors)
        self.logger.info(f"[ParallelStep] Completed: {completed} substeps, {error_count} failed")
        if errors:
            # Report only first error for fail-fast
            raise errors[0]
