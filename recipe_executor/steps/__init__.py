from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.llm_generate import LLMGenerateStep
from recipe_executor.steps.loop import LoopStep
from recipe_executor.steps.mcp import McpStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

# Register standard step implementations by updating the STEP_REGISTRY
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": McpStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})

__all__ = [
    "STEP_REGISTRY",
    "ExecuteRecipeStep",
    "LLMGenerateStep",
    "LoopStep",
    "McpStep",
    "ParallelStep",
    "ReadFilesStep",
    "WriteFilesStep",
]
