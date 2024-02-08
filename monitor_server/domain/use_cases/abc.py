import abc
import typing as t

from monitor_server.domain.dto.abc import DTO

INPUT = t.TypeVar('INPUT', bound=DTO)
OUTPUT = t.TypeVar('OUTPUT', bound=DTO)


class UseCase(t.Generic[INPUT, OUTPUT], abc.ABC):
    @abc.abstractmethod
    def execute(self, input_dto: INPUT) -> OUTPUT:
        """Implements the business logic"""
