import abc
import typing as t
from contextlib import suppress

from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.orm.engine import ORMEngine
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.machines import (
    ExecutionContextInMemRepository,
    ExecutionContextSQLRepository,
)
from monitor_server.infrastructure.persistence.metrics import (
    MetricInMemRepository,
    MetricSQLRepository,
)
from monitor_server.infrastructure.persistence.sessions import (
    SessionInMemRepository,
    SessionSQLRepository,
)


class MonitoringMetricsService(abc.ABC):
    @abc.abstractmethod
    def add_metrics(
        self, metrics: t.List[Metric], session: MonitorSession | None = None, machine: Machine | None = None
    ) -> int:
        """Add a list of metrics and associate them to the given session and machine"""

    @abc.abstractmethod
    def add_metric(self, metric: Metric) -> Metric:
        """Add a new metric."""

    @abc.abstractmethod
    def add_machine(self, machine: Machine) -> Machine:
        """Add a new execution context (aka machine)"""

    @abc.abstractmethod
    def add_session(self, session: MonitorSession) -> MonitorSession:
        """Add a new monitoring session"""

    @abc.abstractmethod
    def get_metric(self, uid: str) -> Metric:
        """Fetch a metric by its uid"""

    @abc.abstractmethod
    def get_session(self, uid: str) -> MonitorSession:
        """Fetch a session given its uid"""

    @abc.abstractmethod
    def get_machine(self, uid: str) -> Machine:
        """Fetch a machine given its uid"""

    @abc.abstractmethod
    def truncate_all(self) -> None:
        """Remove all data"""


class MonitoringMetricsSQLService(MonitoringMetricsService):
    def __init__(self, orm_engine: ORMEngine) -> None:
        super().__init__()
        self._session = orm_engine.session
        self._metric_repo = MetricSQLRepository(self._session)
        self._session_repo = SessionSQLRepository(self._session)
        self._node_repo = ExecutionContextSQLRepository(self._session)

    def add_machine(self, machine: Machine) -> Machine:
        return self._node_repo.create(machine)

    def add_metric(self, metric: Metric) -> Metric:
        return self._metric_repo.create(metric)

    def add_session(self, session: MonitorSession) -> MonitorSession:
        return self._session_repo.create(session)

    def add_metrics(
        self, metrics: t.List[Metric], session: MonitorSession | None = None, machine: Machine | None = None
    ) -> int:
        if session:
            with suppress(EntityAlreadyExists):
                self._session_repo.create(session)
        if machine:
            with suppress(EntityAlreadyExists):
                self._node_repo.create(machine)
        count = 0
        for metric in metrics:
            self._metric_repo.create(metric)
            count += 1
        return count

    def get_metric(self, uid: str) -> Metric:
        return self._metric_repo.get(uid)

    def get_session(self, uid: str) -> MonitorSession:
        return self._session_repo.get(uid)

    def get_machine(self, uid: str) -> Machine:
        return self._node_repo.get(uid)

    def truncate_all(self) -> None:
        self._node_repo.truncate()
        self._session_repo.truncate()
        self._metric_repo.truncate()


class MonitoringMetricsInMemService(MonitoringMetricsService):
    def __init__(self) -> None:
        super().__init__()
        self._metric_repo = MetricInMemRepository()
        self._session_repo = SessionInMemRepository()
        self._node_repo = ExecutionContextInMemRepository()

    def add_machine(self, machine: Machine) -> Machine:
        return self._node_repo.create(machine)

    def add_metric(self, metric: Metric) -> Metric:
        try:
            self._node_repo.get(metric.node_id)
            self._session_repo.get(metric.session_id)
        except EntityNotFound as e:
            if str(e) == metric.node_id:
                raise LinkedEntityMissing(  # noqa: B904
                    f'Execution Context {metric.node_id} cannot be found. '
                    f'Metric {metric.uid.hex} cannot be inserted'
                )
            raise LinkedEntityMissing(  # noqa: B904
                f'Session {metric.session_id} cannot be found. Metric {metric.uid.hex} cannot be inserted'
            )
        return self._metric_repo.create(metric)

    def add_session(self, session: MonitorSession) -> MonitorSession:
        return self._session_repo.create(session)

    def add_metrics(
        self, metrics: t.List[Metric], session: MonitorSession | None = None, machine: Machine | None = None
    ) -> int:
        if session:
            self._session_repo.create(session)
        if machine:
            self._node_repo.create(machine)
        count = 0
        for metric in metrics:
            try:
                self._session_repo.get(metric.session_id)
                self._node_repo.get(metric.node_id)
                self._metric_repo.create(metric)
                count += 1
            except EntityNotFound as e:
                if str(e) == metric.node_id:
                    raise LinkedEntityMissing(  # noqa: B904
                        f'Execution Context {metric.node_id} cannot be found.'
                        f' Metric {metric.uid.hex} cannot be inserted'
                    )
                raise LinkedEntityMissing(  # noqa: B904
                    f'Session {metric.session_id} cannot be found.' f' Metric {metric.uid.hex} cannot be inserted'
                )
        return count

    def get_metric(self, uid: str) -> Metric:
        return self._metric_repo.get(uid)

    def get_session(self, uid: str) -> MonitorSession:
        return self._session_repo.get(uid)

    def get_machine(self, uid: str) -> Machine:
        return self._node_repo.get(uid)

    def truncate_all(self) -> None:
        self._node_repo.truncate()
        self._session_repo.truncate()
        self._metric_repo.truncate()