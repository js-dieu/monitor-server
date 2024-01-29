import abc

from sqlalchemy import Integer, String, delete, distinct, func, select, tuple_
from sqlalchemy.orm import Mapped, Session, mapped_column

from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.repositories import InMemoryRepository, SQLRepository


class ExecutionContext(ORMModel):
    uid: Mapped[str] = mapped_column(String(64), nullable=False, primary_key=True)
    cpu_frequency: Mapped[int] = mapped_column(Integer(), nullable=False)
    cpu_vendor: Mapped[str] = mapped_column(String(256), nullable=False)
    cpu_count: Mapped[int] = mapped_column(Integer(), nullable=False)
    total_ram: Mapped[int] = mapped_column(Integer(), nullable=False)
    hostname: Mapped[str] = mapped_column(String(512), nullable=False)
    machine_type: Mapped[str] = mapped_column(String(32), nullable=False)
    machine_arch: Mapped[str] = mapped_column(String(16), nullable=False)
    system_info: Mapped[str] = mapped_column(String(256), nullable=False)
    python_info: Mapped[str] = mapped_column(String(512), nullable=False)


class ExecutionContextRepository:
    @abc.abstractmethod
    def save(self, item: ExecutionContext) -> ExecutionContext:
        """Persist a context"""

    @abc.abstractmethod
    def get(self, uid: str) -> ExecutionContext | None:
        """Get an execution context given an uid"""

    @abc.abstractmethod
    def count(self) -> int:
        """Count elements in the repository"""

    @abc.abstractmethod
    def truncate(self) -> None:
        """Remove all element in the repository"""


class ExecutionContextSQLRepository(ExecutionContextRepository, SQLRepository[ExecutionContext]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def save(self, item: ExecutionContext) -> ExecutionContext:
        self.session.add(item)
        self.session.commit()
        return item

    def get(self, uid: str) -> ExecutionContext | None:
        return self.session.get(ExecutionContext, uid)

    def count(self) -> int:
        primary_key = tuple(getattr(self.model, a) for a in self.primary_key)
        return (
            self.session.execute(
                select(self.model).with_only_columns(
                    # Operand should contain 1 column(s) error in case of composite primary key
                    func.count(distinct(tuple_(*primary_key))),
                ),
            )
        ).scalar_one()

    def truncate(self) -> None:
        self.session.execute(delete(self.model))
        self.session.commit()
        self.session.close()


class ExecutionContextInMemRepository(ExecutionContextRepository, InMemoryRepository[ExecutionContext]):
    def __init__(self) -> None:
        super().__init__()

    def save(self, item: ExecutionContext) -> ExecutionContext:
        self._data[item.uid] = item
        return item

    def get(self, uid: str) -> ExecutionContext | None:
        return self._data.get(uid)

    def count(self) -> int:
        return len(self._data)

    def truncate(self) -> None:
        self._data = {}
