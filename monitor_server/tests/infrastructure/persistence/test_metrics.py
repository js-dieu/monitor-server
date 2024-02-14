import typing as t
import uuid

import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.metrics import MetricRepository
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService
from monitor_server.tests.sdk.persistence.generators import MetricGenerator


@pytest.mark.int()
class TestMetricSQLRepository:
    def test_it_creates_a_new_metric_from_unknown_uid(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_sql_service.add_machine(a_machine)
        metrics_sql_service.add_session(a_session)
        metric_sql_repo.create(a_valid_metric)
        assert metric_sql_repo.get(a_valid_metric.uid.hex)

    def test_create_a_metric_raises_linked_entity_missing_if_session_is_unknown(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_sql_service.add_machine(a_machine)
        msg = f'Session {a_session.uid} cannot be found. Metric {a_valid_metric.uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metric_sql_repo.create(a_valid_metric)

    def test_create_a_metric_raises_linked_entity_missing_if_machine_is_unknown(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_sql_service.add_session(a_session)
        msg = (
            f'Execution Context {a_machine.uid} cannot be found.' f' Metric {a_valid_metric.uid.hex} cannot be inserted'
        )
        with pytest.raises(LinkedEntityMissing, match=msg):
            metric_sql_repo.create(a_valid_metric)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_sql_service.add_session(a_session)
        metrics_sql_service.add_machine(a_machine)
        metric_sql_repo.create(a_valid_metric)

        with pytest.raises(EntityAlreadyExists, match=a_valid_metric.uid.hex):
            metric_sql_repo.create(a_valid_metric)

    def test_it_returns_a_metric_when_querying_a_known_uid(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
        a_valid_metric: Metric,
    ):
        metrics_sql_service.add_session(a_session)
        metrics_sql_service.add_machine(a_machine)
        metric_sql_repo.create(a_valid_metric)
        assert metric_sql_repo.get(a_valid_metric.uid.hex) == a_valid_metric

    def test_it_raises_entity_not_found_when_querying_an_unknown_metric(self, metric_sql_repo: MetricRepository):
        an_id = uuid.uuid4()
        with pytest.raises(EntityNotFound, match=an_id.hex):
            metric_sql_repo.get(an_id.hex)

    def test_an_empty_repository_counts_0_elements(self, metric_sql_repo: MetricRepository):
        assert metric_sql_repo.count() == 0

    def test_a_repository_having_3_elements_counts_3(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_sql_service.add_session(a_session)
        metrics_sql_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(3)):
            metric_sql_repo.create(metric)
        assert metric_sql_repo.count() == 3

    def test_it_lists_all_metrics_when_no_page_info_is_given(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_sql_service.add_session(a_session)
        metrics_sql_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        metrics = []
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_sql_repo.create(metric)
            metrics.append(metric)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex), page_no=None, next_page=None
        )
        assert metric_sql_repo.list() == expected

    def test_it_lists_all_metrics_in_the_given_page(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_sql_service.add_session(a_session)
        metrics_sql_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        metrics = []
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_sql_repo.create(metric)
            metrics.append(metric)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex)[25:30], page_no=5, next_page=None
        )
        assert metric_sql_repo.list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_all_metrics_in_the_given_page_and_provide_next_page_info(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_sql_service.add_session(a_session)
        metrics_sql_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        metrics = []
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_sql_repo.create(metric)
            metrics.append(metric)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex)[15:20], page_no=3, next_page=4
        )
        assert metric_sql_repo.list(PageableStatement(page_no=3, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_sql_service.add_session(a_session)
        metrics_sql_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_sql_repo.create(metric)
        assert metric_sql_repo.list(PageableStatement(page_no=10, page_size=5)) == PaginatedResponse[t.List[Metric]](
            data=[], next_page=None, page_no=10
        )


class TestMetricInMemRepository:
    def test_it_creates_a_new_metric_from_unknown_uid(
        self, metric_in_mem_repo: MetricRepository, a_valid_metric: Metric
    ):
        assert metric_in_mem_repo.create(a_valid_metric)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, metric_in_mem_repo: MetricRepository, a_valid_metric: Metric
    ):
        metric_in_mem_repo.create(a_valid_metric)

        with pytest.raises(EntityAlreadyExists, match=f'Metric "{a_valid_metric.uid.hex} already exists'):
            metric_in_mem_repo.create(a_valid_metric)

    def test_it_returns_a_metric_when_querying_a_known_uid(
        self, metric_in_mem_repo: MetricRepository, a_valid_metric: Metric
    ):
        metric_in_mem_repo.create(a_valid_metric)
        assert metric_in_mem_repo.get(a_valid_metric.uid.hex) == a_valid_metric

    def test_it_raises_entity_not_found_when_querying_an_unknown_metric(
        self,
        metric_in_mem_repo: MetricRepository,
    ):
        an_id = uuid.uuid4().hex
        with pytest.raises(EntityNotFound, match=f'Metric "{an_id}" cannot be found'):
            metric_in_mem_repo.get(an_id)

    def test_an_empty_repository_counts_0_elements(
        self,
        metric_in_mem_repo: MetricRepository,
    ):
        assert metric_in_mem_repo.count() == 0

    def test_a_repository_having_3_elements_counts_3(self, metric_in_mem_repo: MetricRepository, a_start_time):
        metric_generator: MetricGenerator = MetricGenerator(
            a_start_time, lambda _: uuid.uuid4().hex, lambda _: uuid.uuid4().hex
        )
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(3)):
            metric_in_mem_repo.create(metric)
        assert metric_in_mem_repo.count() == 3

    def test_it_lists_all_metrics_when_no_page_info_is_given(
        self,
        metrics_in_mem_service: MonitoringMetricsService,
        metric_in_mem_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_in_mem_service.add_session(a_session)
        metrics_in_mem_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        metrics = []
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_in_mem_repo.create(metric)
            metrics.append(metric)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex), page_no=None, next_page=None
        )
        assert metric_in_mem_repo.list() == expected

    def test_it_lists_all_metrics_in_the_given_page(
        self,
        metrics_in_mem_service: MonitoringMetricsService,
        metric_in_mem_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_in_mem_service.add_session(a_session)
        metrics_in_mem_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        metrics = []
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_in_mem_repo.create(metric)
            metrics.append(metric)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex)[25:30], page_no=5, next_page=None
        )
        assert metric_in_mem_repo.list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_all_metrics_in_the_given_page_and_provide_next_page_info(
        self,
        metrics_in_mem_service: MonitoringMetricsService,
        metric_in_mem_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_in_mem_service.add_session(a_session)
        metrics_in_mem_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        metrics = []
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_in_mem_repo.create(metric)
            metrics.append(metric)
        expected = PaginatedResponse[t.List[Metric]](
            data=sorted(metrics, key=lambda m: m.uid.hex)[15:20], page_no=3, next_page=4
        )
        assert metric_in_mem_repo.list(PageableStatement(page_no=3, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        metrics_in_mem_service: MonitoringMetricsService,
        metric_in_mem_repo: MetricRepository,
        a_session: MonitorSession,
        a_machine: Machine,
    ):
        metrics_in_mem_service.add_session(a_session)
        metrics_in_mem_service.add_machine(a_machine)
        metric_generator: MetricGenerator = MetricGenerator(
            a_session.start_date, lambda _: a_session.uid, lambda _: a_machine.uid
        )
        for metric in (metric_generator(offset_from_start_date_sec=i) for i in range(30)):
            metric_in_mem_repo.create(metric)
        assert metric_in_mem_repo.list(PageableStatement(page_no=10, page_size=5)) == PaginatedResponse[t.List[Metric]](
            data=[], next_page=None, page_no=10
        )
