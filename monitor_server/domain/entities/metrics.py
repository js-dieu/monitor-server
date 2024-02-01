import pathlib
import typing as t
from datetime import datetime
from uuid import UUID, uuid4

from monitor_server.domain.entities.abc import Attribute, Entity


class Metric(Entity):
    uid: UUID = Attribute(default_factory=uuid4)
    session_id: str
    node_id: str
    item_start_time: datetime
    item_path: str
    item: str
    variant: str
    item_path_fs: pathlib.Path
    item_type: str
    component: str
    wall_time: float
    user_time: float
    kernel_time: float
    memory_usage: float
    cpu_usage: float

    def __eq__(self, other: object) -> bool:
        if type(other) is Metric:
            other_metric = t.cast(Metric, other)
            return (
                self.uid == other_metric.uid
                and self.session_id == other_metric.session_id
                and self.node_id == other_metric.node_id
                and self.item_path == other_metric.item_path
                and self.item == other_metric.item
                and self.variant == other_metric.variant
                and self.component == other_metric.component
                and self.item_start_time == other_metric.item_start_time
                and self.item_path_fs == other_metric.item_path_fs
                and self.item_type == other_metric.item_type
                and abs(self.wall_time - other_metric.wall_time) < 10e-6
                and abs(self.user_time - other_metric.user_time) < 10e-6
                and abs(self.kernel_time - other_metric.kernel_time) < 10e-6
                and abs(self.memory_usage - other_metric.memory_usage) < 10e-6
                and abs(self.cpu_usage - other_metric.cpu_usage) < 10e-6
            )

        return False
