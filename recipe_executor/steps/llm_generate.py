# recipe_executor/steps/llm_generate.py

from pydantic_ai import Agent
from recipe_executor import config

def execute(step, context):
    """
    Execute an llm_generate step: use an LLM to generate content from a prompt.
    The output is stored in the context (with a key if provided, otherwise an auto-generated step key).
    """
    prompt = step.prompt
    model_name = config.Config.DEFAULT_MODEL
    # Initialize the LLM agent with the specified model
    agent = Agent(model_name)
    result_text = None
    # Attempt the LLM call with up to 3 retries for transient errors
    for attempt in range(1, 4):
        try:
            result = agent.run_sync(prompt)  # synchronous call to the model
            result_text = str(result.data)   # ensure we have a string output
            break  # success, break out of retry loop
        except Exception as e:
            err_msg = str(e).lower()
            # Check for transient error indicators
            if "rate limit" in err_msg or "timeout" in err_msg or "transient" in err_msg:
                if attempt < 3:
                    import time
                    time.sleep(1)  # brief pause before retry
                    continue  # retry the loop
            # Not a transient error (or max retries reached): propagate the exception
            raise
    # Store the LLM output in context
    key = step.output_key or f"step_{len(context) + 1}"
    context[key] = result_text
    return result_text
