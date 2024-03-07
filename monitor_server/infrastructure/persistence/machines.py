import typing as t

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from monitor_server.domain.models.machines import Machine
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.orm.repositories import CRUDRepositoryABC, InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.models import ExecutionContext

ExecutionContextRepository = CRUDRepositoryABC[Machine, ExecutionContext]


class ExecutionContextSQLRepository(SQLRepository[Machine, ExecutionContext]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # def count(self) -> int:
    #     return super()._count()
    #
    # def truncate(self) -> None:
    #     return super()._truncate()

    def create(self, machine: Machine) -> Machine:
        stmt = insert(ExecutionContext).values(
            uid=machine.uid,
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
            raise EntityAlreadyExists(Machine, machine.uid.hex) from e
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return machine

    def update(self, machine: Machine) -> Machine:
        stmt = (
            update(self.model)
            .where(ExecutionContext.uid == machine.uid)
            .values(
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
            return self.mapper.cast_model(row[0], as_=Machine)
        raise EntityNotFound(Machine, uid)

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[Machine]]:
        q = self.session.query(self.model)
        if page_info:
            q = q.limit(page_info.page_size).offset(page_info.offset)
            count = self.count()
            rows = t.cast(t.Iterable[ExecutionContext], q.all())
            return page_info.build_response(
                [self.mapper.cast_model(row, as_=Machine) for row in rows or []], elements_count=count
            )

        rows = t.cast(t.Iterable[ExecutionContext], q.all())
        return PaginatedResponse(
            data=[self.mapper.cast_model(row, as_=Machine) for row in rows or []],
            page_no=None,
            next_page=None,
        )


class ExecutionContextInMemRepository(InMemoryRepository[Machine, ExecutionContext]):
    def __init__(self) -> None:
        super().__init__()

    def create(self, machine: Machine) -> Machine:
        if machine.uid.hex in self._data:
            raise EntityAlreadyExists(Machine, machine.uid.hex)
        self._data[machine.uid.hex] = t.cast(ExecutionContext, self.model).from_model(machine)
        return machine

    def update(self, machine: Machine) -> Machine:
        if machine.uid.hex not in self._data:
            raise EntityNotFound(Machine, machine.uid.hex)
        self._data[machine.uid.hex] = t.cast(ExecutionContext, self.model).from_model(machine)
        return machine

    def get(self, uid: str) -> Machine:
        row = self._data.get(uid)
        if not row:
            raise EntityNotFound(Machine, uid)
        return self.mapper.cast_model(row, as_=Machine)

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[Machine]]:
        if page_info is None:
            return PaginatedResponse(
                data=[
                    self.mapper.cast_model(machine, as_=Machine)
                    for machine in sorted(self._data.values(), key=lambda m: m.uid)
                ],
                page_no=None,
                next_page=None,
            )
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        element_ids = sorted(self._data.keys())[page]
        return page_info.build_response(
            data=[self.mapper.cast_model(self._data[element_id], as_=Machine) for element_id in element_ids],
            elements_count=self.count(),
        )

    # def count(self) -> int:
    #     return super()._count()
    #
    # def truncate(self) -> None:
    #     return super()._truncate()
