import logging
from typing import Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.llm_utils.llm import call_llm
from recipe_executor.utils import render_template


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider:model_name format).
        artifact: The name under which to store the LLM response in context.
    """
    prompt: str
    model: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    GenerateWithLLMStep executes an LLM call using a templated prompt and model.
    The result is stored in the context under a dynamically rendered artifact key.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: ContextProtocol) -> None:
        """
        Executes the generate_llm step:
          - Renders prompt and model using the context
          - Calls the LLM with the rendered prompt and model
          - Renders artifact key and stores the result in the context
        """
        try:
            # Render the prompt and model identifier from the configuration using the context values
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)

            self.logger.debug(f"Calling LLM with prompt: {rendered_prompt} and model: {rendered_model}")

            # Call the LLM with the rendered prompt and model
            result = call_llm(prompt=rendered_prompt, model=rendered_model, logger=self.logger)

            # Render the artifact key to store the generation result
            artifact_key = render_template(self.config.artifact, context)
            context[artifact_key] = result
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}", exc_info=True)
            raise e
