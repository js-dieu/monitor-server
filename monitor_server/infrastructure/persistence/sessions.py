import abc
import typing as t

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import insert, select, update

from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.orm.repositories import InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.mapper import ORMMapper
from monitor_server.infrastructure.persistence.models import Session


class SessionRepository:
    @abc.abstractmethod
    def create(self, item: MonitorSession) -> MonitorSession:
        """Persist a new session"""

    @abc.abstractmethod
    def update(self, machine: MonitorSession) -> MonitorSession:
        """Update an existing session"""

    @abc.abstractmethod
    def get(self, uid: str) -> MonitorSession:
        """Get a session given an uid"""

    @abc.abstractmethod
    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[MonitorSession]]:
        """List all known sessions"""

    @abc.abstractmethod
    def count(self) -> int:
        """Count the number of items in this repository"""


class SessionSQLRepository(SessionRepository, SQLRepository[Session]):
    def create(self, item: MonitorSession) -> MonitorSession:
        stmt = insert(Session).values(
            uid=item.uid, description=item.tags, run_date=item.start_date, scm_id=item.scm_revision
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError as e:
            raise EntityAlreadyExists(f'Session "{item.uid}" already exists', MonitorSession, item.uid) from e
        except SQLAlchemyError as e:
            raise ORMError(str(e)) from e
        return item

    def count(self) -> int:
        return super()._count()

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
            return ORMMapper().orm_session_to_entity(row[0])
        raise EntityNotFound(f'Session "{uid}" cannot be found', MonitorSession, uid)

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[MonitorSession]]:
        q = self.session.query(self.model)
        mapper = ORMMapper()
        if page_info:
            q = q.limit(page_info.page_size).offset(page_info.offset)
            count = self.count()
            rows = t.cast(t.Iterable[Session], q.all())
            return page_info.build_response(
                [mapper.orm_session_to_entity(row) for row in rows or []], elements_count=count
            )

        rows = t.cast(t.Iterable[Session], q.all())
        return PaginatedResponse(
            data=[mapper.orm_session_to_entity(row) for row in rows or []],
            page_no=None,
            next_page=None,
        )


class SessionInMemRepository(SessionRepository, InMemoryRepository[Session]):
    def get(self, uid: str) -> MonitorSession:
        row = self._data.get(uid)
        if row is None:
            raise EntityNotFound(f'Session "{uid}" cannot be found', MonitorSession, uid)

        return MonitorSession(uid=row.uid, scm_revision=row.scm_id, start_date=row.run_date, tags=row.description)

    def create(self, item: MonitorSession) -> MonitorSession:
        if item.uid in self._data:
            raise EntityAlreadyExists(f'Session "{item.uid}" already exists', MonitorSession, item.uid)
        self._data[item.uid] = Session(
            uid=item.uid, description=item.tags, run_date=item.start_date, scm_id=item.scm_revision
        )
        return item

    def update(self, item: MonitorSession) -> MonitorSession:
        if item.uid not in self._data:
            raise EntityNotFound(f'Session "{item.uid}" cannot be found', MonitorSession, item.uid)
        self._data[item.uid] = Session(
            uid=item.uid, description=item.tags, run_date=item.start_date, scm_id=item.scm_revision
        )
        return item

    def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[MonitorSession]]:
        mapper = ORMMapper()
        if page_info is None:
            return PaginatedResponse(
                data=[
                    mapper.orm_session_to_entity(session)
                    for session in sorted(self._data.values(), key=lambda m: m.uid)
                ],
                page_no=None,
                next_page=None,
            )
        page = slice(page_info.offset, page_info.offset + page_info.page_size)
        element_ids = sorted(self._data.keys())[page]
        return page_info.build_response(
            data=[mapper.orm_session_to_entity(self._data[element_id]) for element_id in element_ids],
            elements_count=self.count(),
        )

    def count(self) -> int:
        return super()._count()
