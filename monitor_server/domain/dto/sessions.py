import typing as t
from datetime import datetime

from monitor_server.domain.dto.abc import DTO, Attribute
from monitor_server.domain.entities.sessions import MonitorSession


class CreateSession(DTO):
    uid: str
    start_date: datetime
    scm_revision: str
    tags: t.Dict[str, t.Any]


class NewSessionCreated(DTO):
    uid: str | None = None


class SessionListing(DTO):
    data: t.List[MonitorSession]
    next_page: int | None = Attribute(default=None)
