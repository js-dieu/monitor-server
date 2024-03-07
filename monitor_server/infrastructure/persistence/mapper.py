import pathlib
import typing as t

from monitor_server.domain.models.abc import Entity
from monitor_server.domain.models.machines import Machine
from monitor_server.domain.models.metrics import Metric
from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.persistence.models import (
    ExecutionContext as ORMMachine,
)
from monitor_server.infrastructure.persistence.models import (
    Session as ORMSession,
)
from monitor_server.infrastructure.persistence.models import (
    TestMetric as ORMMetric,
)

AnyModel = t.TypeVar('AnyModel', bound=ORMModel)
AnyEntity = t.TypeVar('AnyEntity', bound=Entity)


def session_model_to_domain(value: ORMSession) -> MonitorSession:
    return MonitorSession(
        uid=value.uid,
        start_date=value.run_date,
        scm_revision=value.scm_id,
        tags=value.description,
    )


def session_domain_to_model(value: MonitorSession) -> ORMSession:
    return ORMSession(
        uid=value.uid,
        run_date=value.start_date,
        scm_id=value.scm_revision,
        description=value.tags,
    )


def machine_model_to_domain(value: ORMMachine) -> Machine:
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


def machine_domain_to_model(value: Machine) -> ORMMachine:
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


def metric_model_to_domain(value: ORMMetric) -> Metric:
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


def metric_domain_to_model(value: ORMMetric) -> Metric:
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


class ORMMapper:
    def __init__(self) -> None:
        self.domain_map: t.Dict[str, t.Callable[[t.Any], t.Any]] = {
            ORMMetric.__name__: metric_domain_to_model,
            ORMMachine.__name__: machine_domain_to_model,
            ORMSession.__name__: session_domain_to_model,
        }
        self.orm_map: t.Dict[str, t.Callable[[t.Any], t.Any]] = {
            Metric.__name__: metric_model_to_domain,
            Machine.__name__: machine_model_to_domain,
            MonitorSession.__name__: session_model_to_domain,
        }

    def cast_entity(self, value: Entity, as_: t.Type[ORMModel]) -> ORMModel:
        return self.domain_map[as_.__name__](value)

    def cast_model(self, value: ORMModel, as_: t.Type[AnyEntity]) -> AnyEntity:
        return self.orm_map[as_.__name__](value)
