import logging

# Do function-level import to avoid cycles in type hints (see Protocols)
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from recipe_executor.protocols import ContextProtocol


# Base configuration class for all steps
class StepConfig(BaseModel):
    """
    Pydantic model that serves as the base for all step configuration models.
    Subclasses should define concrete config fields.
    """

    pass


# Type variable for StepConfig subclasses
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(Generic[ConfigType]):
    """
    Base class for steps, enforcing interface and type safety.
    All step implementations should subclass BaseStep, specifying their config type.
    """

    config: ConfigType
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: ConfigType) -> None:
        self.logger = logger
        self.config = config
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config.json()}")

    async def execute(self, context: "ContextProtocol") -> None:
        """Perform the step's action using the provided context. Must be implemented by subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__}.execute() must be implemented in subclasses.")
