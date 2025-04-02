from recipe_executor.steps.registry import STEP_REGISTRY

from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register standard steps in the registry
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_file": ReadFileStep,
    "write_files": WriteFilesStep,
})
