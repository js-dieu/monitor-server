import abc
import pathlib
import typing as t
from datetime import datetime
from uuid import UUID

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import insert, select, update

from monitor_server.domain.entities.abc import Entity
from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.repositories import InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.machines import ExecutionContext
from monitor_server.infrastructure.persistence.sessions import Session


class TestMetric(ORMModel):
    uid: Mapped[UUID] = mapped_column(nullable=False, primary_key=True)
    sid: Mapped[str] = mapped_column(String(64), ForeignKey(Session.uid), nullable=False)
    xid: Mapped[str] = mapped_column(String(64), ForeignKey(ExecutionContext.uid), nullable=False)
    item_start_time: Mapped[datetime] = mapped_column(nullable=False)
    item_path: Mapped[str] = mapped_column(String(4096), nullable=False)
    item: Mapped[str] = mapped_column(String(2048), nullable=False)
    variant: Mapped[str] = mapped_column(String(2048), nullable=False)
    item_fs_loc: Mapped[str] = mapped_column(String(2048), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    component: Mapped[str] = mapped_column(String(512), nullable=False)
    wall_time: Mapped[float] = mapped_column(Float(), nullable=False)
    user_time: Mapped[float] = mapped_column(Float(), nullable=False)
    kernel_time: Mapped[float] = mapped_column(Float(), nullable=False)
    cpu_usage: Mapped[float] = mapped_column(Float(), nullable=False)
    mem_usage: Mapped[float] = mapped_column(Float(), nullable=False)
    session = relationship(Session)
    execution_context = relationship(ExecutionContext)


class MetricRepository:
    @classmethod
    def build_entity_from(cls, model: TestMetric) -> Metric:
        return Metric(
            uid=model.uid,
            session_id=model.sid,
            node_id=model.xid,
            item_start_time=model.item_start_time,
            item_path=model.item_path,
            item=model.item,
            variant=model.variant,
            item_path_fs=pathlib.Path(model.item_fs_loc),
            item_type=model.kind,
            component=model.component,
            wall_time=model.wall_time,
            user_time=model.user_time,
            kernel_time=model.kernel_time,
            cpu_usage=model.cpu_usage,
            memory_usage=model.mem_usage,
        )

    @abc.abstractmethod
    def create(self, item: Metric) -> Metric:
        """Persist a new session"""

    @abc.abstractmethod
    def update(self, machine: Metric) -> Metric:
        """Update an existing session"""

    @abc.abstractmethod
    def get(self, uid: str) -> Metric:
        """Get a session given an uid"""


class MetricSQLRepository(MetricRepository, SQLRepository[TestMetric]):
    def create(self, item: Metric) -> Metric:
        stmt = insert(TestMetric).values(
            uid=item.uid,
            sid=item.session_id,
            xid=item.node_id,
            item_start_time=item.item_start_time,
            item_path=item.item_path,
            item=item.item,
            variant=item.variant,
            item_fs_loc=item.item_path_fs.as_posix(),
            kind=item.item_type,
            component=item.component,
            wall_time=item.wall_time,
            user_time=item.user_time,
            kernel_time=item.kernel_time,
            cpu_usage=item.cpu_usage,
            mem_usage=item.memory_usage,
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError as e:
            x_cls: t.Type[ORMError] = EntityAlreadyExists
            msg = item.uid.hex
            etype: t.Type[Entity] = Metric
            elinked = ''
            if e.orig.args[0] == 1452 and 'Session' in e.orig.args[1]:  # type: ignore[union-attr]
                x_cls = LinkedEntityMissing
                msg = f'Session {item.session_id} cannot be found.' f' Metric {item.uid.hex} cannot be inserted'
                etype, elinked = MonitorSession, item.session_id
            elif e.orig.args[0] == 1452 and 'Session' not in e.orig.args[1]:  # type: ignore[union-attr]
                x_cls = LinkedEntityMissing
                msg = f'Execution Context {item.node_id} cannot be found.' f' Metric {item.uid.hex} cannot be inserted'
                etype, elinked = Machine, item.node_id
            raise x_cls(msg, etype, elinked) from e
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return item

    def update(self, item: Metric) -> Metric:
        stmt = (
            update(TestMetric)
            .where(TestMetric.uid == item.uid)
            .values(
                item_start_time=item.item_start_time,
                item_path=item.item_path,
                item=item.item,
                variant=item.variant,
                item_fs_loc=item.item_path_fs.as_posix(),
                kind=item.item_type,
                component=item.component,
                wall_time=item.wall_time,
                user_time=item.user_time,
                kernel_time=item.kernel_time,
                cpu_usage=item.cpu_usage,
                mem_usage=item.memory_usage,
            )
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return item

    def get(self, uid: str) -> Metric:
        stmt = select(TestMetric).where(TestMetric.uid == uid)
        row = self.session.execute(stmt).fetchone()
        if row is not None:
            return self.build_entity_from(row[0])
        raise EntityNotFound(f'Metric "{uid}" cannot be found', Metric, uid)


class MetricInMemRepository(MetricRepository, InMemoryRepository[TestMetric]):
    def get(self, uid: str) -> Metric:
        row = self._data.get(uid)
        if row is None:
            raise EntityNotFound(f'Metric "{uid}" cannot be found', Metric, uid)

        return self.build_entity_from(row)

    def create(self, item: Metric) -> Metric:
        if item.uid.hex in self._data:
            raise EntityAlreadyExists(f'Metric "{item.uid.hex} already exists', Metric, item.uid.hex)
        self._data[item.uid.hex] = TestMetric(
            uid=item.uid,
            sid=item.session_id,
            xid=item.node_id,
            item_start_time=item.item_start_time,
            item_path=item.item_path,
            item=item.item,
            variant=item.variant,
            item_fs_loc=item.item_path_fs.as_posix(),
            kind=item.item_type,
            component=item.component,
            wall_time=item.wall_time,
            user_time=item.user_time,
            kernel_time=item.kernel_time,
            cpu_usage=item.cpu_usage,
            mem_usage=item.memory_usage,
        )
        return item

    def update(self, item: Metric) -> Metric:
        if item.uid.hex not in self._data:
            raise EntityNotFound(f'Metric "{item.uid.hex}" cannot be found', Metric, item.uid.hex)
        self._data[item.uid.hex] = TestMetric(
            uid=item.uid,
            sid=item.session_id,
            xid=item.node_id,
            item_start_time=item.item_start_time,
            item_path=item.item_path,
            item=item.item,
            variant=item.variant,
            item_fs_loc=item.item_path_fs.as_posix(),
            kind=item.item_type,
            component=item.component,
            wall_time=item.wall_time,
            user_time=item.user_time,
            kernel_time=item.kernel_time,
            cpu_usage=item.cpu_usage,
            mem_usage=item.memory_usage,
        )
        return item
