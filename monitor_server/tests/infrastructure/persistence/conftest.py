import pathlib
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric
from monitor_server.domain.models.sessions import MonitorSession


@pytest.fixture()
def a_machine() -> Machine:
    return Machine(
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


@pytest.fixture()
def a_start_time() -> datetime:
    return datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC)


@pytest.fixture()
def a_session(a_start_time) -> MonitorSession:
    return MonitorSession(
        uid=uuid.uuid4(),
        scm_revision='scm_revision',
        start_date=a_start_time,
        tags={'description': 'a description', 'extras': 'information'},
    )


@pytest.fixture()
def a_valid_metric(a_machine, a_session) -> Metric:
    return Metric(
        uid=uuid.uuid4(),
        session_id=a_session.uid.hex,
        node_id=a_machine.uid.hex,
        item_start_time=a_session.start_date + timedelta(seconds=1),
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
