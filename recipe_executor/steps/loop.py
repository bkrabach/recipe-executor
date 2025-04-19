import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple
from recipe_executor.protocols import ContextProtocol, StepProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Key in the context containing the collection to iterate over.
        item_key: Key to use when storing the current item in each iteration's context.
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error (default: True).
    """
    items: str
    item_key: str
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


def is_iterable_collection(obj: Any) -> bool:
    return isinstance(obj, (list, tuple, dict))


def collection_items(obj: Union[List[Any], Dict[Any, Any]]) -> List[Tuple[Any, Any]]:
    if isinstance(obj, dict):
        # Returns list of (key, value)
        return list(obj.items())
    elif isinstance(obj, (list, tuple)):
        # Returns list of (index, value)
        return list(enumerate(obj))
    else:
        raise ValueError("Items is not a collection (list, tuple, dict)")


class LoopStep(BaseStep[LoopStepConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        executor: Optional[ExecutorProtocol] = context.get('__executor')
        if executor is None:
            raise RuntimeError("Executor instance (as '__executor') is required in context for LoopStep.")

        items_key: str = self.config.items
        item_key: str = self.config.item_key
        substeps: List[Dict[str, Any]] = self.config.substeps
        result_key: str = self.config.result_key
        fail_fast: bool = self.config.fail_fast

        if not items_key:
            raise ValueError("'items' key must be specified in LoopStep config.")
        if not item_key:
            raise ValueError("'item_key' must be specified in LoopStep config.")
        if not result_key:
            raise ValueError("'result_key' must be specified in LoopStep config.")
        if not substeps:
            raise ValueError("'substeps' must be specified in LoopStep config.")

        if items_key not in context:
            raise ValueError(f"Context is missing items key '{items_key}' for LoopStep.")
        items_collection: Any = context[items_key]

        if not is_iterable_collection(items_collection):
            raise ValueError(f"Items in '{items_key}' is not iterable; must be array or object.")

        key_value_list: List[Tuple[Any, Any]] = collection_items(items_collection)
        total_count: int = len(key_value_list)
        self.logger.info(f"LoopStep starting: Processing {total_count} items from key '{items_key}'.")

        result_collection: List[Any] = []
        errors: List[Dict[str, Any]] = []
        iteration: int = 0

        for loop_key, item in key_value_list:
            iteration += 1
            self.logger.debug(f"LoopStep: Processing item {iteration}/{total_count} (key/index: {loop_key}).")
            # Clone context to isolate each iteration
            item_context: ContextProtocol = context.clone()

            # Set well-known magic keys for templates
            if isinstance(items_collection, dict):
                item_context['__key'] = loop_key
            else:
                item_context['__index'] = loop_key
            # Set the current item under the configured context key
            item_context[item_key] = item

            step_error: Optional[Exception] = None
            # Run substeps in order in the cloned context
            try:
                for substep in substeps:
                    step_type = substep.get('type')
                    if not step_type:
                        raise ValueError(f"Substep missing 'type' in LoopStep (key: {loop_key}).")

                    from recipe_executor.steps.registry import STEP_REGISTRY  # avoid global import cycle
                    step_cls = STEP_REGISTRY.get(step_type)
                    if not step_cls:
                        raise ValueError(f"Unknown step type '{step_type}' in LoopStep substeps.")
                    step_instance: StepProtocol = step_cls(self.logger, substep.get('config', {}))
                    # Step execute may be async or sync; always await if has coroutine
                    result = step_instance.execute(item_context)
                    if asyncio.iscoroutine(result):
                        await result
                # User may want to capture only certain keys, but by default store item_context[item_key]
                result_item: Any = item_context.get(item_key, None)
                result_collection.append(result_item)
                self.logger.debug(f"LoopStep: Finished item {iteration} (key: {loop_key}).")
            except Exception as exc:
                self.logger.error(f"LoopStep: Error in item {iteration} (key: {loop_key}): {exc}")
                errors.append({
                    "key": loop_key,
                    "item": item,
                    "error": str(exc)
                })
                step_error = exc
                if fail_fast:
                    self.logger.info(f"LoopStep: Fail-fast enabled; aborting on error at item {loop_key}.")
                    break

        # Always collect results, even if empty
        context[result_key] = result_collection
        # Add errors to special key in result if any and fail_fast is False
        if errors and not fail_fast:
            if isinstance(context[result_key], dict):
                context[result_key]['__errors'] = errors
            elif isinstance(context[result_key], list):
                context[result_key + "__errors"] = errors
            else:
                context[result_key + "__errors"] = errors
        # Logging summary
        self.logger.info(
            f"LoopStep finished: processed {len(result_collection)} items, "
            f"{len(errors)} errors written to result."
        )
        # If fail_fast and there was an error, re-raise last error for propagation
        if fail_fast and errors:
            raise RuntimeError(f"LoopStep: Error processing item {errors[-1]['key']}: {errors[-1]['error']}")
