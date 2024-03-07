import abc
import typing as t

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import insert, select, update

from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric
from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.orm.repositories import CRUDRepositoryBase, InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.models import TestMetric


class MetricRepository(CRUDRepositoryBase[Metric, TestMetric]):
    # @abc.abstractmethod
    # def create(self, item: Metric) -> Metric:
    #     """Persist a new session"""
    #
    # @abc.abstractmethod
    # def update(self, machine: Metric) -> Metric:
    #     """Update an existing session"""
    #
    # @abc.abstractmethod
    # def get(self, uid: str) -> Metric:
    #     """Get a session given an uid"""
    #
    @abc.abstractmethod
    def get_all_of(
        self, session_id: str | None = None, node_id: str | None = None, page_info: PageableStatement | None = None
    ) -> PaginatedResponse[t.List[Metric]]:
        """Get all metrics of the given session_id and/or node_id"""

    # @abc.abstractmethod
    # def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[Metric]]:
    #     """List all metrics ids"""
    #
    # @abc.abstractmethod
    # def count(self) -> int:
    #     """Count the number of items in this repository"""
    #
    # @abc.abstractmethod
    # def truncate(self) -> None:
    #     """Remove all entries from this repository"""


class MetricSQLRepository(MetricRepository, SQLRepository[Metric, TestMetric]):
    def create(self, item: Metric) -> Metric:
        stmt = insert(TestMetric).values(
            uid=item.uid.hex,
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
            if e.orig.args[0] == 1452 and 'Session' in e.orig.args[1]:  # type: ignore[union-attr]
                raise LinkedEntityMissing(MonitorSession, item.session_id, Metric, item.uid.hex) from e
            if e.orig.args[0] == 1452 and 'Session' not in e.orig.args[1]:  # type: ignore[union-attr]
                raise LinkedEntityMissing(Machine, item.node_id, Metric, item.uid.hex) from e
            raise EntityAlreadyExists(Metric, item.uid.hex) from e
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

    # def count(self) -> int:
    #     return super()._count()
    #
    # def truncate(self) -> None:
    #     return super()._truncate()

    def get(self, uid: str) -> Metric:
        stmt = select(TestMetric).where(TestMetric.uid == uid)
        row = self.session.execute(stmt).fetchone()
        if row is not None:
            return self.mapper.cast_model(row[0], as_=Metric)
        raise EntityNotFound(Metric, uid)

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[Metric]]:
        q = self.session.query(self.model)
        if page_info:
            q = q.limit(page_info.page_size).offset(page_info.offset)
            count = self.count()
            rows = t.cast(t.Iterable[TestMetric], q.all())
            return page_info.build_response(
                [self.mapper.cast_model(row, as_=Metric) for row in rows or []], elements_count=count
            )

        rows = t.cast(t.Iterable[TestMetric], q.all())
        return PaginatedResponse(
            data=[self.mapper.cast_model(row, as_=Metric) for row in rows or []],
            page_no=None,
            next_page=None,
        )

    def get_all_of(
        self, session_id: str | None = None, node_id: str | None = None, page_info: PageableStatement | None = None
    ) -> PaginatedResponse[t.List[Metric]]:
        q = self.session.query(self.model)
        if session_id:
            q = q.where(TestMetric.sid == session_id)
        if node_id:
            q = q.where(TestMetric.xid == node_id)
        if page_info:
            q = q.limit(page_info.page_size).offset(page_info.offset)
            count = self.count()
            rows = t.cast(t.Iterable[TestMetric], q.all())
            return page_info.build_response(
                [self.mapper.cast_model(row, as_=Metric) for row in rows or []], elements_count=count
            )

        rows = t.cast(t.Iterable[TestMetric], q.all())
        return PaginatedResponse(
            data=[self.mapper.cast_model(row, as_=Metric) for row in rows or []], page_no=None, next_page=None
        )


class MetricInMemRepository(MetricRepository, InMemoryRepository[Metric, TestMetric]):
    def get(self, uid: str) -> Metric:
        row = self._data.get(uid)
        if row is None:
            raise EntityNotFound(Metric, uid)

        return self.mapper.cast_model(row, as_=Metric)

    def create(self, item: Metric) -> Metric:
        if item.uid.hex in self._data:
            raise EntityAlreadyExists(Metric, item.uid.hex)
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
            raise EntityNotFound(Metric, item.uid.hex)
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

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[Metric]]:
        if page_info is None:
            return PaginatedResponse(
                data=[
                    self.mapper.cast_model(metric, as_=Metric)
                    for metric in sorted(self._data.values(), key=lambda m: m.uid)
                ],
                page_no=None,
                next_page=None,
            )
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        element_ids = sorted(self._data.keys())[page]
        return page_info.build_response(
            data=[self.mapper.cast_model(self._data[element_id], as_=Metric) for element_id in element_ids],
            elements_count=self.count(),
        )

    # def count(self) -> int:
    #     return super()._count()
    #
    # def truncate(self) -> None:
    #     return super()._truncate()

    def get_all_of(
        self, session_id: str | None = None, node_id: str | None = None, page_info: PageableStatement | None = None
    ) -> PaginatedResponse[t.List[Metric]]:
        def filter_metric(metric: TestMetric) -> bool:
            session_is_ok = (session_id is None) or (session_id is not None and metric.sid == session_id)
            node_is_ok = (node_id is None) or (node_id is not None and metric.xid == node_id)
            return session_is_ok and node_is_ok

        matching_metrics = sorted(filter(filter_metric, self._data.values()), key=lambda m: m.uid.hex)

        if page_info is None:
            return PaginatedResponse(
                data=[self.mapper.cast_model(metric, as_=Metric) for metric in matching_metrics],
                page_no=None,
                next_page=None,
            )
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        count = len(matching_metrics)
        return page_info.build_response(
            data=[self.mapper.cast_model(metric, as_=Metric) for metric in matching_metrics[page]],
            elements_count=count,
        )
