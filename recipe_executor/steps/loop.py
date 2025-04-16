from typing import Any, Dict, List

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig


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
    """
    LoopStep allows recipes to iterate over a collection of items, executing a set of substeps for each item.
    """

    async def execute(self, context: ContextProtocol) -> None:
        # Retrieve the collection of items from the context
        try:
            collection = context[self.config.items]
        except KeyError:
            raise ValueError(f"Missing items collection '{self.config.items}' in context")

        if not isinstance(collection, (list, dict)):
            raise ValueError(f"Items collection '{self.config.items}' is not an iterable (list or dict)")

        # Prepare containers for results and errors
        successes: Any = [] if isinstance(collection, list) else {}
        errors: List[Dict[str, Any]] = []

        # Process each item in the collection
        if isinstance(collection, list):
            for index, item in enumerate(collection):
                self.logger.debug(f"Starting processing item at index {index}")
                cloned_context = context.clone()
                # Set current item and iteration metadata
                cloned_context[self.config.item_key] = item
                cloned_context["__index"] = index
                try:
                    await self._execute_substeps(cloned_context)
                    result = cloned_context.get(self.config.item_key)
                    successes.append(result)
                    self.logger.debug(f"Finished processing item at index {index}")
                except Exception as e:
                    error_info = {"index": index, "error": str(e)}
                    self.logger.error(f"Error processing item at index {index}: {str(e)}")
                    if self.config.fail_fast:
                        raise
                    errors.append(error_info)
        else:  # collection is a dict
            for key, item in collection.items():
                self.logger.debug(f"Starting processing item with key '{key}'")
                cloned_context = context.clone()
                # Set current item and iteration metadata
                cloned_context[self.config.item_key] = item
                cloned_context["__key"] = key
                try:
                    await self._execute_substeps(cloned_context)
                    result = cloned_context.get(self.config.item_key)
                    successes[key] = result
                    self.logger.debug(f"Finished processing item with key '{key}'")
                except Exception as e:
                    error_info = {"key": key, "error": str(e)}
                    self.logger.error(f"Error processing item with key '{key}': {str(e)}")
                    if self.config.fail_fast:
                        raise
                    errors.append(error_info)

        # Store the aggregated results in the parent context
        if not self.config.fail_fast and errors:
            # When continuing on error, include both successes and errors
            context[self.config.result_key] = {"results": successes, "__errors": errors}
        else:
            context[self.config.result_key] = successes

    async def _execute_substeps(self, context: ContextProtocol) -> None:
        """
        Executes the configured substeps in sequence using the provided context.
        """
        # Import step registry locally to avoid circular dependencies
        from recipe_executor.steps.registry import STEP_REGISTRY

        for idx, step_config in enumerate(self.config.substeps):
            step_type = step_config.get("type")
            if not step_type:
                raise ValueError("Substep configuration missing 'type' field")

            step_class = STEP_REGISTRY.get(step_type)
            if not step_class:
                raise ValueError(f"Step type '{step_type}' not registered in STEP_REGISTRY")

            self.logger.debug(f"Executing substep {idx} of type '{step_type}'")
            step_instance = step_class(step_config, logger=self.logger)
            await step_instance.execute(context)
