import typing as t
from datetime import datetime

from monitor_server.domain.models.abc import Attribute, Entity, Model


class MonitorSession(Entity):
    start_date: datetime
    scm_revision: str
    tags: t.Dict[str, t.Any]

    def __eq__(self, other: object) -> bool:
        if type(other) is MonitorSession:
            other_session = t.cast(MonitorSession, other)
            return (
                self.uid == other_session.uid
                and self.start_date == other_session.start_date
                and self.scm_revision == other_session.scm_revision
                and self.tags.get('description', '') == other_session.tags.get('description', '')
            )
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other


class NewSessionCreated(Model):
    uid: str | None = None


class SessionListing(Model):
    data: t.List[MonitorSession]
    next_page: int | None = Attribute(default=None)
