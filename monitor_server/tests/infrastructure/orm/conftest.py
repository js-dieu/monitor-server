import pytest

from monitor_server.infrastructure.orm.config import ORMConfig, SessionConfig
from monitor_server.infrastructure.orm.engine import ORMEngine


@pytest.fixture(scope='session')
def orm_config() -> ORMConfig:
    return ORMConfig(
        driver='mysql+mysqldb',
        username='monitor',
        password='monitor',
        host='127.0.0.1',
        port=3307,
        database='metrics',
        echo=False,
        session=SessionConfig(autoflush=False, expire_on_commit=False),
    )


@pytest.fixture()
def orm(orm_config: ORMConfig) -> ORMEngine:
    return ORMEngine(orm_config)
