import typing as t
import uuid

import pytest

from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric
from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.metrics import MetricRepository
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService
from monitor_server.tests.sdk.persistence.generators import MetricGenerator


class TestMetricRepository:
    def test_it_creates_a_new_metric_from_unknown_uid(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_service.add_machine(a_machine)
        metrics_service.add_session(a_session)
        metric_repository = metrics_service.metric_repository()
        metric_repository.create(a_valid_metric)
        assert metric_repository.get(a_valid_metric.uid.hex)

    def test_create_a_metric_raises_linked_entity_missing_if_session_is_unknown(
        self,
        metrics_sql_service: MonitoringMetricsService,  # in memory does not support the use case
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_sql_service.add_machine(a_machine)
        msg = f'Session {a_session.uid.hex} cannot be found. Metric {a_valid_metric.uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_sql_service.metric_repository().create(a_valid_metric)

    def test_create_a_metric_raises_linked_entity_missing_if_machine_is_unknown(
        self,
        metrics_sql_service: MonitoringMetricsService,  # in memory does not support the use case
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_sql_service.add_session(a_session)
        msg = (
            f'Execution Context {a_machine.uid.hex} cannot be found.'
            f' Metric {a_valid_metric.uid.hex} cannot be inserted'
        )
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_sql_service.metric_repository().create(a_valid_metric)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_service.add_session(a_session)
        metrics_service.add_machine(a_machine)
        metrics_service.metric_repository().create(a_valid_metric)

        with pytest.raises(EntityAlreadyExists, match=a_valid_metric.uid.hex):
            metrics_service.metric_repository().create(a_valid_metric)

    def test_it_returns_a_metric_when_querying_a_known_uid(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_service.add_session(a_session)
        metrics_service.add_machine(a_machine)
        metrics_service.metric_repository().create(a_valid_metric)
        assert metrics_service.metric_repository().get(a_valid_metric.uid.hex) == a_valid_metric

    def test_it_raises_entity_not_found_when_querying_an_unknown_metric(self, metrics_repository: MetricRepository):
        an_id = uuid.uuid4()
        with pytest.raises(EntityNotFound, match=an_id.hex):
            metrics_repository.get(an_id.hex)

    def test_an_empty_repository_counts_0_elements(self, metrics_repository: MetricRepository):
        assert metrics_repository.count() == 0

    def test_a_repository_having_3_elements_counts_3(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_service.add_session(a_session)
        metrics_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid.hex, lambda _: a_machine.uid.hex
        )
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(3)):
            metrics_service.metric_repository().create(metric)
        assert metrics_service.metric_repository().count() == 3

    def test_it_lists_all_metrics_when_no_page_info_is_given(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid.hex, lambda _: a_machine.uid.hex
        )
        metrics = [metric_generator(offset_from_start_date_sec=i) for i in range(30)]
        metrics_service.add_metrics(metrics, a_session, a_machine)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex), page_no=None, next_page=None
        )
        assert metrics_service.metric_repository().list() == expected

    def test_it_lists_all_metrics_in_the_given_page(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid.hex, lambda _: a_machine.uid.hex
        )
        metrics = [metric_generator(offset_from_start_date_sec=i) for i in range(30)]
        metrics_service.add_metrics(metrics, a_session, a_machine)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex)[25:30], page_no=5, next_page=None
        )
        assert metrics_service.metric_repository().list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_all_metrics_in_the_given_page_and_provide_next_page_info(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid.hex, lambda _: a_machine.uid.hex
        )
        metrics = [metric_generator(offset_from_start_date_sec=i) for i in range(30)]
        metrics_service.add_metrics(metrics, a_session, a_machine)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex)[15:20], page_no=3, next_page=4
        )
        assert metrics_service.metric_repository().list(PageableStatement(page_no=3, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        metrics_service: MonitoringMetricsService,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid.hex, lambda _: a_machine.uid.hex
        )
        metrics_service.add_metrics(
            [metric_generator(offset_from_start_date_sec=i) for i in range(30)], a_session, a_machine
        )
        expected = PaginatedResponse[t.List[Metric]](data=[], next_page=None, page_no=10)
        assert metrics_service.metric_repository().list(PageableStatement(page_no=10, page_size=5)) == expected
