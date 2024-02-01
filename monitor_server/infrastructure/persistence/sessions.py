import abc
import typing as t
from datetime import datetime

# import sqlalchemy.dialects.mysql as mysql
from sqlalchemy import JSON, String
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import insert, select, update

from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.repositories import InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound


class Session(ORMModel):
    uid: Mapped[str] = mapped_column(String(64), nullable=False, primary_key=True)
    run_date: Mapped[datetime] = mapped_column(nullable=False)
    description: Mapped[t.Dict[str, t.Any]] = mapped_column(MutableDict.as_mutable(JSON()), nullable=False)
    scm_id: Mapped[str] = mapped_column(String(128), nullable=False)


class SessionRepository:
    @classmethod
    def build_entity_from(cls, model: Session) -> MonitorSession:
        return MonitorSession(
            uid=model.uid, start_date=model.run_date, scm_revision=model.scm_id, tags=model.description
        )

    @abc.abstractmethod
    def create(self, item: MonitorSession) -> MonitorSession:
        """Persist a new session"""

    @abc.abstractmethod
    def update(self, machine: MonitorSession) -> MonitorSession:
        """Update an existing session"""

    @abc.abstractmethod
    def get(self, uid: str) -> MonitorSession:
        """Get a session given an uid"""


class SessionSQLRepository(SessionRepository, SQLRepository[Session]):
    def create(self, item: MonitorSession) -> MonitorSession:
        stmt = insert(Session).values(
            uid=item.uid, description=item.tags, run_date=item.start_date, scm_id=item.scm_revision
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError as e:
            raise EntityAlreadyExists(item.uid) from e
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return item

    def update(self, item: MonitorSession) -> MonitorSession:
        stmt = (
            update(Session)
            .where(Session.uid == item.uid)
            .values(uid=item.uid, description=item.tags, run_date=item.start_date, scm_id=item.scm_revision)
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return item

    def get(self, uid: str) -> MonitorSession:
        stmt = select(Session).where(Session.uid == uid)
        row = self.session.execute(stmt).fetchone()
        if row is not None:
            return self.build_entity_from(row[0])
        raise EntityNotFound(uid)


class SessionInMemRepository(SessionRepository, InMemoryRepository[Session]):
    def get(self, uid: str) -> MonitorSession:
        row = self._data.get(uid)
        if row is None:
            raise EntityNotFound(uid)

        return MonitorSession(uid=row.uid, scm_revision=row.scm_id, start_date=row.run_date, tags=row.description)

    def create(self, item: MonitorSession) -> MonitorSession:
        if item.uid in self._data:
            raise EntityAlreadyExists(item.uid)
        self._data[item.uid] = Session(
            uid=item.uid, description=item.tags, run_date=item.start_date, scm_id=item.scm_revision
        )
        return item

    def update(self, item: MonitorSession) -> MonitorSession:
        if item.uid not in self._data:
            raise EntityNotFound(item.uid)
        self._data[item.uid] = Session(
            uid=item.uid, description=item.tags, run_date=item.start_date, scm_id=item.scm_revision
        )
        return item
