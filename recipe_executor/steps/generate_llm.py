import logging
from typing import List, Optional

from pydantic import BaseModel

from recipe_executor.llm_utils.llm import LLM
from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    GenerateWithLLMStep enables recipes to generate content using large language models (LLMs).
    It processes prompt templates using context data, handles model selection, makes LLM calls,
    and stores the generated result in the execution context under a dynamic artifact key.
    """

    def __init__(self, config: dict, logger: logging.Logger) -> None:
        super().__init__(logger, GenerateLLMConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the LLM generation step:
          1. Render the prompt using context data.
          2. Render the model identifier using context data.
          3. Log a debug message with call details.
          4. Call the LLM with the rendered prompt and model.
          5. Render the artifact key using context data and store the response.

        Args:
            context (ContextProtocol): Execution context implementing artifact storage.

        Raises:
            Exception: Propagates any exceptions from the LLM call for upstream handling.
        """
        rendered_prompt = ""  # Initialize before try block to avoid "possibly unbound" error
        try:
            # Render prompt, model, and artifact key using the provided context
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model: str = render_template(self.config.model, context)
            artifact_key: str = render_template(self.config.artifact, context)

            # Log debug message about the LLM call details
            self.logger.debug(f"Calling LLM with prompt: {rendered_prompt[:50]}... and model: {rendered_model}")

            class FileGenerationResult(BaseModel):
                """
                FileGenerationResult is a structured result from the LLM containing generated files and optional commentary.
                """

                files: List[FileSpec]
                commentary: Optional[str] = None

            # Call the LLM asynchronously
            llm = LLM(self.logger, model=rendered_model)
            response = await llm.generate(prompt=rendered_prompt, output_type=FileGenerationResult)

            # Store the generated result in the execution context
            context[artifact_key] = response

        except Exception as error:
            self.logger.error(f"LLM call failed for prompt: {rendered_prompt[:50]}... with error: {error}")
            raise
