import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.errors import ORMInvalidMapping
from monitor_server.infrastructure.orm.repositories import RepositoryBase


class MyTestModel(ORMModel):
    ident: Mapped[int | None] = mapped_column(primary_key=True, autoincrement=True, default=None)
    data: Mapped[str | None] = mapped_column(String(255), default=None)


class TestAbstractRepository:
    def test_model_init_reflects_the_the_generic_type(self, orm):
        class ATestRepository(RepositoryBase[MyTestModel]):
            """A dummy repository"""

        assert ATestRepository().model == MyTestModel

    def test_it_fails_to_init_a_repository_without_model(self, orm):
        class ATestRepository(RepositoryBase):
            """A dummy repository"""

        with pytest.raises(ORMInvalidMapping, match='no model found for repository ATestRepository'):
            ATestRepository()
