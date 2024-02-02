import datetime
import pathlib
import typing as t
import uuid

import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.metrics import (
    MetricInMemRepository,
)


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
        self,
        metrics_service,
    ):
        metrics_service.session.create(self.a_session)
        metrics_service.execution_contexts.create(self.a_machine)
        assert metrics_service.metric.create(self.a_metric)

    def test_it_raises_missing_entity_when_creating_a_metric_on_an_unknown_session(self):
        pass

    def test_it_raises_missing_entity_when_creating_a_metric_on_an_unknown_machine(self):
        pass

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self,
        metrics_service,
    ):
        metrics_service.session.create(self.a_session)
        metrics_service.execution_contexts.create(self.a_machine)
        metrics_service.metric.create(self.a_metric)

        with pytest.raises(EntityAlreadyExists, match=self.a_metric.uid.hex):
            metrics_service.metric.create(self.a_metric)

    def test_it_returns_a_metric_when_querying_a_known_uid(
        self,
        metrics_service,
    ):
        metrics_service.session.create(self.a_session)
        metrics_service.execution_contexts.create(self.a_machine)
        metrics_service.metric.create(self.a_metric)
        assert metrics_service.metric.get(self.a_metric.uid) == self.a_metric

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self,
        metrics_service,
    ):
        an_id = uuid.uuid4()
        with pytest.raises(EntityNotFound, match=an_id.hex):
            metrics_service.metric.get(an_id)

    def test_an_empty_repository_counts_0_elements(
        self,
        metrics_service,
    ):
        assert metrics_service.metric.count() == 0

    def test_a_repository_having_3_elements_counts_3(
        self,
        metrics_service,
    ):
        metrics_service.session.create(self.a_session)
        metrics_service.execution_contexts.create(self.a_machine)
        for i in range(3):
            metric_data = self.a_metric.as_dict()
            metric_data['uid'] = uuid.uuid4()
            metric_data['variant'] = f'item[{i + 1}]'
            metric_data['item_start_time'] = self.session_time + datetime.timedelta(seconds=i)
            a_metric = Metric.from_dict(metric_data)
            metrics_service.metric.create(a_metric)
        assert metrics_service.metric.count() == 3


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

    def test_it_raises_missing_entity_when_creating_a_metric_on_an_unknown_session(self):
        pass

    def test_it_raises_missing_entity_when_creating_a_metric_on_an_unknown_machine(self):
        pass

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
        assert metric_in_mem_repo.get(self.a_metric.uid) == self.a_metric

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self,
        metric_in_mem_repo: MetricInMemRepository,
    ):
        an_id = uuid.uuid4()
        with pytest.raises(EntityNotFound, match=an_id.hex):
            metric_in_mem_repo.get(an_id)

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