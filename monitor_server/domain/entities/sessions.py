import datetime
import hashlib
import typing as t
from functools import cached_property

from monitor_server.domain.entities.abc import Entity


class MonitorSession(Entity):
    uid: str
    start_date: datetime.datetime
    scm_revision: str
    tags: t.Dict[str, t.Any]

    @cached_property
    def footprint(self) -> str:
        if self.uid:
            return self.uid
        hr = hashlib.md5()
        hr.update(self.start_date.isoformat().encode())
        hr.update(self.scm_revision.encode())
        hr.update(self.tags.get('description', '').encode())
        return hr.hexdigest()

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
