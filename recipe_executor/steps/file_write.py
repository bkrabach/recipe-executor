# recipe_executor/steps/file_write.py

import os
from recipe_executor import config

def execute(step, context):
    """
    Execute a file_write step: write given content to the specified file path.
    The path may be relative to the output root.
    """
    # Resolve the full file path relative to output root if not an absolute path
    output_root = config.Config.OUTPUT_ROOT
    path = step.path
    if not os.path.isabs(path):
        full_path = os.path.join(output_root, path)
    else:
        full_path = path
    # Ensure the directory for the file exists
    os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
    content = step.content
    # Substitute context variables in content if any placeholders are present (e.g., {{step_1}})
    if "{{" in content:
        for key, val in context.items():
            content = content.replace(f"{{{{{key}}}}}", str(val))
    # Write content to the file (overwrites if exists)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    # Returning the file path might be useful for logging or future extension
    return full_path
