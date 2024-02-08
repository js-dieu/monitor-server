import typing as t

from monitor_server.domain.dto.sessions import CreateSession, NewSessionCreated
from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.domain.use_cases.abc import UseCase
from monitor_server.domain.use_cases.exceptions import SessionAlreadyExists, UseCaseError
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists
from monitor_server.infrastructure.persistence.sessions import SessionRepository


class AddSession(UseCase[CreateSession, NewSessionCreated]):
    def __init__(self, session_repo: SessionRepository) -> None:
        super().__init__()
        self._session_repo = session_repo

    def execute(self, input_dto: CreateSession) -> NewSessionCreated:
        a_session = t.cast(MonitorSession, MonitorSession.from_dict(input_dto.to_dict()))
        try:
            self._session_repo.create(a_session)
            return NewSessionCreated(uid=a_session.uid)
        except EntityAlreadyExists as e:
            raise SessionAlreadyExists(str(e)) from e
        except ORMError as e:
            raise UseCaseError(str(e)) from e
