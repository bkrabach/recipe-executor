"""
Run Command Step implementation for the Recipe Executor CLI tool.

This step executes a shell command and returns its output. It also performs
placeholder substitution on the command string using the provided context.
"""

import logging
import subprocess
from typing import Optional
from recipe_executor.models import Step

class RunCommandStep(Step):
    """
    Step that runs a shell command.

    Attributes:
        type: The step type identifier ("run_command").
        name: An optional name for the step.
        command: The shell command to execute.
    """
    type: str = "run_command"
    name: Optional[str] = None
    command: str

    def execute(self, context: dict) -> str:
        """
        Execute the command after performing placeholder substitution with the context.

        Args:
            context: A dictionary holding shared execution state. Placeholders in the command
                     should be formatted as {{key}} and will be replaced by the corresponding value.

        Returns:
            The stdout output from the executed command.

        Raises:
            subprocess.CalledProcessError: If the command returns a non-zero exit status.
        """
        root = context.get("root", "")
        logging.info("Executing RunCommandStep: running command '%s' with cwd '%s'", self.command, root)

        try:
            command_to_run = self.command

            # Substitute placeholders in the command using the context.
            for key, value in context.items():
                command_to_run = command_to_run.replace(f"{{{{{key}}}}}", str(value))
            result = subprocess.run(command_to_run, shell=True, capture_output=True, text=True, cwd=root)
            result.check_returncode()
            output = result.stdout.strip()

            logging.debug("Command '%s' executed successfully. Output: %s", command_to_run, output)

            return output

        except subprocess.CalledProcessError as e:
            logging.error("Command '%s' failed: %s", self.command, e)
            raise

    model_config = {"extra": "forbid"}
