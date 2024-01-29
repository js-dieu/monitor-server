import pytest
from sqlalchemy import text

from monitor_server.infrastructure.orm.config import ORMConfig
from monitor_server.infrastructure.orm.engine import ORMEngine


@pytest.mark.int()
class TestORMEngine:
    def test_it_connects(self, orm_config: ORMConfig):
        my_orm = ORMEngine(orm_config)
        my_orm.engine.connect()
        assert my_orm.engine.raw_connection().is_valid

    def test_it_can_execute_query_from_session(self, orm_config: ORMConfig):
        my_orm = ORMEngine(orm_config)
        data = my_orm.session.execute(text('SELECT 1 FROM DUAL')).first()
        assert data == (1,)
