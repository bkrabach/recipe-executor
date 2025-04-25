import logging
import os
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class ConditionalConfig(StepConfig):
    """
    Configuration for ConditionalStep.

    Fields:
        condition: Expression string to evaluate against the context.
        if_true: Optional steps to execute when the condition evaluates to true.
        if_false: Optional steps to execute when the condition evaluates to false.
    """

    condition: str
    if_true: Optional[Dict[str, Any]] = None
    if_false: Optional[Dict[str, Any]] = None


def _coerce_bool(value: Any) -> bool:
    # Handles None or missing key as False
    return bool(value)


def file_exists(path: str) -> bool:
    return os.path.exists(path)


def all_files_exist(files: List[str]) -> bool:
    return all(os.path.exists(f) for f in files)


def file_is_newer(source: str, output: str) -> bool:
    if not os.path.exists(source) or not os.path.exists(output):
        return False
    source_time = os.path.getmtime(source)
    output_time = os.path.getmtime(output)
    return source_time > output_time


def _and(*args: Any) -> bool:
    return all(_coerce_bool(arg) for arg in args)


def _or(*args: Any) -> bool:
    return any(_coerce_bool(arg) for arg in args)


def _not(arg: Any) -> bool:
    return not _coerce_bool(arg)


def _safe_eval(expr: str, eval_globals: Dict[str, Any], eval_locals: Dict[str, Any]) -> Any:
    # Only allow access to declared builtins and context
    try:
        return eval(expr, eval_globals, eval_locals)
    except Exception as exc:
        raise ValueError(f"Invalid conditional expression: {expr!r}: {exc}") from exc


class ConditionalStep(BaseStep[ConditionalConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ConditionalConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        from recipe_executor.steps.registry import STEP_REGISTRY

        # 1. Render the template string for the condition
        rendered_condition: str = ""
        try:
            rendered_condition = render_template(self.config.condition, context)
        except Exception as exc:
            self.logger.error(f"Template rendering error in condition: {self.config.condition!r}: {exc}")
            raise

        # 2. Prepare the context for evaluation
        expr: str = rendered_condition
        expr = expr.replace(" true", " True").replace(" false", " False").replace(" null", " None")
        expr = expr.replace("and(", "_and(")
        expr = expr.replace("or(", "_or(")
        expr = expr.replace("not(", "_not(")

        eval_globals: Dict[str, Any] = {
            "__builtins__": {},
            "_and": _and,
            "_or": _or,
            "_not": _not,
            "file_exists": file_exists,
            "all_files_exist": all_files_exist,
            "file_is_newer": file_is_newer,
        }
        eval_locals: Dict[str, Any] = {"context": context}

        # 3. Evaluate the condition
        try:
            result: Any = _safe_eval(expr, eval_globals, eval_locals)
        except Exception as exc:
            self.logger.error(f"Error evaluating condition: {expr!r}: {exc}")
            raise

        result_bool: bool = _coerce_bool(result)
        self.logger.debug(
            f"ConditionalStep evaluated condition '{self.config.condition}' (rendered: '{expr}') -> {result_bool}"
        )

        chosen_branch: Optional[Dict[str, Any]] = None
        branch_name: Optional[str] = None
        if result_bool and self.config.if_true is not None:
            chosen_branch = self.config.if_true
            branch_name = "if_true"
        elif not result_bool and self.config.if_false is not None:
            chosen_branch = self.config.if_false
            branch_name = "if_false"

        if chosen_branch is not None:
            self.logger.debug(f"ConditionalStep executing branch: {branch_name}")
            steps: List[Dict[str, Any]] = chosen_branch.get("steps", [])
            for step_index, step_config in enumerate(steps):
                step_type: str = step_config["type"]
                step_conf: Dict[str, Any] = step_config.get("config", {})
                StepClass = STEP_REGISTRY[step_type]
                step_instance = StepClass(self.logger, step_conf)
                try:
                    await step_instance.execute(context)
                except Exception as exc:
                    self.logger.error(
                        f"ConditionalStep error in branch '{branch_name}', step {step_index} [{step_type}]: {exc}"
                    )
                    raise
        else:
            self.logger.debug(f"ConditionalStep: Skipping branch, none taken. (Condition result: {result_bool})")
