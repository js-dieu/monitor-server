import abc
import typing as t

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import insert, select, update

from monitor_server.domain.entities.abc import Entity
from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.pageable import PageableStatement
from monitor_server.infrastructure.orm.repositories import InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.mapper import ORMMapper
from monitor_server.infrastructure.persistence.models import TestMetric


class MetricRepository:
    @abc.abstractmethod
    def create(self, item: Metric) -> Metric:
        """Persist a new session"""

    @abc.abstractmethod
    def update(self, machine: Metric) -> Metric:
        """Update an existing session"""

    @abc.abstractmethod
    def get(self, uid: str) -> Metric:
        """Get a session given an uid"""

    @abc.abstractmethod
    def list(self, page_info: PageableStatement | None = None) -> t.List[Metric]:
        """List all metrics ids"""

    @abc.abstractmethod
    def count(self) -> int:
        """Count the number of items in this repository"""


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
            x_cls: t.Type[ORMError]
            msg: str
            etype: t.Type[Entity]
            elinked: str
            if e.orig.args[0] == 1452 and 'Session' in e.orig.args[1]:  # type: ignore[union-attr]
                x_cls = LinkedEntityMissing
                msg = f'Session {item.session_id} cannot be found.' f' Metric {item.uid.hex} cannot be inserted'
                etype, elinked = MonitorSession, item.session_id
            elif e.orig.args[0] == 1452 and 'Session' not in e.orig.args[1]:  # type: ignore[union-attr]
                x_cls = LinkedEntityMissing
                msg = f'Execution Context {item.node_id} cannot be found.' f' Metric {item.uid.hex} cannot be inserted'
                etype, elinked = Machine, item.node_id
            else:
                x_cls = EntityAlreadyExists
                msg = f'Metric "{item.uid.hex}" already exists'
                elinked, etype = item.uid.hex, Metric
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

    def count(self) -> int:
        return super()._count()

    def get(self, uid: str) -> Metric:
        stmt = select(TestMetric).where(TestMetric.uid == uid)
        row = self.session.execute(stmt).fetchone()
        if row is not None:
            return ORMMapper().orm_test_metric_to_entity(row[0])
        raise EntityNotFound(f'Metric "{uid}" cannot be found', Metric, uid)

    def list(self, page_info: PageableStatement | None = None) -> t.List[Metric]:
        q = self.session.query(self.model)
        if page_info:
            q = q.offset(page_info.offset).limit(page_info.page_size)
        rows: t.List[TestMetric] = t.cast(t.List[TestMetric], q.all())
        mapper = ORMMapper()
        return [mapper.orm_test_metric_to_entity(row) for row in rows or []]


class MetricInMemRepository(MetricRepository, InMemoryRepository[TestMetric]):
    def get(self, uid: str) -> Metric:
        row = self._data.get(uid)
        if row is None:
            raise EntityNotFound(f'Metric "{uid}" cannot be found', Metric, uid)

        return ORMMapper().orm_test_metric_to_entity(row)

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

    def list(self, page_info: PageableStatement | None = None) -> t.List[Metric]:
        mapper = ORMMapper()
        if page_info is None:
            return [
                mapper.orm_test_metric_to_entity(metric)
                for metric in sorted(self._data.values(), key=lambda m: m.uid.hex)
            ]
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        element_ids = sorted(self._data.keys())[page]
        return [mapper.orm_test_metric_to_entity(self._data[element_id]) for element_id in element_ids]

    def count(self) -> int:
        return super()._count()
