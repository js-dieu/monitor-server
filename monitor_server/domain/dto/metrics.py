import pathlib
import typing as t
from datetime import datetime

from monitor_server.domain.dto.abc import DTO, Attribute
from monitor_server.domain.entities.metrics import Metric


class CreateMetricRequest(DTO):
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


class NewMetricCreated(DTO):
    uid: str | None = Attribute(default=None)


class MetricsListing(DTO):
    data: t.List[Metric]
    next_page: int | None = Attribute(default=None)
