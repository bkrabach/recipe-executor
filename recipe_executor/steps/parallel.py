import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
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
        max_concurrency: int = self.config.max_concurrency or len(self.config.substeps)
        delay: float = self.config.delay or 0
        substeps: List[Dict[str, Any]] = self.config.substeps
        errors: List[Exception] = []
        results: List[Optional[Exception]] = [None] * len(substeps)
        loop = asyncio.get_running_loop()
        # Use a single thread pool for all substeps to avoid nested executor issues
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_concurrency)
        semaphore: asyncio.Semaphore = asyncio.Semaphore(max_concurrency)
        tasks: List[asyncio.Task] = []
        cancelled = False

        self.logger.info(
            f"ParallelStep: starting {len(substeps)} substeps with max_concurrency={max_concurrency}, delay={delay}"
        )

        async def run_substep(idx: int, step_def: Dict[str, Any]) -> None:
            nonlocal cancelled
            if cancelled:
                return
            await semaphore.acquire()
            if cancelled:
                semaphore.release()
                return
            context_copy: ContextProtocol = context.clone()
            step_type: str = step_def.get("type", "execute_recipe")
            step_config: Dict[str, Any] = step_def.get("config") or step_def
            # Render templates in string fields
            for k, v in step_config.items():
                if isinstance(v, str):
                    step_config[k] = render_template(v, context_copy)
            step_cls = STEP_REGISTRY.get(step_type)
            if step_cls is None:
                semaphore.release()
                raise ValueError(f"ParallelStep: step type '{step_type}' is not registered.")
            # Steps might be async or sync
            step: StepProtocol = step_cls(self.logger, step_config)
            try:
                self.logger.debug(f"ParallelStep: starting substep {idx + 1}/{len(substeps)}: {step_type}")
                execute_method = getattr(step, "execute", None)
                if execute_method is None:
                    semaphore.release()
                    raise AttributeError(f"ParallelStep: step '{step_type}' does not have an 'execute' method.")
                if asyncio.iscoroutinefunction(execute_method):
                    await execute_method(context_copy)
                else:
                    await loop.run_in_executor(executor, execute_method, context_copy)
                self.logger.debug(f"ParallelStep: completed substep {idx + 1}/{len(substeps)}: {step_type}")
            except Exception as e:
                self.logger.error(f"ParallelStep: substep {idx + 1} failed: {e}")
                results[idx] = e
                errors.append(e)
                cancelled = True
                raise
            finally:
                semaphore.release()

        try:
            for idx, substep in enumerate(substeps):
                if cancelled:
                    break
                task = asyncio.create_task(run_substep(idx, substep))
                tasks.append(task)
                if delay > 0 and idx < len(substeps) - 1:
                    await asyncio.sleep(delay)
            # Wait for all tasks (fail fast: propagate first error)
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            # If error, cancel all unfinished tasks
            if any(t for t in done if t.exception()):
                for t in pending:
                    t.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
                for i, t in enumerate(tasks):
                    if t.done() and t.exception() and results[i] is None:
                        exc = t.exception()
                        results[i] = exc if isinstance(exc, Exception) else None
            else:
                # Wait for everything to finish
                await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            executor.shutdown(wait=True, cancel_futures=True)

        failed_count: int = sum(1 for e in results if e)
        self.logger.info(
            f"ParallelStep: completed {len(substeps)} substeps; failures: {failed_count}"
            + (f"; error: {errors[0]}" if errors else "")
        )
        if errors:
            idx = results.index(errors[0]) if errors[0] in results else -1
            raise RuntimeError(f"ParallelStep: substep {idx + 1} failed: {errors[0]}")
