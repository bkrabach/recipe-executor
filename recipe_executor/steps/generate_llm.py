import logging
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.steps.base import BaseStep, StepConfig
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
    GenerateWithLLMStep enables recipes to generate content using large language models.
    It processes prompt templates using context data, supports configurable model selection,
    calls the LLM for content generation, and then stores the generated results in the context.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert the config dict into a GenerateLLMConfig Pydantic model
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the LLM generation step by rendering templates, calling the LLM, and storing the result.

        Args:
            context (Context): The execution context containing artifacts and configuration.

        Raises:
            Exception: Propagates exceptions from LLM call failures.
        """
        try:
            # Render the prompt, model identifier, and artifact key using the provided context
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)
            artifact_key = render_template(self.config.artifact, context)

            self.logger.debug("Calling LLM with prompt: %s using model: %s", rendered_prompt, rendered_model)
            # Call the large language model with the rendered prompt and model identifier
            response = call_llm(rendered_prompt, rendered_model, logger=self.logger)

            # Store the generation result in the context under the dynamically rendered artifact key
            context[artifact_key] = response

        except Exception as e:
            self.logger.error("LLM call failed for prompt: %s with error: %s", self.config.prompt, str(e))
            raise e
