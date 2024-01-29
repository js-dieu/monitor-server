from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import delete, text

from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.engine import ORMEngine


class AUIDDateTimeModel(ORMModel):
    uid: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(default=None)
    # mysql_engine = 'InnoDB'


class BasicRepo:
    def __init__(self, orm: ORMEngine) -> None:
        self.session = orm.session
        self.session.execute(
            text(
                f'CREATE TABLE IF NOT EXISTS {AUIDDateTimeModel.__tablename__} ('
                f' uid INT PRIMARY KEY,'
                f' created_at DATETIME(6)'
                f');'
            )
        )

    def save(self, item: AUIDDateTimeModel) -> None:
        self.session.add(item)
        self.session.commit()

    def truncate(self) -> None:
        self.session.execute(delete(AUIDDateTimeModel))
        self.session.commit()
        self.session.close()


@pytest.fixture()
def repository(orm: ORMEngine):
    repo = BasicRepo(orm)
    try:
        yield repo
    finally:
        repo.session.rollback()
        repo.truncate()


@pytest.mark.int()
class TestCustomTypes:
    def test_it_converts_a_datetime_object_to_a_utc_based_datetime(self, repository: BasicRepo):
        local_now = datetime(2023, 12, 4, 22, 14, 31, 123456, tzinfo=ZoneInfo('Europe/Paris'))
        utc_now = local_now.astimezone(UTC)
        model = AUIDDateTimeModel(created_at=local_now, uid=1)
        repository.save(model)
        assert model.created_at == utc_now

    def test_it_raises_statement_error_when_the_datetime_has_no_tzinfo(self, repository: BasicRepo):
        local_now = datetime(  # noqa
            2023, 12, 4, 22, 14, 31, 123456
        )
        model = AUIDDateTimeModel(created_at=local_now, uid=2)
        with pytest.raises(StatementError, match='Time Zone information is required'):
            repository.save(model)


class TestORMModel:
    def test_it_reflects_the_table_name(self):
        assert AUIDDateTimeModel.__tablename__ == 'AUIDDateTimeModel'
