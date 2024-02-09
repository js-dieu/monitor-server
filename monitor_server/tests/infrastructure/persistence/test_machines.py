import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.machines import (
    ExecutionContextInMemRepository,
    ExecutionContextSQLRepository,
)
from monitor_server.tests.sdk.persistence.generators import MachineGenerator


@pytest.mark.int()
class TestExecutionContextSQLRepository:
    def test_it_creates_a_new_context_from_unknown_uid(
        self, execution_context_sql_repo: ExecutionContextSQLRepository, a_machine: Machine
    ):
        assert execution_context_sql_repo.create(a_machine)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, execution_context_sql_repo: ExecutionContextSQLRepository, a_machine: Machine
    ):
        execution_context_sql_repo.create(a_machine)

        with pytest.raises(EntityAlreadyExists, match=f'Machine "{a_machine.uid}" already exists'):
            execution_context_sql_repo.create(a_machine)

    def test_it_returns_a_machine_when_querying_a_known_uid(
        self, execution_context_sql_repo: ExecutionContextSQLRepository, a_machine: Machine
    ):
        execution_context_sql_repo.create(a_machine)
        assert execution_context_sql_repo.get(a_machine.uid)

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self, execution_context_sql_repo: ExecutionContextSQLRepository
    ):
        with pytest.raises(EntityNotFound, match='unknown'):
            execution_context_sql_repo.get('unknown')

    def test_an_empty_repository_counts_0_elements(self, execution_context_sql_repo: ExecutionContextSQLRepository):
        assert execution_context_sql_repo.count() == 0

    def test_a_repository_having_3_elements_counts_3(self, execution_context_sql_repo: ExecutionContextSQLRepository):
        generator = MachineGenerator()
        for xc in [generator() for _ in range(3)]:
            execution_context_sql_repo.create(xc)
        assert execution_context_sql_repo.count() == 3


class TestExecutionContextInMemRepository:
    def test_it_creates_a_new_context_from_unknown_uid(
        self, execution_context_in_mem_repo: ExecutionContextInMemRepository, a_machine: Machine
    ):
        assert execution_context_in_mem_repo.create(a_machine)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, execution_context_in_mem_repo: ExecutionContextInMemRepository, a_machine: Machine
    ):
        execution_context_in_mem_repo.create(a_machine)

        with pytest.raises(EntityAlreadyExists, match=f'Machine "{a_machine.uid}" already exists'):
            execution_context_in_mem_repo.create(a_machine)

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self, execution_context_in_mem_repo: ExecutionContextInMemRepository
    ):
        with pytest.raises(EntityNotFound, match='unknown'):
            execution_context_in_mem_repo.get('unknown')

    def test_it_counts_0_when_the_repository_is_empty(
        self, execution_context_in_mem_repo: ExecutionContextInMemRepository
    ):
        assert execution_context_in_mem_repo.count() == 0

    def test_it_counts_3_elements_when_3_elements_have_been_inserted(
        self, execution_context_in_mem_repo: ExecutionContextInMemRepository
    ):
        generator = MachineGenerator()
        for xc in [generator() for _ in range(3)]:
            execution_context_in_mem_repo.create(xc)
        assert execution_context_in_mem_repo.count() == 3
