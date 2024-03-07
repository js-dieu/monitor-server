import inspect
import typing as t
from abc import ABC, abstractmethod
from functools import cached_property

from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, distinct, func, select, tuple_

from monitor_server.domain.models.abc import Entity
from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.errors import ORMInvalidMapping
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.persistence.exceptions import EntityNotFound
from monitor_server.infrastructure.persistence.mapper import ORMMapper

Model = t.TypeVar('Model', bound=ORMModel)
DomainObject = t.TypeVar('DomainObject', bound=Entity)


def _get_domain(repository: t.Any) -> t.Type[Entity]:
    domain: t.Type[Entity] | None = None
    for generic_base in repository.__orig_bases__:  # type: ignore
        for arg in t.get_args(generic_base):
            if not inspect.isclass(arg) or not issubclass(arg, Entity):
                continue
            if domain is not None:
                raise ORMInvalidMapping(
                    f'multiple domain object found for repository {repository.__class__.__name__}: ({domain}, {arg})',
                )
            domain = arg
    if domain is None:
        raise ORMInvalidMapping(
            f'no domain object found for repository {repository.__class__.__name__}',
        )
    return domain


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


class CRUDRepositoryABC(ABC, t.Generic[DomainObject, Model]):
    @abstractmethod
    def create(self, item: DomainObject) -> DomainObject:
        """Persist the given item. Must be unrecorded."""

    @abstractmethod
    def update(self, machine: DomainObject) -> DomainObject:
        """Update an existing row"""

    @abstractmethod
    def get(self, uid: str) -> DomainObject:
        """Get the model with given uid"""

    @abstractmethod
    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[DomainObject]]:
        """List all row using a paging system"""

    @abstractmethod
    def count(self) -> int:
        """Count the number of items in this repository"""

    @abstractmethod
    def truncate(self) -> None:
        """Remove all entries from this repository"""


class CRUDRepositoryBase(CRUDRepositoryABC[DomainObject, Model], ABC):
    def __init__(self) -> None:
        self.model = _get_model(self)  # type: ignore[assignment]
        self.domain = _get_domain(self)  # type: ignore[assignment]
        self.mapper = ORMMapper()


class SQLRepository(CRUDRepositoryBase[DomainObject, Model], ABC):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def get(self, uid: str) -> DomainObject:
        where = tuple(
            c == v for c, v in zip(tuple(getattr(self.model, a) for a in self.primary_key), (uid,), strict=False)
        )
        q = self.session.query(self.model).where(*where)
        row = q.one_or_none()
        if row is not None:
            row = t.cast(Model, q.one_or_none())
            return t.cast(DomainObject, self.mapper.cast_model(row, self.domain))
        raise EntityNotFound(self.domain, uid)

    @cached_property
    def primary_key(self) -> t.Tuple[str, ...]:
        return tuple(self.model.__table__.primary_key.columns.keys())  # type: ignore

    def count(self) -> int:
        primary_key = tuple(getattr(self.model, a) for a in self.primary_key)
        return (
            self.session.execute(
                select(self.model).with_only_columns(
                    # Operand should contain 1 column(s) error in case of composite primary key
                    func.count(distinct(tuple_(*primary_key))),
                ),
            )
        ).scalar_one()

    def truncate(self) -> None:
        self.session.execute(delete(self.model))
        self.session.commit()
        self.session.close()


class InMemoryRepository(CRUDRepositoryBase[DomainObject, Model], ABC):
    def __init__(self) -> None:
        super().__init__()
        self._data: t.Dict[t.Any, Model] = {}

    def count(self) -> int:
        return len(self._data)

    def truncate(self) -> None:
        self._data = {}
