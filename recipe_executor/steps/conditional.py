import logging
import os
import re
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
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


# Utility functions for condition evaluation


def file_exists(path: Any) -> bool:
    """Check if a given path exists on the filesystem."""
    try:
        return isinstance(path, str) and os.path.exists(path)
    except Exception:
        return False


def all_files_exist(paths: Any) -> bool:
    """Check if all paths in a list or tuple exist."""
    try:
        if not isinstance(paths, (list, tuple)):
            return False
        return all(isinstance(p, str) and os.path.exists(p) for p in paths)
    except Exception:
        return False


def file_is_newer(src: Any, dst: Any) -> bool:
    """Check if src file is newer than dst file."""
    try:
        if not (isinstance(src, str) and isinstance(dst, str)):
            return False
        if not (os.path.exists(src) and os.path.exists(dst)):
            return False
        return os.path.getmtime(src) > os.path.getmtime(dst)
    except Exception:
        return False


def and_(*args: Any) -> bool:
    """Logical AND over all arguments."""
    return all(bool(a) for a in args)


def or_(*args: Any) -> bool:
    """Logical OR over all arguments."""
    return any(bool(a) for a in args)


def not_(val: Any) -> bool:
    """Logical NOT of the value."""
    return not bool(val)


def evaluate_condition(expr: str, context: ContextProtocol, logger: logging.Logger) -> bool:
    """
    Render and evaluate a condition expression against the context.
    Supports file checks, comparisons, and function-like logical operations.
    Raises ValueError on render or eval errors.
    """
    try:
        rendered = render_template(expr, context)
    except Exception as err:
        raise ValueError(f"Error rendering condition '{expr}': {err}")

    logger.debug(f"Rendered condition '{expr}': '{rendered}'")
    trimmed = rendered.strip()
    lowered = trimmed.lower()

    # Direct boolean literal
    if lowered in ("true", "false"):
        result = lowered == "true"
        logger.debug(f"Interpreted boolean literal '{trimmed}' as {result}")
        return result

    # Replace logical function names to avoid Python keyword conflicts
    expr_transformed = re.sub(r"\band\(", "and_(", trimmed)
    expr_transformed = re.sub(r"\bor\(", "or_(", expr_transformed)
    expr_transformed = re.sub(r"\bnot\(", "not_(", expr_transformed)
    logger.debug(f"Transformed expression for eval: '{expr_transformed}'")

    safe_globals: Dict[str, Any] = {
        "__builtins__": {},
        # file utilities
        "file_exists": file_exists,
        "all_files_exist": all_files_exist,
        "file_is_newer": file_is_newer,
        # logical helpers
        "and_": and_,
        "or_": or_,
        "not_": not_,
        # boolean literals
        "true": True,
        "false": False,
    }

    try:
        eval_result = eval(expr_transformed, safe_globals, {})  # noqa: P204
    except Exception as err:
        raise ValueError(f"Invalid condition expression '{expr_transformed}': {err}")

    result_bool = bool(eval_result)
    logger.debug(f"Condition '{expr_transformed}' evaluated to {result_bool}")
    return result_bool


class ConditionalStep(BaseStep[ConditionalConfig]):
    """
    Step that branches execution based on a boolean condition.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ConditionalConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        expr = self.config.condition
        self.logger.debug(f"Evaluating conditional expression: '{expr}'")
        try:
            result = evaluate_condition(expr, context, self.logger)
        except ValueError as err:
            raise RuntimeError(f"Condition evaluation error: {err}")

        if result:
            self.logger.debug(f"Condition '{expr}' is True, executing 'if_true' branch")
            branch = self.config.if_true
        else:
            self.logger.debug(f"Condition '{expr}' is False, executing 'if_false' branch")
            branch = self.config.if_false

        if branch and isinstance(branch, dict):
            await self._execute_branch(branch, context)
        else:
            self.logger.debug("No branch to execute for this condition result")

    async def _execute_branch(self, branch: Dict[str, Any], context: ContextProtocol) -> None:
        steps: List[Any] = branch.get("steps", []) or []
        if not isinstance(steps, list):
            self.logger.debug("Branch 'steps' is not a list, skipping execution")
            return

        for step_def in steps:
            if not isinstance(step_def, dict):
                continue

            step_type = step_def.get("type")
            step_conf = step_def.get("config", {}) or {}
            if not step_type:
                self.logger.debug("Step definition missing 'type', skipping")
                continue

            step_cls = STEP_REGISTRY.get(step_type)
            if not step_cls:
                raise RuntimeError(f"Unknown step type in conditional branch: {step_type}")

            self.logger.debug(f"Executing step '{step_type}' in conditional branch")
            step = step_cls(self.logger, step_conf)
            await step.execute(context)


# Register this step in the global registry
STEP_REGISTRY["conditional"] = ConditionalStep
