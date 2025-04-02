import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from recipe_executor.context import Context  # Assumed to exist in the project


class StepConfig(BaseModel):
    """Base class for all step configurations. Extend this class in each step's configuration."""
    pass


# Type variable for configuration types bound to StepConfig
ConfigType = TypeVar('ConfigType', bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """
    Base class for all step implementations in the Recipe Executor system.
    Subclasses must implement the `execute` method.

    Each step is initialized with a configuration object and an optional logger.

    Args:
        config (ConfigType): Configuration for the step, validated using Pydantic.
        logger (Optional[logging.Logger]): Logger instance; defaults to the 'RecipeExecutor' logger.
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config}")

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Execute the step using the provided context.

        Args:
            context (Context): Shared context for data exchange between steps.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError("Each step must implement the `execute()` method.")
