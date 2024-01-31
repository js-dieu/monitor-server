import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.machines import (
    ExecutionContextInMemRepository,
    ExecutionContextSQLRepository,
)


@pytest.mark.int()
class TestExecutionContextSQLRepository:
    def test_it_creates_a_new_context_from_unknown_uid(self, execution_context_sql_repo: ExecutionContextSQLRepository):
        xc = Machine(
            uid='abcd',
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            cpu_type='cpu_type',
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )
        assert execution_context_sql_repo.create(xc)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, execution_context_sql_repo: ExecutionContextSQLRepository
    ):
        xc = Machine(
            uid='abcd',
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            cpu_type='cpu_type',
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )
        execution_context_sql_repo.create(xc)

        with pytest.raises(EntityAlreadyExists, match='abcd'):
            execution_context_sql_repo.create(xc)

    def test_it_returns_a_machine_when_querying_a_known_uid(
        self, execution_context_sql_repo: ExecutionContextSQLRepository
    ):
        xc = Machine(
            uid='abcd',
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            cpu_type='cpu_type',
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )
        execution_context_sql_repo.create(xc)
        assert execution_context_sql_repo.get('abcd').uid == 'abcd'

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self, execution_context_sql_repo: ExecutionContextSQLRepository
    ):
        with pytest.raises(EntityNotFound, match='unknown'):
            execution_context_sql_repo.get('unknown')

    def test_an_empty_repository_counts_0_elements(self, execution_context_sql_repo: ExecutionContextSQLRepository):
        assert execution_context_sql_repo.count() == 0

    def test_a_repository_having_3_elements_counts_3(self, execution_context_sql_repo: ExecutionContextSQLRepository):
        xcs = [
            Machine(
                uid=key,
                cpu_frequency=1024,
                cpu_vendor='cpu_vendor',
                cpu_count=32 + i,
                cpu_type='cpu_type',
                total_ram=2048 * i,
                hostname=f'hostname_{key}',
                machine_type='type',
                machine_arch='arch',
                system_info='system info',
                python_info='python info',
            )
            for key, i in [('abcd', 1), ('efgh', 2), ('ijkl', 3)]
        ]
        for xc in xcs:
            execution_context_sql_repo.create(xc)
        assert execution_context_sql_repo.count() == 3


class TestExecutionContextInMemRepository:
    def test_it_creates_a_new_context_from_unknown_uid(
        self, execution_context_sql_repo: ExecutionContextInMemRepository
    ):
        xc = Machine(
            uid='abcd',
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            cpu_type='cpu_type',
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )
        assert execution_context_sql_repo.create(xc)

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self, execution_context_sql_repo: ExecutionContextInMemRepository
    ):
        with pytest.raises(EntityNotFound, match='unknown'):
            execution_context_sql_repo.get('unknown')

    def test_it_counts_0_when_the_repository_is_empty(
        self, execution_context_sql_repo: ExecutionContextInMemRepository
    ):
        assert execution_context_sql_repo.count() == 0

    def test_it_counts_3_elements_when_3_elements_have_been_inserted(
        self, execution_context_sql_repo: ExecutionContextInMemRepository
    ):
        xcs = [
            Machine(
                uid=key,
                cpu_frequency=1024,
                cpu_vendor='cpu_vendor',
                cpu_count=32 + i,
                cpu_type='cpu_type',
                total_ram=2048 * i,
                hostname=f'hostname_{key}',
                machine_type='type',
                machine_arch='arch',
                system_info='system info',
                python_info='python info',
            )
            for key, i in [('abcd', 1), ('efgh', 2), ('ijkl', 3)]
        ]
        for xc in xcs:
            execution_context_sql_repo.create(xc)
        assert execution_context_sql_repo.count() == 3
