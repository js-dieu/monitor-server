from dataclasses import dataclass

import pytest

from monitor_server.infrastructure.orm.config import ORMConfig, SessionConfig
from monitor_server.infrastructure.orm.engine import ORMEngine
from monitor_server.infrastructure.persistence.machines import (
    ExecutionContextInMemRepository,
    ExecutionContextSQLRepository,
)
from monitor_server.infrastructure.persistence.metrics import MetricInMemRepository, MetricSQLRepository
from monitor_server.infrastructure.persistence.sessions import (
    SessionInMemRepository,
    SessionSQLRepository,
)


@pytest.fixture(scope='session')
def orm_config() -> ORMConfig:
    return ORMConfig(
        driver='mysql+mysqldb',
        username='monitor',
        password='monitor',
        host='127.0.0.1',
        port=3307,
        database='metrics',
        echo=True,
        session=SessionConfig(autoflush=False, expire_on_commit=False),
    )


@pytest.fixture()
def orm(orm_config: ORMConfig) -> ORMEngine:
    return ORMEngine(orm_config)


@pytest.fixture()
def execution_context_sql_repo(orm: ORMEngine):
    repo = ExecutionContextSQLRepository(orm.session)
    yield repo
    repo.truncate()


@pytest.fixture()
def execution_context_in_mem_repo():
    repo = ExecutionContextInMemRepository()
    yield repo
    repo.truncate()


@pytest.fixture()
def session_sql_repo(orm: ORMEngine):
    repo = SessionSQLRepository(orm.session)
    yield repo
    repo.truncate()


@pytest.fixture()
def session_in_mem_repo():
    repo = SessionInMemRepository()
    yield repo
    repo.truncate()


@pytest.fixture()
def metric_sql_repo(orm: ORMEngine):
    repo = MetricSQLRepository(orm.session)
    yield repo
    repo.truncate()


@pytest.fixture()
def metric_in_mem_repo():
    repo = MetricInMemRepository()
    yield repo
    repo.truncate()


@dataclass(init=True)
class MetricService:
    session: SessionSQLRepository
    execution_contexts: ExecutionContextSQLRepository
    metric: MetricSQLRepository


@pytest.fixture()
def metrics_service(orm: ORMEngine):
    session = orm.session
    service = MetricService(
        session=SessionSQLRepository(session),
        execution_contexts=ExecutionContextSQLRepository(session),
        metric=MetricSQLRepository(session),
    )
    yield service
    service.execution_contexts.truncate()
    service.session.truncate()
    service.metric.truncate()
