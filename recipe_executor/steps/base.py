import logging
from typing import Any, Generic, TypeVar

from pydantic import BaseModel


# Avoid direct import to prevent cycles; use runtime import/type only for annotation
def _get_protocols():
    from recipe_executor.protocols import ContextProtocol  # type: ignore

    return ContextProtocol


class StepConfig(BaseModel):
    """
    Base class for step configuration objects. Extend this using Pydantic fields
    in your custom step config models. This base class defines no fields,
    enforcing only structure and validation via Pydantic.
    """

    pass


StepConfigType = TypeVar("StepConfigType", bound=StepConfig)


class BaseStep(Generic[StepConfigType]):
    """
    Base class for all steps. Implements common structure: stores config and logger,
    enforces async execute interface, and type safety for config via generics.
    """

    config: StepConfigType
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: StepConfigType) -> None:
        self.logger = logger
        self.config = config
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config.json()}")

    async def execute(self, context: Any) -> None:
        """
        Execute this step using a context implementing ContextProtocol.
        Subclasses must implement this method. This base method raises NotImplementedError
        as a safeguard.
        """
        ContextProtocol = _get_protocols()  # Delayed import for typing
        if not isinstance(context, ContextProtocol):
            raise TypeError(f"context must implement ContextProtocol, got {type(context)}")
        raise NotImplementedError(f"{self.__class__.__name__}.execute() must be implemented by subclasses.")
