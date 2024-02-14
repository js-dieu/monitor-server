import pathlib
import typing as t

from monitor_server.domain.entities.abc import Entity
from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.entities.sessions import MonitorSession
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


class ORMMapper:
    @classmethod
    def orm_session_to_entity(cls, orm_session: ORMSession) -> MonitorSession:
        return MonitorSession(
            uid=orm_session.uid,
            start_date=orm_session.run_date,
            scm_revision=orm_session.scm_id,
            tags=orm_session.description,
        )

    @classmethod
    def orm_execution_context_to_entity(cls, orm_execution_context: ORMMachine) -> Machine:
        return Machine(
            uid=orm_execution_context.uid,
            cpu_frequency=orm_execution_context.cpu_frequency,
            cpu_vendor=orm_execution_context.cpu_vendor,
            cpu_count=orm_execution_context.cpu_count,
            cpu_type=orm_execution_context.cpu_type,
            total_ram=orm_execution_context.total_ram,
            hostname=orm_execution_context.hostname,
            machine_type=orm_execution_context.machine_type,
            machine_arch=orm_execution_context.machine_arch,
            system_info=orm_execution_context.system_info,
            python_info=orm_execution_context.python_info,
        )

    @classmethod
    def orm_test_metric_to_entity(cls, orm_metric: ORMMetric) -> Metric:
        return Metric(
            uid=orm_metric.uid,
            session_id=orm_metric.sid,
            node_id=orm_metric.xid,
            item_start_time=orm_metric.item_start_time,
            item_path=orm_metric.item_path,
            item=orm_metric.item,
            variant=orm_metric.variant,
            item_path_fs=pathlib.Path(orm_metric.item_fs_loc),
            item_type=orm_metric.kind,
            component=orm_metric.component,
            wall_time=orm_metric.wall_time,
            user_time=orm_metric.user_time,
            kernel_time=orm_metric.kernel_time,
            cpu_usage=orm_metric.cpu_usage,
            memory_usage=orm_metric.mem_usage,
        )
