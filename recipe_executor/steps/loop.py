import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class LoopStepConfig(StepConfig):
    items: str
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        from recipe_executor.executor import Executor  # dynamic import to avoid cycles

        items_path: str = render_template(self.config.items, context)
        items_obj: Any = _resolve_path(items_path, context)

        if items_obj is None:
            raise ValueError(f"LoopStep: Items collection '{items_path}' not found in context.")
        if not isinstance(items_obj, (list, dict)):
            raise ValueError(
                f"LoopStep: Items collection '{items_path}' must be a list or dict, got {type(items_obj).__name__}"
            )

        items_list: List[Tuple[Any, Any]] = []
        if isinstance(items_obj, list):
            for i, v in enumerate(items_obj):
                items_list.append((i, v))
        else:
            for k, v in items_obj.items():
                items_list.append((k, v))
        total_items: int = len(items_list)

        self.logger.info(
            f"LoopStep: Processing {total_items} items with max_concurrency={self.config.max_concurrency}."
        )

        if total_items == 0:
            context[self.config.result_key] = [] if isinstance(items_obj, list) else {}
            self.logger.info("LoopStep: No items to process.")
            return

        results: Union[List[Any], Dict[Any, Any]]
        errors: Union[Dict[Any, Dict[str, Any]], List[Dict[str, Any]]]
        results = [] if isinstance(items_obj, list) else {}
        errors = [] if isinstance(items_obj, list) else {}

        semaphore: Optional[asyncio.Semaphore] = None
        if self.config.max_concurrency and self.config.max_concurrency > 0:
            semaphore = asyncio.Semaphore(self.config.max_concurrency)

        step_executor: ExecutorProtocol = Executor(self.logger)
        substeps_recipe: Dict[str, Any] = {"steps": self.config.substeps}
        fail_fast_triggered: bool = False
        tasks: List[asyncio.Task] = []
        completed_count: int = 0

        async def process_single_item(idx_or_key: Any, item: Any) -> Tuple[Any, Any, Optional[str]]:
            item_context: ContextProtocol = context.clone()
            item_context[self.config.item_key] = item
            if isinstance(items_obj, list):
                item_context["__index"] = idx_or_key
            else:
                item_context["__key"] = idx_or_key
            try:
                self.logger.debug(f"LoopStep: Starting item {idx_or_key}.")
                await step_executor.execute(substeps_recipe, item_context)
                result = item_context.get(self.config.item_key, item)
                self.logger.debug(f"LoopStep: Finished item {idx_or_key}.")
                return idx_or_key, result, None
            except Exception as exc:
                self.logger.error(f"LoopStep: Error processing item {idx_or_key}: {exc}")
                return idx_or_key, None, str(exc)

        async def run_sequential():
            nonlocal fail_fast_triggered, completed_count
            for idx_or_key, item in items_list:
                if fail_fast_triggered:
                    break
                idx, res, err = await process_single_item(idx_or_key, item)
                if err:
                    if isinstance(errors, list):
                        errors.append({"index": idx, "error": err})
                    else:
                        errors[idx] = {"error": err}
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break
                else:
                    if isinstance(results, list):
                        results.append(res)
                    else:
                        results[idx] = res
                completed_count += 1

        async def run_parallel():
            nonlocal fail_fast_triggered, completed_count

            async def parallel_worker(idx_or_key: Any, item: Any):
                nonlocal fail_fast_triggered, completed_count
                if semaphore is not None:
                    async with semaphore:
                        result = await process_single_item(idx_or_key, item)
                        return result
                else:
                    result = await process_single_item(idx_or_key, item)
                    return result

            for idx, (key, item) in enumerate(items_list):
                if fail_fast_triggered:
                    break
                task = asyncio.create_task(parallel_worker(key, item))
                tasks.append(task)
                if self.config.delay and self.config.delay > 0 and idx < total_items - 1:
                    await asyncio.sleep(self.config.delay)
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

        if self.config.max_concurrency == 1:
            await run_sequential()
        else:
            await run_parallel()

        context[self.config.result_key] = results
        output_errors = (
            errors if (isinstance(errors, list) and errors) or (isinstance(errors, dict) and errors) else None
        )
        if output_errors:
            context[f"{self.config.result_key}__errors"] = errors
        self.logger.info(f"LoopStep: Processed {completed_count} items. Errors: {len(errors) if errors else 0}.")


def _resolve_path(path: str, context: ContextProtocol) -> Any:
    value: Any = context
    for part in path.split("."):
        if isinstance(value, ContextProtocol):
            value = value.get(part, None)
        elif isinstance(value, dict):
            value = value.get(part, None)
        else:
            return None
        if value is None:
            return None
    return value
