import datetime
import itertools as it
import pathlib
import typing as t
from uuid import UUID, uuid4

from monitor_server.domain.entities.machines import Machine
from monitor_server.infrastructure.persistence.metrics import Metric

EntityIdCallBack = t.Callable[[int], str]


class MetricGenerator:
    def __init__(
        self, start_date: datetime.datetime, session_uid_cb: EntityIdCallBack, machine_uid_cb: EntityIdCallBack
    ) -> None:
        self._start_date = start_date
        self._session_cb = session_uid_cb
        self._machine_cb = machine_uid_cb
        self._counter = it.count(1)

    def __call__(
        self,
        offset_from_start_date_sec: int | None = None,
        uid: t.Callable[[], UUID] = uuid4,
        item_path: str | None = None,
        item: str | None = None,
        variant: str | None = None,
        item_path_fs: pathlib.Path | None = None,
        item_type: str | None = None,
        component: str | None = None,
        wall_time: float | None = None,
        user_time: float | None = None,
        kernel_time: float | None = None,
        memory_usage: float | None = None,
        cpu_usage: float | None = None,
    ) -> Metric:
        step = next(self._counter)
        return Metric(
            uid=uid(),
            session_id=self._session_cb(step),
            node_id=self._machine_cb(step),
            item_start_time=self._start_date + datetime.timedelta(seconds=offset_from_start_date_sec or step),
            item_path=item_path or 'tests.this.item',
            item=item or 'item',
            variant=variant or f'item[{step}]',
            item_path_fs=item_path_fs or pathlib.Path('tests/this.py'),
            item_type=item_type or 'function',
            component=component or 'component',
            wall_time=wall_time or 1.23,
            user_time=user_time or 0.8,
            kernel_time=kernel_time or 0.13,
            memory_usage=memory_usage or 65,
            cpu_usage=cpu_usage or 123,
        )


class MachineGenerator:
    def __init__(self) -> None:
        self._counter = it.count(1)

    def __call__(
        self,
        uid: t.Callable[[], UUID] = uuid4,
        cpu_frequency: int | None = None,
        cpu_vendor: str | None = None,
        cpu_count: int | None = None,
        cpu_type: str | None = None,
        total_ram: int | None = None,
        hostname: str | None = None,
        machine_type: str | None = None,
        machine_arch: str | None = None,
        system_info: str | None = None,
        python_info: str | None = None,
    ) -> Machine:
        step = next(self._counter)
        return Machine(
            uid=uid().hex,
            cpu_frequency=cpu_frequency or 1024,
            cpu_vendor=cpu_vendor or 'cpu_vendor',
            cpu_count=cpu_count or 32,
            cpu_type=cpu_type or 'cpu_type',
            total_ram=total_ram or 2048,
            hostname=hostname or f'hostname_{step}',
            machine_type=machine_type or 'type',
            machine_arch=machine_arch or 'arch',
            system_info=system_info or 'system info',
            python_info=python_info or 'python info',
        )
