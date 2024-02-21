import pathlib
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from monitor_server.domain.models.abc import PageableRequest
from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric, MetricsListing
from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.domain.use_cases.exceptions import InvalidMetric
from monitor_server.domain.use_cases.metrics.crud import AddMetric, ListMetrics
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService
from monitor_server.tests.sdk.persistence.generators import MachineGenerator, MetricGenerator, MonitorSessionGenerator


class TestAddMetric:
    def setup_method(self):
        self._start_date = datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC)
        self.a_test_session = MonitorSession(
            uid=uuid.uuid4(),
            scm_revision='scm_revision',
            start_date=self._start_date,
            tags={'description': 'a description', 'extras': 'information'},
        )
        self.a_machine = Machine(
            uid=uuid.uuid4(),
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            cpu_type='cpu_type',
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )

    def test_it_generates_a_new_id_when_adding_a_new_metric(self, metrics_service: MonitoringMetricsService):
        metrics_service.add_session(self.a_test_session)
        metrics_service.add_machine(self.a_machine)
        use_case = AddMetric(metrics_service)
        assert use_case.execute(
            Metric(
                session_id=self.a_test_session.uid.hex,
                node_id=self.a_machine.uid.hex,
                item_start_time=self._start_date + timedelta(seconds=1),
                item_path='item.path',
                item='some_test',
                variant='some_test[variant]',
                item_path_fs=pathlib.Path('item') / 'path',
                item_type='function',
                component='component',
                wall_time=1.00,
                user_time=0.99,
                kernel_time=0.88,
                memory_usage=100,
                cpu_usage=1.2,
            )
        ).uid

    def test_it_raises_invalid_metric_when_inserting_twice_the_same_metric(
        self, metrics_service: MonitoringMetricsService
    ):
        metrics_service.add_session(self.a_test_session)
        metrics_service.add_machine(self.a_machine)
        use_case = AddMetric(metrics_service)
        unknown_session_id = uuid.uuid4().hex
        msg = f'Session {unknown_session_id} cannot be found. Metric [a-z0-9]* cannot be inserted'
        with pytest.raises(InvalidMetric, match=msg):
            use_case.execute(
                Metric(
                    session_id=unknown_session_id,
                    node_id=self.a_machine.uid.hex,
                    item_start_time=self._start_date + timedelta(seconds=1),
                    item_path='item.path',
                    item='some_test',
                    variant='some_test[variant]',
                    item_path_fs=pathlib.Path('item') / 'path',
                    item_type='function',
                    component='component',
                    wall_time=1.00,
                    user_time=0.99,
                    kernel_time=0.88,
                    memory_usage=100,
                    cpu_usage=1.2,
                )
            )


class TestListMetrics:
    def setup_method(self) -> None:
        self.session = MonitorSessionGenerator()()
        self.machine = MachineGenerator()()
        metrics_generator: MetricGenerator = MetricGenerator(
            start_date=self.session.start_date,
            machine_uid_cb=lambda _: self.machine.uid.hex,
            session_uid_cb=lambda _: self.session.uid.hex,
        )
        self.metrics = []
        for metric in (metrics_generator() for _ in range(30)):
            self.metrics.append(metric)
        self.metrics = sorted(self.metrics, key=lambda m: m.uid.hex)

    def test_it_returns_all_elements_when_no_page_info(self, metrics_service: MonitoringMetricsService):
        metrics_service.add_metrics(self.metrics, self.session, self.machine)
        use_case = ListMetrics(metrics_service.metric_repository())
        result = use_case.execute(PageableRequest())
        assert result == MetricsListing(data=self.metrics, next_page=None)

    def test_it_returns_no_elements_when_out_of_bounds(self, metrics_service: MonitoringMetricsService):
        metrics_service.add_metrics(self.metrics, self.session, self.machine)
        use_case = ListMetrics(metrics_service.metric_repository())
        result = use_case.execute(PageableRequest(page_no=10, page_size=5))
        assert result == MetricsListing(data=[], next_page=None)

    def test_it_returns_elements_with_next_page_when_listing_is_not_complete(
        self, metrics_service: MonitoringMetricsService
    ):
        metrics_service.add_metrics(self.metrics, self.session, self.machine)
        use_case = ListMetrics(metrics_service.metric_repository())
        result = use_case.execute(PageableRequest(page_no=1, page_size=5))
        assert result == MetricsListing(data=self.metrics[5:10], next_page=2)
