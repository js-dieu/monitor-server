import abc
import typing as t

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from monitor_server.domain.entities.machines import Machine
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.pageable import PageableStatement
from monitor_server.infrastructure.orm.repositories import InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.mapper import ORMMapper
from monitor_server.infrastructure.persistence.models import ExecutionContext


class ExecutionContextRepository:
    @abc.abstractmethod
    def create(self, item: Machine) -> Machine:
        """Persist a new context"""

    @abc.abstractmethod
    def update(self, machine: Machine) -> Machine:
        """Update an existing context"""

    @abc.abstractmethod
    def get(self, uid: str) -> Machine:
        """Get an execution context given an uid"""

    @abc.abstractmethod
    def list(self, page_info: PageableStatement | None = None) -> t.List[Machine]:
        """List all ids of known machine"""

    @abc.abstractmethod
    def count(self) -> int:
        """Count the number of items in this repository"""


class ExecutionContextSQLRepository(ExecutionContextRepository, SQLRepository[ExecutionContext]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def count(self) -> int:
        return super()._count()

    def create(self, machine: Machine) -> Machine:
        stmt = insert(ExecutionContext).values(
            uid=machine.footprint,
            cpu_frequency=machine.cpu_frequency,
            cpu_vendor=machine.cpu_vendor,
            cpu_count=machine.cpu_count,
            cpu_type=machine.cpu_type,
            total_ram=machine.total_ram,
            hostname=machine.hostname,
            machine_type=machine.machine_type,
            machine_arch=machine.machine_arch,
            system_info=machine.system_info,
            python_info=machine.python_info,
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError as e:
            raise EntityAlreadyExists(
                f'Machine "{machine.footprint}" already exists', Machine, machine.footprint
            ) from e
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return machine

    def update(self, machine: Machine) -> Machine:
        stmt = (
            update(self.model)
            .where(ExecutionContext.uid == machine.footprint)
            .values(
                uid=machine.footprint,
                cpu_frequency=machine.cpu_frequency,
                cpu_vendor=machine.cpu_vendor,
                cpu_count=machine.cpu_count,
                cpu_type=machine.cpu_type,
                total_ram=machine.total_ram,
                hostname=machine.hostname,
                machine_type=machine.machine_type,
                machine_arch=machine.machine_arch,
                system_info=machine.system_info,
                python_info=machine.python_info,
            )
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return machine

    def get(self, uid: str) -> Machine:
        stmt = select(self.model).where(ExecutionContext.uid == uid)
        row = self.session.execute(stmt).fetchone()
        if row is not None:
            return ORMMapper().orm_execution_context_to_entity(row[0])
        raise EntityNotFound(f'Machine {uid} cannot be found', Machine, uid)

    def list(self, page_info: PageableStatement | None = None) -> t.List[Machine]:
        q = self.session.query(self.model)
        if page_info:
            q = q.limit(page_info.page_size).offset(page_info.offset)
        rows = t.cast(t.Iterable[ExecutionContext], q.all())
        mapper = ORMMapper()
        return [mapper.orm_execution_context_to_entity(row) for row in rows or []]


class ExecutionContextInMemRepository(ExecutionContextRepository, InMemoryRepository[ExecutionContext]):
    def __init__(self) -> None:
        super().__init__()

    def create(self, machine: Machine) -> Machine:
        if machine.footprint in self._data:
            raise EntityAlreadyExists(f'Machine "{machine.footprint}" already exists', Machine, machine.footprint)
        self._data[machine.footprint] = t.cast(ExecutionContext, self.model).from_dict(machine.as_dict())
        return machine

    def update(self, machine: Machine) -> Machine:
        if machine.footprint not in self._data:
            raise EntityNotFound(f'Machine "{machine.footprint}" cannot be found', Machine, machine.footprint)
        self._data[machine.footprint] = t.cast(ExecutionContext, self.model).from_dict(machine.as_dict())
        return machine

    def get(self, uid: str) -> Machine:
        row = self._data.get(uid)
        if not row:
            raise EntityNotFound(f'Machine "{uid}" cannot be found', Machine, uid)
        return ORMMapper().orm_execution_context_to_entity(row)

    def list(self, page_info: PageableStatement | None = None) -> t.List[Machine]:
        mapper = ORMMapper()
        if page_info is None:
            return [
                mapper.orm_execution_context_to_entity(machine)
                for machine in sorted(self._data.values(), key=lambda m: m.uid)
            ]
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        element_ids = sorted(self._data.keys())[page]
        return [mapper.orm_execution_context_to_entity(self._data[element_id]) for element_id in element_ids]

    def count(self) -> int:
        return super()._count()
