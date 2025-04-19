import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple, Type

from recipe_executor.protocols import ContextProtocol, StepProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.utils import render_template


class ParallelConfig(StepConfig):
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    def __init__(
        self,
        logger: logging.Logger,
        config: Dict[str, Any],
    ) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        substep_defs: List[Dict[str, Any]] = self.config.substeps
        max_concurrency: int = self.config.max_concurrency
        delay: float = self.config.delay or 0.0

        if not substep_defs:
            self.logger.info("No substeps to execute in ParallelStep")
            return

        step_count: int = len(substep_defs)
        self.logger.info(
            f"ParallelStep starting: {step_count} substeps, max_concurrency={max_concurrency}, delay={delay}"
        )
        errors: List[Tuple[int, Exception]] = []

        semaphore: Optional[asyncio.Semaphore] = None
        if max_concurrency and max_concurrency > 0:
            semaphore = asyncio.Semaphore(max_concurrency)

        # Avoid creating nested thread pools: always execute steps with their own await/sync rules, don't wrap in ThreadPoolExecutor.
        thread_pool: Optional[ThreadPoolExecutor] = None

        async def run_substep(idx: int, substep_def: Dict[str, Any]) -> Optional[Exception]:
            nonlocal errors
            if semaphore:
                async with semaphore:
                    return await _run_step(idx, substep_def)
            else:
                return await _run_step(idx, substep_def)

        async def _run_step(idx: int, substep_def: Dict[str, Any]) -> Optional[Exception]:
            context_clone = context.clone()
            # Deeply render all string values in substep_def with template
            rendered_def = _render_deep(substep_def, context_clone)
            step_type = rendered_def.get("type")
            step_cfg = rendered_def.get("config", {})
            if not step_type or step_type not in STEP_REGISTRY:
                self.logger.error(f"Substep {idx} missing or unknown type: {step_type}")
                return ValueError(f"Substep {idx}: unknown step type: {step_type}")
            StepCls: Type[StepProtocol] = STEP_REGISTRY[step_type]
            step: StepProtocol = StepCls(self.logger, step_cfg)
            self.logger.debug(f"Substep {idx} ({step_type}) starting")
            try:
                res = step.execute(context_clone)
                if asyncio.iscoroutine(res):
                    await res
                self.logger.debug(f"Substep {idx} ({step_type}) completed successfully")
                return None
            except Exception as e:
                self.logger.error(f"Substep {idx} ({step_type}) failed: {e}")
                return e

        all_tasks: List[asyncio.Task] = []
        results: List[Optional[Exception]] = [None] * step_count
        pending_idx: int = 0

        stop_launching: bool = False
        start_event = asyncio.Event()  # Used to wake up waiters on fail-fast

        async def substep_launcher():
            nonlocal pending_idx, all_tasks, stop_launching
            while pending_idx < step_count:
                if stop_launching:
                    break
                substep_def = substep_defs[pending_idx]
                idx = pending_idx
                task = asyncio.create_task(run_substep(idx, substep_def))
                all_tasks.append(task)
                pending_idx += 1
                await asyncio.sleep(delay)

        launcher_task = asyncio.create_task(substep_launcher())

        try:
            for idx in range(step_count):
                if stop_launching:
                    break
                if idx >= len(all_tasks):
                    await asyncio.sleep(0.01)  # Give scheduler a chance
                task: Optional[asyncio.Task] = all_tasks[idx] if idx < len(all_tasks) else None
                if task is None:
                    continue
                try:
                    result = await task
                    results[idx] = result
                    if result is not None:
                        # Fail-fast: stop launching; cancel pending tasks
                        stop_launching = True
                        launcher_task.cancel()
                        for extra_task in all_tasks[idx + 1 :]:
                            extra_task.cancel()
                        raise result
                except asyncio.CancelledError:
                    self.logger.debug(f"Substep {idx} was cancelled")
                    continue
            # Wait for any straggler tasks
            await asyncio.gather(*all_tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"ParallelStep failed: {e}")
            raise
        finally:
            if launcher_task:
                launcher_task.cancel()
                try:
                    await launcher_task
                except Exception:
                    pass
            if thread_pool is not None:
                thread_pool.shutdown(wait=False)

        success_count = sum(1 for r in results if r is None)
        fail_count = step_count - success_count
        if fail_count > 0:
            self.logger.info(f"ParallelStep completed: {success_count} succeeded, {fail_count} failed")
        else:
            self.logger.info(f"ParallelStep completed: all {step_count} substeps succeeded")
        return


def _render_deep(obj: Any, context: ContextProtocol) -> Any:
    # Recursively render all strings using render_template
    if isinstance(obj, dict):
        return {k: _render_deep(v, context) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_render_deep(v, context) for v in obj]
    if isinstance(obj, str):
        return render_template(obj, context)
    return obj
