import datetime
import pathlib
import typing as t
import uuid

import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.persistence.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    LinkedEntityMissing,
)
from monitor_server.infrastructure.persistence.metrics import MetricInMemRepository, MetricSQLRepository
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService


@pytest.mark.int()
class TestMetricSQLRepository:
    def setup_method(self):
        self.session_time = datetime.datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=datetime.UTC)

        self.a_session = MonitorSession(
            uid='abcd',
            scm_revision='scm_revision',
            start_date=self.session_time,
            tags={'description': 'a description', 'extras': 'information'},
        )
        self.a_machine = Machine(
            uid='dcba',
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
        self.a_metric = Metric(
            uid=uuid.uuid4(),
            session_id=self.a_session.uid,
            node_id=self.a_machine.uid,
            item_start_time=self.session_time + datetime.timedelta(seconds=1),
            item_path='tests.this.item',
            item='item',
            variant='item',
            item_path_fs=pathlib.Path('tests/this.py'),
            item_type='function',
            component='component',
            wall_time=1.23,
            user_time=0.8,
            kernel_time=0.13,
            memory_usage=65,
            cpu_usage=123,
        )

    def test_it_creates_a_new_metric_from_unknown_uid(
        self, metrics_sql_service: MonitoringMetricsService, metric_sql_repo: MetricSQLRepository
    ):
        metrics_sql_service.add_machine(self.a_machine)
        metrics_sql_service.add_session(self.a_session)
        metric_sql_repo.create(self.a_metric)
        assert metric_sql_repo.get(self.a_metric.uid.hex)

    def test_create_a_metric_raises_linked_entity_missing_if_session_is_unknown(
        self, metrics_sql_service: MonitoringMetricsService, metric_sql_repo: MetricSQLRepository
    ):
        metrics_sql_service.add_machine(self.a_machine)
        msg = f'Session {self.a_session.uid} cannot be found. Metric {self.a_metric.uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metric_sql_repo.create(self.a_metric)

    def test_create_a_metric_raises_linked_entity_missing_if_machine_is_unknown(
        self, metrics_sql_service: MonitoringMetricsService, metric_sql_repo: MetricSQLRepository
    ):
        metrics_sql_service.add_session(self.a_session)
        msg = (
            f'Execution Context {self.a_machine.uid} cannot be found.'
            f' Metric {self.a_metric.uid.hex} cannot be inserted'
        )
        with pytest.raises(LinkedEntityMissing, match=msg):
            metric_sql_repo.create(self.a_metric)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, metrics_sql_service: MonitoringMetricsService, metric_sql_repo: MetricSQLRepository
    ):
        metrics_sql_service.add_session(self.a_session)
        metrics_sql_service.add_machine(self.a_machine)
        metric_sql_repo.create(self.a_metric)

        with pytest.raises(EntityAlreadyExists, match=self.a_metric.uid.hex):
            metric_sql_repo.create(self.a_metric)

    def test_it_returns_a_metric_when_querying_a_known_uid(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricSQLRepository,
    ):
        metrics_sql_service.add_session(self.a_session)
        metrics_sql_service.add_machine(self.a_machine)
        metric_sql_repo.create(self.a_metric)
        assert metric_sql_repo.get(self.a_metric.uid.hex) == self.a_metric

    def test_it_raises_entity_not_found_when_querying_an_unknown_metric(self, metric_sql_repo: MetricSQLRepository):
        an_id = uuid.uuid4()
        with pytest.raises(EntityNotFound, match=an_id.hex):
            metric_sql_repo.get(an_id.hex)

    def test_an_empty_repository_counts_0_elements(self, metric_sql_repo: MetricSQLRepository):
        assert metric_sql_repo.count() == 0

    def test_a_repository_having_3_elements_counts_3(
        self,
        metrics_sql_service: MonitoringMetricsService,
        metric_sql_repo: MetricSQLRepository,
    ):
        metrics_sql_service.add_session(self.a_session)
        metrics_sql_service.add_machine(self.a_machine)
        for i in range(3):
            metric_data = self.a_metric.as_dict()
            metric_data['uid'] = uuid.uuid4()
            metric_data['variant'] = f'item[{i + 1}]'
            metric_data['item_start_time'] = self.session_time + datetime.timedelta(seconds=i)
            a_metric = t.cast(Metric, Metric.from_dict(metric_data))
            metric_sql_repo.create(a_metric)
        assert metric_sql_repo.count() == 3


class TestMetricInMemRepository:
    def setup_method(self):
        self.session_time = datetime.datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=datetime.UTC)

        self.a_session = MonitorSession(
            uid='abcd',
            scm_revision='scm_revision',
            start_date=self.session_time,
            tags={'description': 'a description', 'extras': 'information'},
        )
        self.a_machine = Machine(
            uid='dcba',
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
        self.a_metric = Metric(
            uid=uuid.uuid4(),
            session_id=self.a_session.uid,
            node_id=self.a_machine.uid,
            item_start_time=self.session_time + datetime.timedelta(seconds=1),
            item_path='tests.this.item',
            item='item',
            variant='item',
            item_path_fs=pathlib.Path('tests/this.py'),
            item_type='function',
            component='component',
            wall_time=1.23,
            user_time=0.8,
            kernel_time=0.13,
            memory_usage=65,
            cpu_usage=123,
        )

    def test_it_creates_a_new_metric_from_unknown_uid(
        self,
        metric_in_mem_repo: MetricInMemRepository,
    ):
        assert metric_in_mem_repo.create(self.a_metric)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self,
        metric_in_mem_repo: MetricInMemRepository,
    ):
        metric_in_mem_repo.create(self.a_metric)

        with pytest.raises(EntityAlreadyExists, match=self.a_metric.uid.hex):
            metric_in_mem_repo.create(self.a_metric)

    def test_it_returns_a_metric_when_querying_a_known_uid(
        self,
        metric_in_mem_repo: MetricInMemRepository,
    ):
        metric_in_mem_repo.create(self.a_metric)
        assert metric_in_mem_repo.get(self.a_metric.uid.hex) == self.a_metric

    def test_it_raises_entity_not_found_when_querying_an_unknown_metric(
        self,
        metric_in_mem_repo: MetricInMemRepository,
    ):
        an_id = uuid.uuid4()
        with pytest.raises(EntityNotFound, match=an_id.hex):
            metric_in_mem_repo.get(an_id.hex)

    def test_an_empty_repository_counts_0_elements(
        self,
        metric_in_mem_repo: MetricInMemRepository,
    ):
        assert metric_in_mem_repo.count() == 0

    def test_a_repository_having_3_elements_counts_3(
        self,
        metric_in_mem_repo: MetricInMemRepository,
    ):
        for i in range(3):
            metric_data = self.a_metric.as_dict()
            metric_data['uid'] = uuid.uuid4()
            metric_data['variant'] = f'item[{i + 1}]'
            metric_data['item_start_time'] = self.session_time + datetime.timedelta(seconds=i)
            a_metric = t.cast(Metric, Metric.from_dict(metric_data))
            metric_in_mem_repo.create(a_metric)
        assert metric_in_mem_repo.count() == 3
