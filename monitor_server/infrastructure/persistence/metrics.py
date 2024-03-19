import abc
import typing as t

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import insert

from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric
from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.orm.presenter import presenter
from monitor_server.infrastructure.orm.repositories import CRUDRepositoryABC, InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.models import TestMetric


class MetricRepository(CRUDRepositoryABC[Metric, TestMetric]):
    @abc.abstractmethod
    def get_all_of(
        self, session_id: str | None = None, node_id: str | None = None, page_info: PageableStatement | None = None
    ) -> PaginatedResponse[t.List[Metric]]:
        """Get all metrics of the given session_id and/or node_id"""


class MetricSQLRepository(MetricRepository, SQLRepository[Metric, TestMetric]):
    def create(self, item: Metric) -> Metric:
        stmt = insert(TestMetric).values(**(presenter.to_orm(item, as_=TestMetric).as_dict()))
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
                [presenter.from_orm(row, as_=Metric) for row in rows or []], elements_count=count
            )

        rows = t.cast(t.Iterable[TestMetric], q.all())
        return PaginatedResponse(
            data=[presenter.from_orm(row, as_=Metric) for row in rows or []], page_no=None, next_page=None
        )


class MetricInMemRepository(MetricRepository, InMemoryRepository[Metric, TestMetric]):
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
                data=[presenter.from_orm(metric, as_=Metric) for metric in matching_metrics],
                page_no=None,
                next_page=None,
            )
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        count = len(matching_metrics)
        return page_info.build_response(
            data=[presenter.from_orm(metric, as_=Metric) for metric in matching_metrics[page]],
            elements_count=count,
        )
