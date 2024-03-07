import typing as t
from datetime import datetime

from monitor_server.domain.models.abc import Attribute, Entity, PageableRequest
from monitor_server.domain.models.metrics import Metric


class ValidationSuiteFilter(PageableRequest):
    session_id: str


class ValidationSuite(Entity):
    scm_revision: str
    tags: t.Dict[str, t.Any]
    start_date: datetime
    metrics: t.List[Metric]
    next_page: int | None = Attribute(default=None)

    @classmethod
    def entity_name(cls) -> str:
        return 'ValidationSuite'
