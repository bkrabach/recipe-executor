import logging
import operator
import os
from typing import Any, Callable, Dict, List, Optional, Union

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template

# Utility: simple operators mapping for comparison
_COMPARISON_OPS: Dict[str, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}


class ConditionalConfig(StepConfig):
    condition: str
    if_true: Dict[str, Any]
    if_false: Optional[Dict[str, Any]] = None


class ConditionalStep(BaseStep[ConditionalConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ConditionalConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        cond_str: str = self.config.condition
        # Render templates if present
        try:
            cond_eval: str = render_template(cond_str, context)
        except Exception as err:
            raise ValueError(f"Error rendering template in condition '{cond_str}': {err}")

        try:
            result: bool = _eval_condition(cond_eval, context)
        except Exception as err:
            raise ValueError(f"Error evaluating conditional expression '{cond_eval}': {err}")

        self.logger.debug(f"[Conditional] Evaluated condition: '{cond_eval}' => {result}")
        branch = self.config.if_true if result else self.config.if_false
        branch_str = "if_true" if result else "if_false"

        if branch is None:
            self.logger.debug(f"[Conditional] Branch '{branch_str}' is not defined. Skipping.")
            return

        steps = branch.get("steps", [])
        if not isinstance(steps, list):
            raise ValueError(f"'{branch_str}' must define a 'steps' list.")

        self.logger.debug(f"[Conditional] Executing branch: '{branch_str}' with {len(steps)} step(s).")
        # Step import here to avoid circular issues
        from recipe_executor.steps.registry import STEP_REGISTRY

        for idx, step_conf in enumerate(steps):
            if not isinstance(step_conf, dict):
                raise ValueError(f"Step definition at index {idx} in '{branch_str}' is not a dictionary.")
            step_type = step_conf.get("type")
            step_cfg = step_conf.get("config", {})
            if step_type not in STEP_REGISTRY:
                raise ValueError(f"No registered step for type '{step_type}' in branch '{branch_str}'.")
            step_cls = STEP_REGISTRY[step_type]
            inner_logger = self.logger.getChild(f"{branch_str}.{step_type}[{idx}]")
            step = step_cls(inner_logger, step_cfg)
            await step.execute(context)


def _eval_condition(expr: str, context: ContextProtocol) -> bool:
    """
    Entry-point for evaluating a condition expr string given a context.
    """
    # Clean up leading/trailing spaces
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty condition expression is not allowed.")
    # Try parsing as logical ops first
    node = _parse_logical(expr)
    if node is not None:
        return _eval_logical_node(node, context)
    # Otherwise, fallback to direct expr
    return _eval_simple_expr(expr, context)


# ---- Simple expression parser below ----


def _parse_logical(expr: str) -> Optional[Dict[str, Any]]:
    # Logical ops: and(expr1, expr2), or(...), not(expr)
    # Ex: and(context['foo']==1, file_exists('bar'))
    expr = expr.strip()
    for op in ("and", "or", "not"):
        if expr.startswith(f"{op}(") and expr.endswith(")"):
            inside = expr[len(op) + 1 : -1].strip()
            parts = _split_args(inside)
            if op == "not":
                if len(parts) != 1:
                    raise ValueError("not(expr) must have exactly one argument.")
            elif len(parts) < 2:
                raise ValueError(f"{op}(...): Must have at least two arguments.")
            return {"type": op, "args": parts}
    return None


def _eval_logical_node(node: Dict[str, Any], context: ContextProtocol) -> bool:
    op: str = node["type"]
    parts: List[str] = node["args"]
    if op == "and":
        for p in parts:
            if not _eval_condition(p, context):
                return False
        return True
    elif op == "or":
        for p in parts:
            if _eval_condition(p, context):
                return True
        return False
    elif op == "not":
        return not _eval_condition(parts[0], context)
    raise ValueError(f"Unknown logical op '{op}' in AST.")


def _split_args(s: str) -> List[str]:
    # Parse expr1, expr2, ... for minimal paren-safe splitting
    args: List[str] = []
    cur = ""
    depth = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == "(":
            depth += 1
            cur += c
        elif c == ")":
            if depth == 0:
                raise ValueError("Mismatched parenthesis in condition.")
            depth -= 1
            cur += c
        elif c == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    if cur.strip():
        args.append(cur.strip())
    return args


def _eval_simple_expr(expr: str, context: ContextProtocol) -> bool:
    # File ops
    if expr.startswith("file_exists(") and expr.endswith(")"):
        arg = _extract_arg(expr)
        return _file_exists(_strip_quotes(arg), context)
    if expr.startswith("all_exist(") and expr.endswith(")"):
        arg = _extract_arg(expr)
        files = _eval_list_argument(arg, context)
        return all(_file_exists(f, context) for f in files)
    if expr.startswith("is_newer(") and expr.endswith(")"):
        arg = _extract_arg(expr)
        parts = _split_args(arg)
        if len(parts) != 2:
            raise ValueError("is_newer(source, target) requires exactly 2 arguments.")
        src, tgt = _strip_quotes(parts[0]), _strip_quotes(parts[1])
        return _file_is_newer(src, tgt, context)

    # Comparisons or contains/startswith
    for op_str in ["==", "!=", ">=", "<=", ">", "<"]:
        lhs, rhs = _split_binary(expr, op_str)
        if lhs is not None:
            if lhs is None or rhs is None:
                raise ValueError(f"Invalid binary expression: '{expr}'")
            left = _resolve_value(lhs, context)
            right = _resolve_value(rhs, context)
            fn = _COMPARISON_OPS[op_str]
            return fn(left, right)

    # contains(list, item)
    if expr.startswith("contains(") and expr.endswith(")"):
        arg = _extract_arg(expr)
        lst_str, item_str = _split_args(arg)
        lst = _resolve_value(lst_str, context)
        item = _resolve_value(item_str, context)
        try:
            return item in lst
        except Exception:
            return False

    # startswith(string, prefix)
    if expr.startswith("startswith(") and expr.endswith(")"):
        arg = _extract_arg(expr)
        s, prefix = _split_args(arg)
        s_val = _resolve_value(s, context)
        prefix_val = _resolve_value(prefix, context)
        try:
            return str(s_val).startswith(str(prefix_val))
        except Exception:
            return False

    # context['key'] or context["key"]
    if expr.startswith("context["):
        # Only truthiness check
        val = _resolve_value(expr, context)
        return _is_truthy(val)

    # bare true/false/null
    if expr in ("true", "True"):
        return True
    if expr in ("false", "False"):
        return False
    if expr in ("null", "None"):
        return False
    raise ValueError(f"Unsupported or invalid condition expression: '{expr}'")


# --- Value parsing utilities ---


def _extract_arg(expr: str) -> str:
    start = expr.find("(")
    end = expr.rfind(")")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Malformed function expression: '{expr}'")
    return expr[start + 1 : end].strip()


def _split_binary(expr: str, op: str) -> Union[tuple, tuple[None, None]]:
    # Only top-level op splitting, not inner parens
    idx = -1
    depth = 0
    for i, c in enumerate(expr):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif not depth and expr[i : i + len(op)] == op:
            idx = i
            break
    if idx == -1:
        return None, None
    lhs = expr[:idx].strip()
    rhs = expr[idx + len(op) :].strip()
    return lhs, rhs


def _resolve_value(val_expr: str, context: ContextProtocol) -> Any:
    # context[...]
    if val_expr.startswith("context["):
        return _extract_context_value(val_expr, context)
    # quoted string
    if (val_expr.startswith("'") and val_expr.endswith("'")) or (val_expr.startswith('"') and val_expr.endswith('"')):
        return val_expr[1:-1]
    # null/None
    if val_expr in ("null", "None"):
        return None
    if val_expr in ("true", "True"):
        return True
    if val_expr in ("false", "False"):
        return False
    # number?
    try:
        if "." in val_expr:
            return float(val_expr)
        return int(val_expr)
    except Exception:
        pass
    # fallback: as is
    return val_expr


def _extract_context_value(expr: str, context: ContextProtocol) -> Any:
    # Support context["key"] or context['a']["b"] and so on
    tokens: List[str] = []
    i = expr.find("[")
    while i < len(expr):
        if expr[i] == "[":
            j = i + 1
            if expr[j] in ('"', "'"):
                q = expr[j]
                k = j + 1
                while k < len(expr) and expr[k] != q:
                    k += 1
                tokens.append(expr[j + 1 : k])
                i = k + 1
            else:
                # e.g., context[NUMBER]
                k = j
                while k < len(expr) and expr[k] != "]":
                    k += 1
                tokens.append(expr[j:k])
                i = k
        elif expr[i] == "]":
            i += 1
        else:
            i += 1
    ref: Any = context
    for t in tokens:
        # context keys always from artifacts
        if isinstance(ref, ContextProtocol):
            obj = ref.get(t, None)
        elif isinstance(ref, dict):
            obj = ref.get(t, None)
        else:
            try:
                obj = ref[t]
            except Exception:
                obj = None
        ref = obj
    return ref


def _is_truthy(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (list, dict, str)):
        return bool(val)
    return True


def _file_exists(path: str, context: ContextProtocol) -> bool:
    try:
        return os.path.isfile(path)
    except Exception:
        return False


def _eval_list_argument(arg: str, context: ContextProtocol) -> List[str]:
    # Accepts either ["a", "b"] or ['a', ...] or context[...] value that resolves to list
    val = arg.strip()
    if val.startswith("[") and val.endswith("]"):
        body = val[1:-1].strip()
        items = _split_args(body)
        return [_strip_quotes(it) for it in items if it]
    # Try to resolve as context value
    result = _resolve_value(val, context)
    if isinstance(result, list):
        return result
    if isinstance(result, str):
        return [result]
    return []


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def _file_is_newer(src: str, tgt: str, context: ContextProtocol) -> bool:
    try:
        if not os.path.exists(src) or not os.path.exists(tgt):
            return False
        src_mtime = os.path.getmtime(src)
        tgt_mtime = os.path.getmtime(tgt)
        return src_mtime > tgt_mtime
    except Exception:
        return False
