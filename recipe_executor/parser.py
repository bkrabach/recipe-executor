# recipe_executor/parser.py

import os
import re
from recipe_executor import config, models

def parse_recipe(recipe_name_or_path: str) -> models.Recipe:
    """
    Parse a recipe file (Markdown) into a Recipe object with structured steps.
    `recipe_name_or_path` can be a recipe name (without extension) or a file path.
    """
    # Determine the file path for the recipe
    if os.path.isfile(recipe_name_or_path):
        filepath = recipe_name_or_path
    else:
        # If a name is given, construct path in the recipes directory (add .md if missing)
        name = recipe_name_or_path
        if not name.endswith(".md"):
            name = name + ".md"
        filepath = os.path.join(config.Config.RECIPES_DIR, name)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Recipe file not found: {filepath}")

    recipe_name = os.path.splitext(os.path.basename(filepath))[0]
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    steps = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue  # skip empty lines
        # Identify list items (ordered "1." or unordered "-" or "*")
        if re.match(r'^(\d+\.)|(^-)|(^\*)', stripped):
            # Remove the list marker (e.g., "1." or "-" or "*") from the line
            step_text = re.sub(r'^(\d+\.)|^[-*]\s*', '', stripped).strip()
            # Interpret this step text into a Step model
            step_model = interpret_step(step_text)
            steps.append(step_model)
    # Construct and return the Recipe model
    recipe = models.Recipe(name=recipe_name, steps=steps)
    return recipe

def interpret_step(step_text: str):
    """
    Infer the step type from a step description and return the appropriate Step model.
    """
    text_lower = step_text.lower()
    # Decide step type based on keywords present in the text
    if "recipe" in text_lower or "sub-recipe" in text_lower or "run recipe" in text_lower:
        # Likely a sub-recipe call, e.g. "Run recipe OtherRecipe"
        match = re.search(r'recipe\s+\"?([\w\-\.]+)\"?', text_lower)
        recipe_name = match.group(1) if match else step_text.split()[-1]
        return models.RunRecipeStep(type='run_recipe', recipe=recipe_name)
    elif "command" in text_lower or text_lower.startswith("run "):
        # A shell command execution, e.g. "Run command ls -al"
        cmd = step_text
        if cmd.lower().startswith("run command"):
            # Remove the "run command" prefix
            parts = step_text.split(" ", 2)
            cmd = parts[2] if len(parts) > 2 else ""
        elif cmd.lower().startswith("run"):
            # Remove the "run " prefix for phrases like "run ls -al"
            cmd = step_text[len("run"):].strip(": ")
        return models.RunCommandStep(type='run_command', command=cmd)
    elif "file" in text_lower or "write" in text_lower:
        # A file write step, e.g. "Write the summary to file summary.txt"
        # Extract content and file path
        match = re.match(r'write (.+) to file (\S+)', text_lower)
        if match:
            content = match.group(1)
            path = match.group(2)
        else:
            # Fallback: split by " to " in case of a slightly different phrasing
            parts = text_lower.split(" to ")
            content = parts[0].replace("write", "").strip()
            path = parts[1] if len(parts) > 1 else "output.txt"
        # Note: content might be a reference like "the summary", to be resolved at execution time.
        return models.FileWriteStep(type='file_write', path=path, content=content)
    else:
        # Default: treat as an LLM generation step.
        # The entire step text (or a quoted portion of it) is the prompt.
        prompt = step_text
        # If the prompt is quoted in the text, extract the quoted part as the actual prompt
        if '"' in step_text or "'" in step_text:
            first_quote = step_text.find('"') if '"' in step_text else step_text.find("'")
            last_quote = step_text.rfind('"') if '"' in step_text else step_text.rfind("'")
            if first_quote != -1 and last_quote != -1 and last_quote > first_quote:
                prompt = step_text[first_quote+1:last_quote]
        return models.LLMGenerateStep(type='llm_generate', prompt=prompt)
