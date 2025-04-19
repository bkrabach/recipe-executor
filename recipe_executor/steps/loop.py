import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol, StepProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


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


class LoopStep(BaseStep[LoopStepConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Validate required fields exist in context
        items_key: str = self.config.items
        item_key: str = self.config.item_key
        substeps: List[Dict[str, Any]] = self.config.substeps
        result_key: str = self.config.result_key
        fail_fast: bool = self.config.fail_fast

        if items_key not in context:
            self.logger.error(f"[LoopStep] Items key '{items_key}' not found in context.")
            raise ValueError(f"Items key '{items_key}' not found in context.")

        if not isinstance(substeps, list) or not substeps:
            self.logger.error("[LoopStep] Substeps must be a non-empty list.")
            raise ValueError("LoopStep requires at least one substep.")

        # Obtain the executor from the context
        executor: Optional[ExecutorProtocol] = context.get("__executor__", None)
        if executor is None:
            self.logger.error("[LoopStep] No executor found in context (missing '__executor__' key).")
            raise ValueError("LoopStep: No executor found in context (missing '__executor__' key).")

        # Support both arrays and objects
        raw_collection: Any = context[items_key]
        if isinstance(raw_collection, dict):
            collection = list(raw_collection.items())  # List[Tuple[str, Any]]
            is_dict = True
        elif isinstance(raw_collection, (list, tuple)):
            collection = list(enumerate(raw_collection))  # List[Tuple[int, Any]]
            is_dict = False
        else:
            self.logger.error(
                f"[LoopStep] The collection under key '{items_key}' "
                f"must be a list, tuple, or dict (got {type(raw_collection).__name__})."
            )
            raise ValueError(
                f"LoopStep: Items must be list/tuple/dict (got {type(raw_collection).__name__}) at key: {items_key}"
            )

        total_count: int = len(collection)
        self.logger.info(f"[LoopStep] Looping over {total_count} items from '{items_key}' to produce '{result_key}'.")
        if total_count == 0:
            self.logger.info(f"[LoopStep] Collection is empty. Storing empty results at '{result_key}'.")
            context[result_key] = []
            return

        results: List[Any] = []
        errors: List[Dict[str, Any]] = []

        async def process_item(item_info: Tuple[Union[int, str], Any]) -> Optional[Any]:
            key_or_index, item_value = item_info
            item_context: ContextProtocol = context.clone()
            item_context[item_key] = item_value
            if is_dict:
                item_context["__key"] = key_or_index
            else:
                item_context["__index"] = key_or_index
            item_id = f"{key_or_index}"
            self.logger.debug(f"[LoopStep] Starting processing item {item_id} ...")

            try:
                for substep_cfg in substeps:
                    step_type = substep_cfg.get("type")
                    if not step_type or step_type not in STEP_REGISTRY:
                        raise ValueError(f"Unknown or missing step type '{step_type}' in LoopStep substeps.")
                    step_cls = STEP_REGISTRY[step_type]
                    step_instance: StepProtocol = step_cls(self.logger, substep_cfg.get("config", {}))
                    if asyncio.iscoroutinefunction(step_instance.execute):
                        await step_instance.execute(item_context)
                    else:
                        # supporting legacy/non-async steps if any
                        await asyncio.get_event_loop().run_in_executor(None, step_instance.execute, item_context)
                    self.logger.debug(f"[LoopStep] Ran substep '{step_type}' for item {item_id}.")

                # Collect the processed result from item_context[item_key] (by default)
                result = item_context.get(item_key, None)
                self.logger.debug(f"[LoopStep] Finished processing item {item_id}.")
                return result
            except Exception as e:
                self.logger.error(f"[LoopStep] Error processing item {item_id}: {str(e)}", exc_info=True)
                errors.append({
                    "key": key_or_index if is_dict else None,
                    "index": key_or_index if not is_dict else None,
                    "error": str(e),
                })
                if fail_fast:
                    raise
                return None

        # Process all items sequentially (async for future scalability)
        for idx, item_info in enumerate(collection):
            try:
                result = await process_item(item_info)
                # Only add successful results
                if result is not None or not fail_fast:
                    results.append(result)
            except Exception:
                # On fail_fast, error already logged and exceptions bubble up
                break

        # Store the final results
        context[result_key] = results
        if errors:
            context["__errors"] = errors
        self.logger.info(f"[LoopStep] Stored results for {len(results)} items at '{result_key}'.")
        if errors:
            self.logger.error(f"[LoopStep] Encountered errors for {len(errors)} item(s): {errors}")
