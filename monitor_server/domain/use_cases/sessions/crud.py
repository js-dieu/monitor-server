import typing as t

from monitor_server.domain.models.abc import PageableRequest
from monitor_server.domain.models.sessions import MonitorSession, NewSessionCreated, SessionListing
from monitor_server.domain.use_cases.abc import UseCase
from monitor_server.domain.use_cases.exceptions import SessionAlreadyExists, UseCaseError
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.orm.pageable import PageableStatement
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists
from monitor_server.infrastructure.persistence.sessions import SessionRepository


class AddSession(UseCase[MonitorSession, NewSessionCreated]):
    def __init__(self, session_repo: SessionRepository) -> None:
        super().__init__()
        self._session_repo = session_repo

    def execute(self, input_dto: MonitorSession) -> NewSessionCreated:
        a_session = t.cast(MonitorSession, MonitorSession.from_dict(input_dto.to_dict()))
        try:
            self._session_repo.create(a_session)
            return NewSessionCreated(uid=a_session.uid.hex)
        except EntityAlreadyExists as e:
            raise SessionAlreadyExists(str(e)) from e
        except ORMError as e:
            raise UseCaseError(str(e)) from e


class ListSession(UseCase[PageableRequest, SessionListing]):
    def __init__(self, session_repo: SessionRepository) -> None:
        super().__init__()
        self._session_repo = session_repo

    def execute(self, input_dto: PageableRequest) -> SessionListing:
        try:
            page_info = None
            if input_dto.with_pagination:
                page_info = PageableStatement(page_no=input_dto.page_no, page_size=input_dto.page_size)
            result = self._session_repo.list(page_info)
            return SessionListing(data=result.data, next_page=result.next_page)
        except ORMError as e:
            raise UseCaseError(str(e)) from e
