import asyncio
import logging
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol, StepProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.utils import render_template


class ParallelConfig(StepConfig):
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0


class ParallelStep(BaseStep[ParallelConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        substep_defs: List[Dict[str, Any]] = self.config.substeps
        max_concurrency: int = self.config.max_concurrency
        delay: float = self.config.delay

        if not substep_defs:
            self.logger.info("No substeps specified; skipping parallel block.")
            return

        # Concurrency control
        semaphore: Optional[asyncio.Semaphore] = None
        if max_concurrency > 0:
            semaphore = asyncio.Semaphore(max_concurrency)

        tasks: List[asyncio.Task] = []

        # Store for cancellation support
        start_exception: Optional[BaseException] = None
        finished_count = 0
        step_count = len(substep_defs)

        async def run_substep(i: int, step_def: Dict[str, Any]) -> None:
            nonlocal finished_count, start_exception
            step_type: str = step_def["type"]
            step_config = step_def.get("config", {})

            # Render config templates using context
            rendered_config: Dict[str, Any] = {}
            for k, v in step_config.items():
                if isinstance(v, str):
                    rendered_config[k] = render_template(v, context)
                else:
                    rendered_config[k] = v

            # Clone context
            sub_context = context.clone()
            # Re-marshal config as per step expectations
            self.logger.debug(
                f"Launching substep {i + 1}/{step_count} of type '{step_type}' with config: {rendered_config}"
            )
            try:
                step_class = STEP_REGISTRY[step_type]
                step: StepProtocol = step_class(self.logger, rendered_config)
                if asyncio.iscoroutinefunction(step.execute):
                    await step.execute(sub_context)
                else:
                    await asyncio.get_running_loop().run_in_executor(None, step.execute, sub_context)
                self.logger.debug(f"Completed substep {i + 1}/{step_count} of type '{step_type}'")
            except Exception as ex:
                self.logger.error(f"Substep {i + 1}/{step_count} failed: {ex}", exc_info=True)
                start_exception = ex
                raise
            finally:
                finished_count += 1

        async def task_runner():
            # Fail-fast logic: launch in order, with concurrency control, and delay
            try:
                for i, step_def in enumerate(substep_defs):
                    if start_exception is not None:
                        self.logger.debug(
                            f"Fail-fast abort: skipping launch of substep {i + 1}/{step_count} after error."
                        )
                        break
                    if semaphore is not None:
                        await semaphore.acquire()
                    # Staggered launch for delay
                    if i > 0 and delay > 0:
                        await asyncio.sleep(delay)

                    async def step_task(idx=i, sdef=step_def):
                        try:
                            await run_substep(idx, sdef)
                        finally:
                            if semaphore is not None:
                                semaphore.release()

                    task = asyncio.create_task(step_task())
                    tasks.append(task)
                # Wait for all launched tasks to finish
                if tasks:
                    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            finally:
                # Cancel others if failed
                if start_exception is not None:
                    for t in tasks:
                        if not t.done():
                            t.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)

        self.logger.info(
            f"Starting parallel block: {step_count} substeps, max_concurrency={max_concurrency}, delay={delay}"
        )
        try:
            await task_runner()
        except Exception as exc:
            error_msg = f"Parallel block failed after {finished_count} completed steps: {exc}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from exc
        success_count = sum(1 for t in tasks if t.done() and not t.cancelled() and t.exception() is None)
        fail_count = sum(1 for t in tasks if t.done() and t.exception() is not None)
        self.logger.info(f"Parallel block complete: {success_count} succeeded, {fail_count} failed, total={step_count}")
