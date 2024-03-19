from monitor_server.domain.models.machines import Machine
from monitor_server.infrastructure.orm.repositories import CRUDRepositoryABC, InMemoryRepository, SQLRepository
from monitor_server.infrastructure.persistence.models import ExecutionContext

ExecutionContextRepository = CRUDRepositoryABC[Machine, ExecutionContext]


class ExecutionContextSQLRepository(SQLRepository[Machine, ExecutionContext]): ...


class ExecutionContextInMemRepository(InMemoryRepository[Machine, ExecutionContext]): ...
