import abc
import typing as t

from sqlalchemy import Integer, String, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Mapped, Session, mapped_column

from monitor_server.domain.entities.machines import Machine
from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.repositories import InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import MachineAlreadyExists, MachineError, MachineNotFound


class ExecutionContext(ORMModel):
    uid: Mapped[str] = mapped_column(String(64), nullable=False, primary_key=True)
    cpu_frequency: Mapped[int] = mapped_column(Integer(), nullable=False)
    cpu_vendor: Mapped[str] = mapped_column(String(256), nullable=False)
    cpu_count: Mapped[int] = mapped_column(Integer(), nullable=False)
    cpu_type: Mapped[str] = mapped_column(String(64), nullable=False)
    total_ram: Mapped[int] = mapped_column(Integer(), nullable=False)
    hostname: Mapped[str] = mapped_column(String(512), nullable=False)
    machine_type: Mapped[str] = mapped_column(String(32), nullable=False)
    machine_arch: Mapped[str] = mapped_column(String(16), nullable=False)
    system_info: Mapped[str] = mapped_column(String(256), nullable=False)
    python_info: Mapped[str] = mapped_column(String(512), nullable=False)

    @classmethod
    def from_dict(cls, data: t.Dict[str, t.Any]) -> 'ExecutionContext':
        return cls(
            uid=data.get('footprint', data['uid']),
            cpu_frequency=data['cpu_frequency'],
            cpu_vendor=data['cpu_vendor'],
            cpu_count=data['cpu_count'],
            cpu_type=data['cpu_type'],
            total_ram=data['total_ram'],
            hostname=data['hostname'],
            machine_type=data['machine_type'],
            machine_arch=data['machine_arch'],
            system_info=data['system_info'],
            python_info=data['python_info'],
        )


class ExecutionContextRepository:
    @classmethod
    def build_entity_from(cls, model: ExecutionContext) -> Machine:
        return Machine(
            uid=model.uid,
            cpu_frequency=model.cpu_frequency,
            cpu_vendor=model.cpu_vendor,
            cpu_count=model.cpu_count,
            cpu_type=model.cpu_type,
            total_ram=model.total_ram,
            hostname=model.hostname,
            machine_type=model.machine_type,
            machine_arch=model.machine_arch,
            system_info=model.system_info,
            python_info=model.python_info,
        )

    @abc.abstractmethod
    def create(self, item: Machine) -> Machine:
        """Persist a new context"""

    @abc.abstractmethod
    def update(self, machine: Machine) -> Machine:
        """Update an existing context"""

    @abc.abstractmethod
    def get(self, uid: str) -> Machine:
        """Get an execution context given an uid"""


class ExecutionContextSQLRepository(ExecutionContextRepository, SQLRepository[ExecutionContext]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

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
            raise MachineAlreadyExists(machine.footprint) from e
        except SQLAlchemyError as e:
            raise MachineError(str(e)) from e
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
            raise MachineError(str(e)) from e
        return machine

    def get(self, uid: str) -> Machine:
        stmt = select(self.model).where(ExecutionContext.uid == uid)
        row = self.session.execute(stmt).fetchone()
        if row is not None:
            return self.build_entity_from(row[0])
        raise MachineNotFound(uid)


class ExecutionContextInMemRepository(ExecutionContextRepository, InMemoryRepository[ExecutionContext]):
    def __init__(self) -> None:
        super().__init__()

    def create(self, machine: Machine) -> Machine:
        if machine.footprint in self._data:
            raise MachineAlreadyExists(machine.footprint)
        self._data[machine.footprint] = t.cast(ExecutionContext, self.model).from_dict(machine.as_dict())
        return machine

    def update(self, machine: Machine) -> Machine:
        try:
            self._data[machine.footprint] = t.cast(ExecutionContext, self.model).from_dict(machine.as_dict())
        except KeyError as e:
            raise MachineError(e) from e
        return machine

    def get(self, uid: str) -> Machine:
        row = self._data.get(uid)
        if not row:
            raise MachineNotFound(uid)
        return Machine(
            uid=row.uid,
            cpu_frequency=row.cpu_frequency,
            cpu_vendor=row.cpu_vendor,
            cpu_count=row.cpu_count,
            cpu_type=row.cpu_type,
            total_ram=row.total_ram,
            hostname=row.hostname,
            machine_type=row.machine_type,
            machine_arch=row.machine_arch,
            system_info=row.system_info,
            python_info=row.python_info,
        )
