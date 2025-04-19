import logging
from typing import Generic, TypeVar

from pydantic import BaseModel

# Type variable for StepConfig typing
StepConfigType = TypeVar("StepConfigType", bound="StepConfig")


class StepConfig(BaseModel):
    """
    Base configuration model for step implementations.
    Intended to be subclassed by specific steps with their own fields.
    """

    pass


class BaseStep(Generic[StepConfigType]):
    """
    Base class for all step implementations.
    Provides structure, config validation, and logging for steps.
    """

    config: StepConfigType
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: StepConfigType) -> None:
        self.logger = logger
        self.config = config
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config}")

    async def execute(self, context: "ContextProtocol") -> None:
        """
        Execute the step within the provided context.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.execute() must be implemented by subclass.")


# Defer import to avoid circular dependencies due to Protocols depending on Steps and vice versa
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from recipe_executor.protocols import ContextProtocol
