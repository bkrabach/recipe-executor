from typing import Any, Dict, TypeVar, Generic
import logging
from pydantic import BaseModel

# Delay import to avoid circular dependencies in type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for steps.
    All step configs should inherit from this class.
    """
    pass

StepConfigType = TypeVar("StepConfigType", bound=StepConfig)


class BaseStep(Generic[StepConfigType]):
    """
    Minimal base class for all step classes. Provides config parsing/validation and logging.
    Enforces async execute(context) contract.
    """
    config: StepConfigType
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: StepConfigType) -> None:
        self.logger = logger
        self.config = config
        self.logger.debug(f"{self.__class__.__name__} initialized with config: {self.config}")

    async def execute(self, context: 'ContextProtocol') -> None:
        """
        Perform the step's action.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.execute() must be implemented in a subclass.")
