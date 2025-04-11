import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

# Import the ContextProtocol from the protocols component
from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for step implementations.

    This class is intentionally left minimal and should be extended by concrete step configurations.
    """
    pass


# Create a type variable that must be a subclass of StepConfig
ConfigType = TypeVar('ConfigType', bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """
    Abstract base class for all steps in the Recipe Executor system.

    Attributes:
        config (ConfigType): The configuration instance for the step.
        logger (logging.Logger): Logger to record operations, defaults to a module logger named 'RecipeExecutor'.
    """
    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger: logging.Logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"{self.__class__.__name__} initialized with config: {self.config}")

    @abstractmethod
    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step with the provided context.

        Args:
            context (ContextProtocol): Execution context conforming to the ContextProtocol interface.

        Raises:
            NotImplementedError: If a subclass does not implement the execute method.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")
