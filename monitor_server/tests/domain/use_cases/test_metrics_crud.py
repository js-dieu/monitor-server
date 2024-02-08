import pathlib
from datetime import UTC, datetime, timedelta

import pytest

from monitor_server.domain.dto.metrics import CreateMetricRequest
from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.domain.use_cases.exceptions import InvalidMetric
from monitor_server.domain.use_cases.metrics.crud import AddMetric
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService


@pytest.mark.int()
class TestAddMetricDB:
    def setup_method(self):
        self._start_date = datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC)
        self.a_test_session = MonitorSession(
            uid='abcd',
            scm_revision='scm_revision',
            start_date=self._start_date,
            tags={'description': 'a description', 'extras': 'information'},
        )
        self.a_machine = Machine(
            uid='abcd',
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

    def test_it_generates_a_new_id_when_adding_a_new_metric(self, metrics_sql_service: MonitoringMetricsService):
        metrics_sql_service.add_session(self.a_test_session)
        metrics_sql_service.add_machine(self.a_machine)
        use_case = AddMetric(metrics_sql_service)
        assert use_case.execute(
            CreateMetricRequest(
                session_id=self.a_test_session.uid,
                node_id=self.a_machine.uid,
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
        self, metrics_sql_service: MonitoringMetricsService
    ):
        metrics_sql_service.add_session(self.a_test_session)
        metrics_sql_service.add_machine(self.a_machine)
        use_case = AddMetric(metrics_sql_service)
        msg = 'Session unknown cannot be found. Metric [a-z0-9]* cannot be inserted'
        with pytest.raises(InvalidMetric, match=msg):
            use_case.execute(
                CreateMetricRequest(
                    session_id='unknown',
                    node_id=self.a_machine.uid,
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
