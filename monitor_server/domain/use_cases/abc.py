import abc
import dataclasses
import typing as t

from monitor_server.domain.dto.abc import DTO

INPUT = t.TypeVar('INPUT', bound=DTO)
OUTPUT = t.TypeVar('OUTPUT', bound=DTO)


@dataclasses.dataclass(eq=True, init=True)
class UseCaseResult(t.Generic[OUTPUT]):
    status: bool
    data: OUTPUT
    msg: str | None = None


RESULT: t.TypeAlias = UseCaseResult[OUTPUT]


class UseCase(t.Generic[INPUT, OUTPUT], abc.ABC):
    @abc.abstractmethod
    def execute(self, input_dto: INPUT) -> RESULT:
        """Implements the business logic"""
