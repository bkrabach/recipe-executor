import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template

__all__ = ["LoopStep", "LoopStepConfig"]


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.
    """
    items: str
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    """
    LoopStep: iterate over a collection, execute substeps per item.
    """
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # dynamic import to avoid circular dependencies
        from recipe_executor.executor import Executor  # type: ignore

        # resolve items path
        items_path: str = render_template(self.config.items, context)
        items_obj: Any = _resolve_path(items_path, context)

        if items_obj is None:
            raise ValueError(f"LoopStep: Items collection '{items_path}' not found in context.")
        if not isinstance(items_obj, (list, dict)):
            raise ValueError(
                f"LoopStep: Items collection '{items_path}' must be a list or dict, got {type(items_obj).__name__}"
            )

        # build list of (key/index, value)
        items_list: List[Tuple[Any, Any]] = []
        if isinstance(items_obj, list):
            for idx, value in enumerate(items_obj):
                items_list.append((idx, value))
        else:
            for key, value in items_obj.items():
                items_list.append((key, value))
        total_items: int = len(items_list)

        self.logger.info(
            f"LoopStep: Processing {total_items} items with max_concurrency={self.config.max_concurrency}."
        )

        # handle empty collection
        if total_items == 0:
            empty: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
            context[self.config.result_key] = empty
            self.logger.info("LoopStep: No items to process.")
            return

        # prepare result and error containers
        results: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
        errors: Union[List[Dict[str, Any]], Dict[Any, Dict[str, Any]]] = [] if isinstance(items_obj, list) else {}

        # concurrency control
        semaphore: Optional[asyncio.Semaphore] = None
        if self.config.max_concurrency and self.config.max_concurrency > 0:
            semaphore = asyncio.Semaphore(self.config.max_concurrency)

        # executor for substeps
        step_executor: ExecutorProtocol = Executor(self.logger)
        substeps_recipe: Dict[str, Any] = {"steps": self.config.substeps}

        fail_fast_triggered: bool = False
        tasks: List[asyncio.Task] = []
        completed_count: int = 0

        async def process_single_item(idx_or_key: Any, item: Any) -> Tuple[Any, Any, Optional[str]]:
            # isolate context
            item_context: ContextProtocol = context.clone()
            item_context[self.config.item_key] = item
            # index or key in context
            if isinstance(items_obj, list):
                item_context["__index"] = idx_or_key
            else:
                item_context["__key"] = idx_or_key
            try:
                self.logger.debug(f"LoopStep: Starting item {idx_or_key}.")
                await step_executor.execute(substeps_recipe, item_context)
                # extract result
                result = item_context.get(self.config.item_key, item)
                self.logger.debug(f"LoopStep: Finished item {idx_or_key}.")
                return idx_or_key, result, None
            except Exception as exc:
                self.logger.error(f"LoopStep: Error processing item {idx_or_key}: {exc}")
                return idx_or_key, None, str(exc)

        async def run_sequential() -> None:
            nonlocal fail_fast_triggered, completed_count
            for idx_or_key, item in items_list:
                if fail_fast_triggered:
                    break
                idx, res, err = await process_single_item(idx_or_key, item)
                if err:
                    # record error
                    if isinstance(errors, list):
                        errors.append({"index": idx, "error": err})
                    else:
                        errors[idx] = {"error": err}
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break
                else:
                    # record success
                    if isinstance(results, list):
                        results.append(res)
                    else:
                        results[idx] = res
                completed_count += 1

        async def run_parallel() -> None:
            nonlocal fail_fast_triggered, completed_count

            async def worker(key: Any, value: Any) -> Tuple[Any, Any, Optional[str]]:
                if semaphore is not None:
                    async with semaphore:
                        return await process_single_item(key, value)
                return await process_single_item(key, value)

            # launch tasks
            for idx, (key, value) in enumerate(items_list):
                if fail_fast_triggered:
                    break
                task = asyncio.create_task(worker(key, value))
                tasks.append(task)
                if self.config.delay and self.config.delay > 0 and idx < total_items - 1:
                    await asyncio.sleep(self.config.delay)
            # collect results
            for fut in asyncio.as_completed(tasks):
                if fail_fast_triggered:
                    break
                try:
                    idx, res, err = await fut
                    if err:
                        if isinstance(errors, list):
                            errors.append({"index": idx, "error": err})
                        else:
                            errors[idx] = {"error": err}
                        if self.config.fail_fast:
                            fail_fast_triggered = True
                            continue
                    else:
                        if isinstance(results, list):
                            results.append(res)
                        else:
                            results[idx] = res
                    completed_count += 1
                except Exception as exc:
                    self.logger.error(f"LoopStep: Unexpected exception: {exc}")
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        continue

        # choose execution mode
        if self.config.max_concurrency == 1:
            await run_sequential()
        else:
            await run_parallel()

        # store results
        context[self.config.result_key] = results
        # store errors if any
        has_errors = (isinstance(errors, list) and bool(errors)) or (isinstance(errors, dict) and bool(errors))
        if has_errors:
            context[f"{self.config.result_key}__errors"] = errors
        self.logger.info(
            f"LoopStep: Processed {completed_count} items. Errors: {len(errors) if has_errors else 0}."
        )


def _resolve_path(path: str, context: ContextProtocol) -> Any:
    """
    Resolve a dot-notated path against the context or nested dicts.
    """
    current: Any = context
    for part in path.split('.'):
        if isinstance(current, ContextProtocol):
            current = current.get(part, None)
        elif isinstance(current, dict):
            current = current.get(part, None)
        else:
            return None
        if current is None:
            return None
    return current
