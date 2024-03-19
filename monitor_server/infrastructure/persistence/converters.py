import pathlib

from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric
from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.infrastructure.orm.presenter import Converter, presenter
from monitor_server.infrastructure.persistence.models import (
    ExecutionContext as ORMMachine,
)
from monitor_server.infrastructure.persistence.models import (
    Session as ORMSession,
)
from monitor_server.infrastructure.persistence.models import (
    TestMetric as ORMMetric,
)


@presenter.register()
class ORMSessionToDomain(Converter[ORMSession, MonitorSession]):
    def __call__(self, value: ORMSession) -> MonitorSession:
        return MonitorSession(
            uid=value.uid, start_date=value.run_date, scm_revision=value.scm_id, tags=value.description
        )


@presenter.register()
class SessionToORMSession(Converter[MonitorSession, ORMSession]):
    def __call__(self, value: MonitorSession) -> ORMSession:
        return ORMSession(uid=value.uid, run_date=value.start_date, scm_id=value.scm_revision, description=value.tags)


@presenter.register()
class MetricToORMMetric(Converter[Metric, ORMMetric]):
    def __call__(self, value: Metric) -> ORMMetric:
        return ORMMetric(
            uid=value.uid,
            sid=value.session_id,
            xid=value.node_id,
            item_start_time=value.item_start_time,
            item_path=value.item_path,
            item=value.item,
            variant=value.variant,
            item_fs_loc=value.item_path_fs.as_posix(),
            kind=value.item_type,
            component=value.component,
            wall_time=value.wall_time,
            user_time=value.user_time,
            kernel_time=value.kernel_time,
            cpu_usage=value.cpu_usage,
            mem_usage=value.memory_usage,
        )


@presenter.register()
class ORMMetricToMetric(Converter[ORMMetric, Metric]):
    def __call__(self, value: ORMMetric) -> Metric:
        return Metric(
            uid=value.uid,
            session_id=value.sid,
            node_id=value.xid,
            item_start_time=value.item_start_time,
            item_path=value.item_path,
            item=value.item,
            variant=value.variant,
            item_path_fs=pathlib.Path(value.item_fs_loc),
            item_type=value.kind,
            component=value.component,
            wall_time=value.wall_time,
            user_time=value.user_time,
            kernel_time=value.kernel_time,
            cpu_usage=value.cpu_usage,
            memory_usage=value.mem_usage,
        )


@presenter.register()
class ORMMachineToMachine(Converter[ORMMachine, Machine]):
    def __call__(self, value: ORMMachine) -> Machine:
        return Machine(
            uid=value.uid,
            cpu_frequency=value.cpu_frequency,
            cpu_vendor=value.cpu_vendor,
            cpu_count=value.cpu_count,
            cpu_type=value.cpu_type,
            total_ram=value.total_ram,
            hostname=value.hostname,
            machine_type=value.machine_type,
            machine_arch=value.machine_arch,
            system_info=value.system_info,
            python_info=value.python_info,
        )


@presenter.register()
class MachineToORMMachine(Converter[Machine, ORMMachine]):
    def __call__(self, value: Machine) -> ORMMachine:
        return ORMMachine(
            uid=value.uid,
            cpu_frequency=value.cpu_frequency,
            cpu_vendor=value.cpu_vendor,
            cpu_count=value.cpu_count,
            cpu_type=value.cpu_type,
            total_ram=value.total_ram,
            hostname=value.hostname,
            machine_type=value.machine_type,
            machine_arch=value.machine_arch,
            system_info=value.system_info,
            python_info=value.python_info,
        )
