from monitor_server.domain.models.sessions import MonitorSession
from monitor_server.infrastructure.orm.repositories import CRUDRepositoryABC, InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.models import Session

SessionRepository = CRUDRepositoryABC[MonitorSession, Session]


class SessionSQLRepository(SQLRepository[MonitorSession, Session]): ...


class SessionInMemRepository(InMemoryRepository[MonitorSession, Session]): ...
