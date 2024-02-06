import itertools as it
import pathlib
import typing as t
import uuid
from datetime import UTC, datetime, timedelta

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


def metric_generator(start_time: datetime, session_id: t.Callable[[int], str], machine_id: t.Callable[[int], str]):
    def _generator() -> t.Iterator[Metric]:
        counter = it.count(1)
        while True:
            step = next(counter)
            yield Metric(
                uid=uuid.uuid4(),
                session_id=session_id(step),
                node_id=machine_id(step),
                item_start_time=start_time + timedelta(seconds=step),
                item_path='tests.this.item',
                item='item',
                variant=f'item[{step}]',
                item_path_fs=pathlib.Path('tests/this.py'),
                item_type='function',
                component='component',
                wall_time=1.23,
                user_time=0.8,
                kernel_time=0.13,
                memory_usage=65,
                cpu_usage=123,
            )

    return _generator()


@pytest.mark.int()
class TestMonitoringMetricsSQLService:
    def setup_method(self):
        self.a_machine = Machine(
            uid='efgh',
            cpu_frequency=3500,
            cpu_vendor='Apple',
            cpu_count=12,
            cpu_type='ARM',
            total_ram=64 * 1024,
            hostname='hostname',
            machine_type='arm64',
            machine_arch='darwin',
            system_info='system info',
            python_info='python info',
        )
        self.session_time = datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC)
        self.a_session = MonitorSession(
            uid='abcd',
            scm_revision='scm_revision',
            start_date=self.session_time,
            tags={'description': 'a description', 'extras': 'information'},
        )
        self.a_metric = Metric(
            uid=uuid.uuid4(),
            session_id=self.a_session.uid,
            node_id=self.a_machine.uid,
            item_start_time=self.session_time + timedelta(seconds=1),
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

    def test_create_the_same_metric_twice_raises_entity_already_exists(
        self, metrics_sql_service: MonitoringMetricsService
    ):
        metrics_sql_service.add_metrics([self.a_metric], session=self.a_session, machine=self.a_machine)
        with pytest.raises(EntityAlreadyExists, match=self.a_metric.uid.hex):
            metrics_sql_service.add_metric(self.a_metric)

    def test_create_a_metric_raises_linked_entity_missing_if_session_is_unknown(
        self, metrics_sql_service: MonitoringMetricsService
    ):
        metrics_sql_service.add_machine(self.a_machine)
        msg = f'Session {self.a_session.uid} cannot be found. Metric {self.a_metric.uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_sql_service.add_metric(self.a_metric)

    def test_it_raises_linked_entity_missing_when_creating_a_metric_on_an_unknown_machine(
        self,
        metrics_sql_service: MonitoringMetricsService,
    ):
        metrics_sql_service.add_session(self.a_session)
        msg = (
            f'Execution Context {self.a_machine.uid} cannot be found.'
            f' Metric {self.a_metric.uid.hex} cannot be inserted'
        )
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_sql_service.add_metric(self.a_metric)

    def test_it_can_create_a_metric_if_both_session_and_machine_are_known(
        self, metrics_sql_service: MonitoringMetricsService
    ):
        metrics_sql_service.add_session(self.a_session)
        metrics_sql_service.add_machine(self.a_machine)
        assert metrics_sql_service.add_metric(self.a_metric)

    def test_creating_multiple_metrics_raises_linked_entity_missing_if_one_session_is_unknown(
        self, metrics_sql_service: MonitoringMetricsService
    ):
        def get_session_id(step: int) -> str:
            if step == 10:
                return self.a_session.uid[::-1]
            return self.a_session.uid

        def get_machine_id(_: int) -> str:
            return self.a_machine.uid

        generator = metric_generator(self.session_time, get_session_id, get_machine_id)
        metrics = [next(generator) for _ in range(20)]

        msg = f'Session {metrics[9].session_id} cannot be found. Metric {metrics[9].uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_sql_service.add_metrics(metrics, session=self.a_session, machine=self.a_machine)

    def test_creating_multiple_metrics_raises_linked_entity_missing_if_one_machine_is_unknown(
        self,
        metrics_sql_service: MonitoringMetricsService,
    ):
        def get_session_id(_: int) -> str:
            return self.a_session.uid

        def get_machine_id(step: int) -> str:
            if step == 10:
                return self.a_machine.uid[::-1]
            return self.a_machine.uid

        generator = metric_generator(self.session_time, get_session_id, get_machine_id)
        metrics = [next(generator) for _ in range(20)]

        msg = f'Execution Context {metrics[9].node_id} cannot be found. Metric {metrics[9].uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_sql_service.add_metrics(metrics, session=self.a_session, machine=self.a_machine)

    def test_it_can_create_multiple_metrics_at_once(self, metrics_sql_service: MonitoringMetricsService):
        generator = metric_generator(self.session_time, lambda _: self.a_session.uid, lambda _: self.a_machine.uid)
        metrics = [next(generator) for _ in range(20)]
        assert metrics_sql_service.add_metrics(metrics, session=self.a_session, machine=self.a_machine) == 20

    def test_it_raises_entity_not_found_when_querying_unknown_metric(
        self, metrics_sql_service: MonitoringMetricsService
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_sql_service.get_metric('abcd')

    def test_it_raises_entity_not_found_when_querying_unknown_session(
        self, metrics_sql_service: MonitoringMetricsService
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_sql_service.get_session('abcd')

    def test_it_raises_entity_not_found_when_querying_unknown_machine(
        self, metrics_sql_service: MonitoringMetricsService
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_sql_service.get_machine('abcd')


class TestMonitoringMetricsInMemService:
    def setup_method(self):
        self.a_machine = Machine(
            uid='efgh',
            cpu_frequency=3500,
            cpu_vendor='Apple',
            cpu_count=12,
            cpu_type='ARM',
            total_ram=64 * 1024,
            hostname='hostname',
            machine_type='arm64',
            machine_arch='darwin',
            system_info='system info',
            python_info='python info',
        )
        self.session_time = datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC)
        self.a_session = MonitorSession(
            uid='abcd',
            scm_revision='scm_revision',
            start_date=self.session_time,
            tags={'description': 'a description', 'extras': 'information'},
        )
        self.a_metric = Metric(
            uid=uuid.uuid4(),
            session_id=self.a_session.uid,
            node_id=self.a_machine.uid,
            item_start_time=self.session_time + timedelta(seconds=1),
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

    def test_create_the_same_metric_twice_raises_entity_already_exists(
        self, metrics_in_mem_service: MonitoringMetricsService
    ):
        metrics_in_mem_service.add_metrics([self.a_metric], session=self.a_session, machine=self.a_machine)
        with pytest.raises(EntityAlreadyExists, match=self.a_metric.uid.hex):
            metrics_in_mem_service.add_metric(self.a_metric)

    def test_create_a_metric_raises_linked_entity_missing_if_session_is_unknown(
        self, metrics_in_mem_service: MonitoringMetricsService
    ):
        metrics_in_mem_service.add_machine(self.a_machine)
        msg = f'Session {self.a_session.uid} cannot be found. Metric {self.a_metric.uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_in_mem_service.add_metric(self.a_metric)

    def test_it_raises_linked_entity_missing_when_creating_a_metric_on_an_unknown_machine(
        self,
        metrics_in_mem_service: MonitoringMetricsService,
    ):
        metrics_in_mem_service.add_session(self.a_session)
        msg = (
            f'Execution Context {self.a_machine.uid} cannot be found.'
            f' Metric {self.a_metric.uid.hex} cannot be inserted'
        )
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_in_mem_service.add_metric(self.a_metric)

    def test_it_can_create_a_metric_if_both_session_and_machine_are_known(
        self, metrics_in_mem_service: MonitoringMetricsService
    ):
        metrics_in_mem_service.add_session(self.a_session)
        metrics_in_mem_service.add_machine(self.a_machine)
        assert metrics_in_mem_service.add_metric(self.a_metric)

    def test_creating_multiple_metrics_raises_linked_entity_missing_if_one_session_is_unknown(
        self, metrics_in_mem_service: MonitoringMetricsService
    ):
        def get_session_id(step: int) -> str:
            if step == 10:
                return self.a_session.uid[::-1]
            return self.a_session.uid

        def get_machine_id(_: int) -> str:
            return self.a_machine.uid

        generator = metric_generator(self.session_time, get_session_id, get_machine_id)
        metrics = [next(generator) for _ in range(20)]

        msg = f'Session {metrics[9].session_id} cannot be found. Metric {metrics[9].uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_in_mem_service.add_metrics(metrics, session=self.a_session, machine=self.a_machine)

    def test_creating_multiple_metrics_raises_linked_entity_missing_if_one_machine_is_unknown(
        self,
        metrics_in_mem_service: MonitoringMetricsService,
    ):
        def get_session_id(_: int) -> str:
            return self.a_session.uid

        def get_machine_id(step: int) -> str:
            if step == 10:
                return self.a_machine.uid[::-1]
            return self.a_machine.uid

        generator = metric_generator(self.session_time, get_session_id, get_machine_id)
        metrics = [next(generator) for _ in range(20)]

        msg = f'Execution Context {metrics[9].node_id} cannot be found. Metric {metrics[9].uid.hex} cannot be inserted'
        with pytest.raises(LinkedEntityMissing, match=msg):
            metrics_in_mem_service.add_metrics(metrics, session=self.a_session, machine=self.a_machine)

    def test_it_can_create_multiple_metrics_at_once(self, metrics_in_mem_service: MonitoringMetricsService):
        generator = metric_generator(self.session_time, lambda _: self.a_session.uid, lambda _: self.a_machine.uid)
        metrics = [next(generator) for _ in range(20)]
        assert metrics_in_mem_service.add_metrics(metrics, session=self.a_session, machine=self.a_machine) == 20

    def test_it_raises_entity_not_found_when_querying_unknown_metric(
        self, metrics_in_mem_service: MonitoringMetricsService
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_in_mem_service.get_metric('abcd')

    def test_it_raises_entity_not_found_when_querying_unknown_session(
        self, metrics_in_mem_service: MonitoringMetricsService
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_in_mem_service.get_session('abcd')

    def test_it_raises_entity_not_found_when_querying_unknown_machine(
        self, metrics_in_mem_service: MonitoringMetricsService
    ):
        with pytest.raises(EntityNotFound, match='abcd'):
            metrics_in_mem_service.get_machine('abcd')
