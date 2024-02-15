import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.services import (
    MonitoringMetricsService,
)
from monitor_server.tests.sdk.persistence.generators import MetricGenerator


class TestMonitoringMetricsService:
    def test_create_the_same_metric_twice_raises_entity_already_exists(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_service.add_metrics([a_valid_metric], session=a_session, machine=a_machine)
        with pytest.raises(EntityAlreadyExists, match=f'Metric "{a_valid_metric.uid.hex}" already exists'):
            metrics_service.add_metric(a_valid_metric)

    def test_create_a_metric_raises_linked_entity_missing_if_session_is_unknown(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_service.add_machine(a_machine)
        msg = f'Session {a_session.uid} cannot be found. Metric {a_valid_metric.uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_service.add_metric(a_valid_metric)

    def test_it_raises_linked_entity_missing_when_creating_a_metric_on_an_unknown_machine(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_service.add_session(a_session)
        msg = (
            f'Execution Context {a_machine.uid} cannot be found.' f' Metric {a_valid_metric.uid.hex} cannot be inserted'
        )
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_service.add_metric(a_valid_metric)

    def test_it_can_create_a_metric_if_both_session_and_machine_are_known(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_service.add_session(a_session)
        metrics_service.add_machine(a_machine)
        assert metrics_service.add_metric(a_valid_metric)

    def test_creating_multiple_metrics_raises_linked_entity_missing_if_one_session_is_unknown(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        def get_session_id(step: int) -> str:
            if step == 10:
                return a_session.uid[::-1]
            return a_session.uid

        def get_machine_id(_: int) -> str:
            return a_machine.uid

        generator = MetricGenerator(a_session.start_date, get_session_id, get_machine_id)
        metrics = [generator() for _ in range(20)]

        msg = f'Session {metrics[9].session_id} cannot be found. Metric {metrics[9].uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_service.add_metrics(metrics, session=a_session, machine=a_machine)

    def test_creating_multiple_metrics_raises_linked_entity_missing_if_one_machine_is_unknown(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        def get_session_id(_: int) -> str:
            return a_session.uid

        def get_machine_id(step: int) -> str:
            if step == 10:
                return a_machine.uid[::-1]
            return a_machine.uid

        generator = MetricGenerator(a_session.start_date, get_session_id, get_machine_id)
        metrics = [generator() for _ in range(20)]

        msg = f'Execution Context {metrics[9].node_id} cannot be found. Metric {metrics[9].uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_service.add_metrics(metrics, session=a_session, machine=a_machine)

    def test_it_can_create_multiple_metrics_at_once(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        generator = MetricGenerator(a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid)
        metrics = [generator() for _ in range(20)]
        assert metrics_service.add_metrics(metrics, session=a_session, machine=a_machine) == 20

    def test_it_raises_entity_not_found_when_querying_unknown_metric(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_service.get_metric('abcd')

    def test_it_raises_entity_not_found_when_querying_unknown_session(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_service.get_session('abcd')

    def test_it_raises_entity_not_found_when_querying_unknown_machine(
        self,
        metrics_service: MonitoringMetricsService,
        a_valid_metric: Metric,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_service.get_machine('abcd')
