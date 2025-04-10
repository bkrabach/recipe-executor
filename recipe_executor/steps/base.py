import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

# Assuming ContextProtocol is defined in recipe_executor.protocols
from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """Base configuration class for steps using Pydantic.

    This class serves as the foundation for step-specific configuration models.
    Concrete steps should subclass this to define their own configuration attributes.
    """
    pass


# Define a TypeVar for configuration types that extend StepConfig
ConfigType = TypeVar('ConfigType', bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """Abstract base class for all steps in the Recipe Executor system.

    This class defines the common interface and behavior for steps. Concrete steps must
    implement the execute method.
    """
    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        """Initialize the step with a given configuration and an optional logger.

        Args:
            config (ConfigType): The configuration for the step, validated using Pydantic.
            logger (Optional[logging.Logger]): An optional logger. If not provided, a default
                                                 logger named 'RecipeExecutor' is used.
        """
        self.config: ConfigType = config
        self.logger: logging.Logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"Initialized step {self.__class__.__name__} with config: {self.config}")

    @abstractmethod
    def execute(self, context: ContextProtocol) -> None:
        """Execute the step with the provided context.

        Concrete implementations must override this method to perform step-specific actions.
        
        Args:
            context (ContextProtocol): The execution context which allows interaction with the
                                         shared state of the recipe execution.
        
        Raises:
            NotImplementedError: If not overridden in a subclass.
        """
        raise NotImplementedError(f"The execute method is not implemented in {self.__class__.__name__}")
