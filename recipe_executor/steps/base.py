import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

from recipe_executor.context import Context

# Base configuration class for all step configurations
class StepConfig(BaseModel):
    """Base class for step configurations. Extend this class for specific steps."""
    pass

# Generic type variable for step configuration types
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """Base class for all step implementations in the Recipe Executor system.

    Subclasses must implement the execute(context) method. Each step receives a config
    object and a logger instance. If no logger is provided, a default logger named 'RecipeExecutor'
    will be used.

    Args:
        config (ConfigType): Configuration for the step.
        logger (Optional[logging.Logger]): Logger instance; defaults to a logger with name "RecipeExecutor".
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")
        # Log at debug level when the step component is initialized
        self.logger.debug(f"Step component initialized with configuration: {self.config.json()}")

    @abstractmethod
    def execute(self, context: Context) -> None:
        """Execute the step with the given context.

        Args:
            context: A context object for data sharing among steps.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Each step must implement the execute() method.")

