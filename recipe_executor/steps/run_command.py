# recipe_executor/steps/run_command.py

import subprocess

def execute(step, context):
    """
    Execute a run_command step: run a shell command and capture its output.
    The output (stdout, stderr, and return code) is stored in context.
    """
    command = step.command
    # Run the command in a shell, capturing output and errors
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed.stdout
    error = completed.stderr
    result = {
        "returncode": completed.returncode,
        "output": output,
        "error": error
    }
    # Store the command result in context with a new step key
    key = f"step_{len(context) + 1}"
    context[key] = result
    return result
