"""
LLM Generate Step implementation for the Recipe Executor CLI tool.

This step generates text using an LLM. It substitutes placeholders in the provided prompt,
invokes the LLM, and stores the generated text in the shared execution context.
"""

import logging
from typing import Optional
from recipe_executor.models import Step
from recipe_executor.llm import get_model
from recipe_executor.config import DEFAULT_MODEL

class LLMGenerateStep(Step):
    """
    Step that generates text using a language model.

    Attributes:
        type: The step type identifier ("llm_generate").
        name: An optional name for the step.
        prompt: The prompt text for the LLM. May include placeholders to be substituted.
        model_name: Optional model identifier; if not provided, DEFAULT_MODEL is used.
    """
    type: str = "llm_generate"
    name: Optional[str] = None
    prompt: str
    model_name: Optional[str] = None

    def execute(self, context: dict) -> str:
        """
        Execute the LLM generation step by:
          1. Substituting any placeholders in the prompt using the context.
          2. Invoking the LLM to generate text.
          3. Storing the generated text in the context.

        Args:
            context: A dictionary holding shared execution state.

        Returns:
            The generated text.
        """

        logging.info("Executing LLMGenerateStep with prompt: '%s'", self.prompt)

        try:
            # Substitute context values in the prompt (e.g., replace {{key}} with context[key]).
            processed_prompt = self.prompt
            for key, value in context.items():
                processed_prompt = processed_prompt.replace(f"{{{{{key}}}}}", str(value))

            # Determine which model to use.
            model_id = self.model_name or DEFAULT_MODEL
            model = get_model(model_id)

            # Create an LLM agent to perform text generation.
            # Note: For simple text generation, we assume the result type is a plain string.
            from pydantic_ai import Agent
            agent = Agent(model, result_type=str, system_prompt="")
            result = agent.run_sync(processed_prompt)
            if not result or result.data is None:
                raise Exception("LLM returned no result")
            generated_text = result.data
            logging.debug("LLM response (truncated): '%s'", generated_text)

            # Store the result in the context using the provided name or a generated key.
            context[self.name or f"llm_generate_{len(context)}"] = generated_text
            return generated_text

        except Exception as e:
            logging.error("Error in LLMGenerateStep: %s", e)
            raise

    model_config = {"extra": "forbid"}
