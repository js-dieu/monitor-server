import abc
import typing as t

from monitor_server.domain.models.abc import Model

INPUT = t.TypeVar('INPUT', bound=Model)
OUTPUT = t.TypeVar('OUTPUT', bound=Model)


class UseCase(t.Generic[INPUT, OUTPUT], abc.ABC):
    @abc.abstractmethod
    def execute(self, input_dto: INPUT) -> OUTPUT:
        """Implements the business logic"""


class UseCaseWithoutInput(t.Generic[OUTPUT], abc.ABC):
    @abc.abstractmethod
    def execute(self) -> OUTPUT:
        """Implements the business logic"""
