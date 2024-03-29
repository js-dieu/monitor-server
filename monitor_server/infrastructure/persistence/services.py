import abc
import typing as t
from contextlib import suppress

from monitor_server.domain.models.aggregates import ValidationSuite
from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric
from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.infrastructure.orm.engine import ORMEngine
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.machines import (
    ExecutionContextInMemRepository,
    ExecutionContextRepository,
    ExecutionContextSQLRepository,
)
from monitor_server.infrastructure.persistence.metrics import (
    MetricInMemRepository,
    MetricRepository,
    MetricSQLRepository,
)
from monitor_server.infrastructure.persistence.sessions import (
    SessionInMemRepository,
    SessionRepository,
    SessionSQLRepository,
)


class MonitoringMetricsService(abc.ABC):
    @abc.abstractmethod
    def metric_repository(self) -> MetricRepository:
        """Direct access to the metric repository"""

    @abc.abstractmethod
    def session_repository(self) -> SessionRepository:
        """Direct access to the metric repository"""

    @abc.abstractmethod
    def machine_repository(self) -> ExecutionContextRepository:
        """Direct access to the metric repository"""

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

    @abc.abstractmethod
    def count_sessions(self) -> int:
        """Count the number of sessions"""

    @abc.abstractmethod
    def count_metrics(self) -> int:
        """Count the number of metrics"""

    @abc.abstractmethod
    def count_machines(self) -> int:
        """count the number of machines/execution contexts"""

    @abc.abstractmethod
    def get_test_suite(self, uid: str) -> ValidationSuite:
        """Get a session and all affiliated tests"""


class BaseMonitoringMetricsService(MonitoringMetricsService, abc.ABC):
    def __init__(
        self,
        metric_repository: MetricRepository,
        session_repository: SessionRepository,
        execution_context_repository: ExecutionContextRepository,
    ) -> None:
        super().__init__()
        self._metric_repo = metric_repository
        self._session_repo = session_repository
        self._node_repo = execution_context_repository

    def count_sessions(self) -> int:
        return self._session_repo.count()

    def count_metrics(self) -> int:
        return self._metric_repo.count()

    def count_machines(self) -> int:
        return self._node_repo.count()

    def metric_repository(self) -> MetricRepository:
        return self._metric_repo

    def session_repository(self) -> SessionRepository:
        return self._session_repo

    def machine_repository(self) -> ExecutionContextRepository:
        return self._node_repo

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

    def get_test_suite(self, uid: str) -> ValidationSuite:
        session = self._session_repo.get(uid)
        metrics = self._metric_repo.get_all_of(session_id=uid)
        return ValidationSuite(
            uid=session.uid,
            scm_revision=session.scm_revision,
            tags=session.tags,
            start_date=session.start_date,
            metrics=metrics.data,
        )


class MonitoringMetricsSQLService(BaseMonitoringMetricsService):
    def __init__(self, orm_engine: ORMEngine) -> None:
        self._session = orm_engine.session
        super().__init__(
            MetricSQLRepository(self._session),
            SessionSQLRepository(self._session),
            ExecutionContextSQLRepository(self._session),
        )

    def truncate_all(self) -> None:
        self.machine_repository().truncate()
        self.session_repository().truncate()
        self.metric_repository().truncate()


class MonitoringMetricsInMemService(BaseMonitoringMetricsService):
    def __init__(self) -> None:
        super().__init__(MetricInMemRepository(), SessionInMemRepository(), ExecutionContextInMemRepository())

    def add_metric(self, metric: Metric) -> Metric:
        try:
            self.machine_repository().get(metric.node_id)
            self.session_repository().get(metric.session_id)
        except EntityNotFound as e:
            if e.entity_typename == Machine.entity_name():
                raise LinkedEntityMissing(  # noqa: B904
                    Machine, e.entity_id, Metric, metric.uid.hex
                )
            raise LinkedEntityMissing(  # noqa: B904
                MonitorSession, e.entity_id, Metric, metric.uid.hex
            )
        return self.metric_repository().create(metric)

    def add_metrics(
        self, metrics: t.List[Metric], session: MonitorSession | None = None, machine: Machine | None = None
    ) -> int:
        if session:
            with suppress(EntityAlreadyExists):
                self.session_repository().create(session)
        if machine:
            with suppress(EntityAlreadyExists):
                self.machine_repository().create(machine)
        count = 0
        for metric in metrics:
            try:
                self.session_repository().get(metric.session_id)
                self.machine_repository().get(metric.node_id)
                self.metric_repository().create(metric)
                count += 1
            except EntityNotFound as e:
                if e.entity_typename == Machine.entity_name():
                    raise LinkedEntityMissing(  # noqa: B904
                        Machine, e.entity_id, Metric, metric.uid.hex
                    )
                raise LinkedEntityMissing(  # noqa: B904
                    MonitorSession, e.entity_id, Metric, metric.uid.hex
                )
        return count

    def truncate_all(self) -> None:
        self.machine_repository().truncate()
        self.session_repository().truncate()
        self.metric_repository().truncate()
