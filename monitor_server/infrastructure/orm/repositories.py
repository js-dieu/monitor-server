import inspect
import typing as t
from abc import ABC
from functools import cached_property

from sqlalchemy.orm import Session

from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.errors import ORMInvalidMapping

Model = t.TypeVar('Model', bound=ORMModel)


def _get_model(repository: t.Any) -> t.Type[ORMModel]:
    model: t.Type[ORMModel] | None = None
    for generic_base in repository.__orig_bases__:  # type: ignore
        for arg in t.get_args(generic_base):
            if not inspect.isclass(arg) or not issubclass(arg, ORMModel):
                continue
            if model is not None:
                raise ORMInvalidMapping(
                    f'multiple model found for repository {repository.__class__.__name__}: ({model}, {arg})',
                )
            model = arg
    if model is None:
        raise ORMInvalidMapping(
            f'no model found for repository {repository.__class__.__name__}',
        )
    return model


class RepositoryBase(ABC, t.Generic[Model]):
    def __init__(self) -> None:
        self.model = _get_model(self)  # type: ignore[assignment]


class SQLRepository(RepositoryBase[Model]):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    @cached_property
    def primary_key(self) -> t.Tuple[str, ...]:
        return tuple(self.model.__table__.primary_key.columns.keys())  # type: ignore


class InMemoryRepository(RepositoryBase[Model]):
    def __init__(self) -> None:
        super().__init__()
        self._data: t.Dict[t.Any, Model] = {}
