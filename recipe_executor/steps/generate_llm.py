import logging
from typing import Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.llm import call_llm
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
    Step that generates content using a large language model (LLM).
    It processes templates for the prompt, model, and artifact key, calls the LLM, and stores the result in the context.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Process the artifact key using templating if needed
        artifact_key: str = self.config.artifact
        if '{{' in artifact_key and '}}' in artifact_key:
            try:
                artifact_key = render_template(artifact_key, context)
            except Exception as e:
                self.logger.error(f"Error rendering artifact template '{artifact_key}': {e}")
                raise ValueError(f"Invalid artifact template: {artifact_key}")

        # Render the prompt and model using the current context
        try:
            rendered_prompt: str = render_template(self.config.prompt, context)
        except Exception as e:
            self.logger.error(f"Error rendering prompt template: {e}")
            raise ValueError(f"Invalid prompt template: {self.config.prompt}")

        try:
            rendered_model: str = render_template(self.config.model, context)
        except Exception as e:
            self.logger.error(f"Error rendering model template: {e}")
            raise ValueError(f"Invalid model template: {self.config.model}")

        self.logger.debug(f"LLM call is being made for artifact '{artifact_key}' with model '{rendered_model}'.")

        # Call the LLM and store the response
        try:
            response = call_llm(rendered_prompt, rendered_model, logger=self.logger)
        except Exception as e:
            self.logger.error(f"LLM call failed for artifact '{artifact_key}': {e}", exc_info=True)
            raise RuntimeError(f"LLM call failed: {e}")

        context[artifact_key] = response
        self.logger.debug(f"LLM response stored in context under '{artifact_key}'")
