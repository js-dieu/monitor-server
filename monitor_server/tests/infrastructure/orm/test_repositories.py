import typing as t

import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from monitor_server.domain.models.abc import Entity
from monitor_server.infrastructure.orm.declarative import ORMModel
from monitor_server.infrastructure.orm.errors import ORMInvalidMapping
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.orm.repositories import CRUDRepositoryBase


class MyTestModel(ORMModel):
    ident: Mapped[int | None] = mapped_column(primary_key=True, autoincrement=True, default=None)
    data: Mapped[str | None] = mapped_column(String(255), default=None)


MyTestEntity = Entity


class TestAbstractRepository:
    def test_model_is_reflected_right_after_init(self):
        class ATestRepository(CRUDRepositoryBase[MyTestEntity, MyTestModel]):
            """A dummy repository"""

            def create(self, item: t.Any) -> t.Any:
                return None

            def update(self, machine: t.Any) -> t.Any:
                return None

            def get(self, uid: str) -> t.Any:
                return None

            def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[t.Any]]:
                return PaginatedResponse(next_page=None, page_no=0, data=[])

            def count(self) -> int:
                return 0

            def delete(self, uid: str) -> None:
                return None

            def truncate(self) -> None:
                return None

        assert ATestRepository().model == MyTestModel

    def test_domain_is_reflected_right_after_init(self):
        class ATestRepository(CRUDRepositoryBase[MyTestEntity, MyTestModel]):
            """A dummy repository"""

            def create(self, item: t.Any) -> t.Any:
                return None

            def update(self, machine: t.Any) -> t.Any:
                return None

            def get(self, uid: str) -> t.Any:
                return None

            def delete(self, uid: str) -> None:
                return None

            def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[t.Any]]:
                return PaginatedResponse(next_page=None, page_no=0, data=[])

            def count(self) -> int:
                return 0

            def truncate(self) -> None:
                return None

        assert ATestRepository().domain == MyTestEntity

    def test_it_fails_to_init_a_repository_without_model(self):
        class ATestRepository(CRUDRepositoryBase[MyTestEntity, t.List]):  # type: ignore[type-var]
            """A dummy repository"""

            def create(self, item: t.Any) -> t.Any:
                return None

            def update(self, machine: t.Any) -> t.Any:
                return None

            def get(self, uid: str) -> t.Any:
                return None

            def delete(self, uid: str) -> None:
                return None

            def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[t.Any]]:
                return PaginatedResponse(next_page=None, page_no=0, data=[])

            def count(self) -> int:
                return 0

            def truncate(self) -> None:
                return None

        with pytest.raises(ORMInvalidMapping, match='no model found for repository ATestRepository'):
            ATestRepository()

    def test_it_fails_to_init_a_repository_without_model_nor_entity(self):
        class ATestRepository(CRUDRepositoryBase[t.List, MyTestModel]):  # type: ignore[type-var]
            """A dummy repository"""

            def create(self, item: t.Any) -> t.Any:
                return None

            def delete(self, uid: str) -> None:
                return None

            def update(self, machine: t.Any) -> t.Any:
                return None

            def get(self, uid: str) -> t.Any:
                return None

            def list(self, page_info: PageableStatement | None = None) -> PaginatedResponse[t.List[t.Any]]:
                return PaginatedResponse(next_page=None, page_no=0, data=[])

            def count(self) -> int:
                return 0

            def truncate(self) -> None:
                return None

        with pytest.raises(ORMInvalidMapping, match='no domain object found for repository ATestRepository'):
            ATestRepository()
