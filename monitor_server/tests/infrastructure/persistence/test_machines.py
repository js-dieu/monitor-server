import pytest

from monitor_server.infrastructure.persistence.machines import (
    ExecutionContext,
    ExecutionContextInMemRepository,
    ExecutionContextSQLRepository,
)


@pytest.mark.int()
class TestExecutionContextSQLRepository:
    def test_it_persists_a_context(self, execution_context_sql_repo: ExecutionContextSQLRepository):
        xc = ExecutionContext(
            uid='abcd',
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )
        assert execution_context_sql_repo.save(xc)

    def test_it_returns_none_when_querying_an_unknown_context(
        self, execution_context_sql_repo: ExecutionContextSQLRepository
    ):
        assert None is execution_context_sql_repo.get('unknown')

    def test_it_counts_0_when_the_repository_is_empty(self, execution_context_sql_repo: ExecutionContextSQLRepository):
        assert execution_context_sql_repo.count() == 0

    def test_it_counts_3_elements_when_3_elements_have_been_inserted(
        self, execution_context_sql_repo: ExecutionContextSQLRepository
    ):
        xcs = [
            ExecutionContext(
                uid=key,
                cpu_frequency=1024,
                cpu_vendor='cpu_vendor',
                cpu_count=32 + i,
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
            execution_context_sql_repo.save(xc)
        assert execution_context_sql_repo.count() == 3


class TestExecutionContextInMemRepository:
    def test_it_persists_a_context(self, execution_context_sql_repo: ExecutionContextInMemRepository):
        xc = ExecutionContext(
            uid='abcd',
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )
        assert execution_context_sql_repo.save(xc)

    def test_it_returns_none_when_querying_an_unknown_context(
        self, execution_context_sql_repo: ExecutionContextInMemRepository
    ):
        assert None is execution_context_sql_repo.get('unknown')

    def test_it_counts_0_when_the_repository_is_empty(
        self, execution_context_sql_repo: ExecutionContextInMemRepository
    ):
        assert execution_context_sql_repo.count() == 0

    def test_it_counts_3_elements_when_3_elements_have_been_inserted(
        self, execution_context_sql_repo: ExecutionContextInMemRepository
    ):
        xcs = [
            ExecutionContext(
                uid=key,
                cpu_frequency=1024,
                cpu_vendor='cpu_vendor',
                cpu_count=32 + i,
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
            execution_context_sql_repo.save(xc)
        assert execution_context_sql_repo.count() == 3
