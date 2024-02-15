import typing as t

import pytest

from monitor_server.infrastructure.orm.config import ORMConfig, SessionConfig
from monitor_server.infrastructure.orm.engine import ORMEngine
from monitor_server.infrastructure.persistence.machines import (
    ExecutionContextInMemRepository,
    ExecutionContextRepository,
    ExecutionContextSQLRepository,
)
from monitor_server.infrastructure.persistence.metrics import (
    MetricInMemRepository,
    MetricRepository,
    MetricSQLRepository,
)
from monitor_server.infrastructure.persistence.services import (
    MonitoringMetricsInMemService,
    MonitoringMetricsService,
    MonitoringMetricsSQLService,
)
from monitor_server.infrastructure.persistence.sessions import (
    SessionInMemRepository,
    SessionRepository,
    SessionSQLRepository,
)

INT_AND_UT_PARAMS = [pytest.param('int', marks=pytest.mark.int()), pytest.param('ut', marks=pytest.mark.ut())]


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
def metrics_sql_service(orm: ORMEngine) -> t.Generator[MonitoringMetricsService, None, None]:
    service = MonitoringMetricsSQLService(orm)
    yield service
    service.truncate_all()


@pytest.fixture(params=INT_AND_UT_PARAMS)
def session_repository(request: pytest.FixtureRequest, orm) -> t.Iterator[SessionRepository]:
    with_sql = False
    if request.param == 'int':
        request.applymarker('int')
        with_sql = True
    if with_sql:
        sql_repo = SessionSQLRepository(orm.session)
        yield sql_repo
        sql_repo.truncate()
    else:
        im_repo = SessionInMemRepository()
        yield im_repo
        im_repo.truncate()


@pytest.fixture(params=INT_AND_UT_PARAMS)
def execution_context_repository(request: pytest.FixtureRequest, orm) -> t.Iterator[ExecutionContextRepository]:
    with_sql = False
    if request.param == 'int':
        request.applymarker('int')
        with_sql = True
    if with_sql:
        sql_repo = ExecutionContextSQLRepository(orm.session)
        yield sql_repo
        sql_repo.truncate()
    else:
        im_repo = ExecutionContextInMemRepository()
        yield im_repo
        im_repo.truncate()


@pytest.fixture(params=INT_AND_UT_PARAMS)
def metrics_repository(request: pytest.FixtureRequest, orm) -> t.Iterator[MetricRepository]:
    with_sql = False
    if request.param == 'int':
        request.applymarker('int')
        with_sql = True
    if with_sql:
        sql_repo = MetricSQLRepository(orm.session)
        yield sql_repo
        sql_repo.truncate()
    else:
        im_repo = MetricInMemRepository()
        yield im_repo
        im_repo.truncate()


@pytest.fixture(params=INT_AND_UT_PARAMS)
def metrics_service(request: pytest.FixtureRequest, orm) -> t.Iterator[MonitoringMetricsService]:
    with_sql = False
    if request.param == 'int':
        request.applymarker('int')
        with_sql = True
    if with_sql:
        sql_repo = MonitoringMetricsSQLService(orm)
        yield sql_repo
        sql_repo.truncate_all()
    else:
        im_repo = MonitoringMetricsInMemService()
        yield im_repo
        im_repo.truncate_all()
