import inspect
import typing as t
from abc import ABC, abstractmethod
from functools import cached_property

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, distinct, func, insert, select, tuple_, update

from monitor_server.domain.models.abc import Entity
from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.errors import ORMError, ORMInvalidMapping
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.orm.presenter import presenter
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound

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
    def delete(self, uid: str) -> None:
        """Remove a single model given its uid"""

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
        self.model: t.Type[Model] = _get_model(self)  # type: ignore[assignment]
        self.domain: t.Type[DomainObject] = _get_domain(self)  # type: ignore[assignment]


class SQLRepository(CRUDRepositoryBase[DomainObject, Model]):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def update(self, item: DomainObject) -> DomainObject:
        clause = tuple(
            c == v for c, v in zip(tuple(getattr(self.model, a) for a in self.primary_key), (item.uid,), strict=False)
        )
        args = presenter.to_orm(item, as_=self.model).as_dict()
        stmt = update(self.model).where(*clause).values(**args)
        try:
            self.session.execute(stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return item

    def create(self, item: DomainObject) -> DomainObject:
        args = presenter.to_orm(item, as_=self.model).as_dict()
        try:
            stmt = insert(self.model).values(**args)
            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError as e:
            raise EntityAlreadyExists(self.domain, item.uid.hex) from e
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return item

    def get(self, uid: str) -> DomainObject:
        where = tuple(
            c == v for c, v in zip(tuple(getattr(self.model, a) for a in self.primary_key), (uid,), strict=False)
        )
        q = self.session.query(self.model).where(*where)
        row = q.one_or_none()
        if row is not None:
            row = t.cast(Model, q.one_or_none())
            return presenter.from_orm(row, as_=self.domain)
        raise EntityNotFound(self.domain, uid)

    def delete(self, uid: str) -> None:
        where = tuple(
            c == v for c, v in zip(tuple(getattr(self.model, a) for a in self.primary_key), (uid,), strict=False)
        )
        stmt = delete(self.model).where(*where)
        try:
            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError as e:
            raise EntityNotFound(self.domain, uid) from e
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e

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

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[DomainObject]]:
        q = self.session.query(self.model)
        count = 0
        if page_info:
            q = q.limit(page_info.page_size).offset(page_info.offset)
            count = self.count()

        rows = t.cast(t.Iterable[Model], q.all() or [])
        values = t.cast(t.List[DomainObject], [presenter.from_orm(row, as_=self.domain) for row in rows])
        if not page_info:
            return PaginatedResponse(data=values, page_no=None, next_page=None)
        return page_info.build_response(values, elements_count=count)

    def truncate(self) -> None:
        self.session.execute(delete(self.model))
        self.session.commit()
        self.session.close()


class InMemoryRepository(CRUDRepositoryBase[DomainObject, Model]):
    def __init__(self) -> None:
        super().__init__()
        self._data: t.Dict[t.Any, Model] = {}

    def count(self) -> int:
        return len(self._data)

    def truncate(self) -> None:
        self._data = {}

    def get(self, uid: str) -> DomainObject:
        row = self._data.get(uid)
        if row is None:
            raise EntityNotFound(self.domain, uid)

        return presenter.from_orm(row, as_=self.domain)

    def create(self, item: DomainObject) -> DomainObject:
        if item.uid.hex in self._data:
            raise EntityAlreadyExists(self.domain, item.uid.hex)
        self._data[item.uid.hex] = presenter.to_orm(item, as_=self.model)
        return item

    def update(self, item: DomainObject) -> DomainObject:
        if item.uid.hex not in self._data:
            raise EntityNotFound(self.domain, item.uid.hex)
        self._data[item.uid.hex] = presenter.to_orm(item, as_=self.model)
        return item

    def delete(self, uid: str) -> None:
        if uid not in self._data:
            raise EntityNotFound(self.domain, uid)
        del self._data[uid]

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[DomainObject]]:
        ids = sorted(self._data)
        if page_info is None:
            return PaginatedResponse(
                data=[presenter.from_orm(self._data[an_id], as_=self.domain) for an_id in ids],
                page_no=None,
                next_page=None,
            )
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        return page_info.build_response(
            data=[presenter.from_orm(self._data[an_id], as_=self.domain) for an_id in ids[page]],
            elements_count=self.count(),
        )
