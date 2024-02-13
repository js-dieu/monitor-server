import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.infrastructure.orm.pageable import PageableStatement
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.machines import ExecutionContextRepository
from monitor_server.tests.sdk.persistence.generators import MachineGenerator


@pytest.mark.int()
class TestExecutionContextSQLRepository:
    def test_it_creates_a_new_context_from_unknown_uid(
        self, execution_context_sql_repo: ExecutionContextRepository, a_machine: Machine
    ):
        assert execution_context_sql_repo.create(a_machine)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, execution_context_sql_repo: ExecutionContextRepository, a_machine: Machine
    ):
        execution_context_sql_repo.create(a_machine)

        with pytest.raises(EntityAlreadyExists, match=f'Machine "{a_machine.uid}" already exists'):
            execution_context_sql_repo.create(a_machine)

    def test_it_returns_a_machine_when_querying_a_known_uid(
        self, execution_context_sql_repo: ExecutionContextRepository, a_machine: Machine
    ):
        execution_context_sql_repo.create(a_machine)
        assert execution_context_sql_repo.get(a_machine.uid)

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self, execution_context_sql_repo: ExecutionContextRepository
    ):
        with pytest.raises(EntityNotFound, match='unknown'):
            execution_context_sql_repo.get('unknown')

    def test_an_empty_repository_counts_0_elements(self, execution_context_sql_repo: ExecutionContextRepository):
        assert execution_context_sql_repo.count() == 0

    def test_a_repository_having_3_elements_counts_3(self, execution_context_sql_repo: ExecutionContextRepository):
        generator = MachineGenerator()
        for xc in [generator() for _ in range(3)]:
            execution_context_sql_repo.create(xc)
        assert execution_context_sql_repo.count() == 3

    def test_it_lists_all_execution_contexts_when_no_page_info_is_given(
        self,
        execution_context_sql_repo: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        expected = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_sql_repo.create(machine)
            expected.append(machine)
        assert execution_context_sql_repo.list() == sorted(expected, key=lambda m: m.uid)

    def test_it_lists_all_execution_contexts_in_the_given_page(
        self,
        execution_context_sql_repo: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        expected = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_sql_repo.create(machine)
            expected.append(machine)
        expected = sorted(expected, key=lambda m: m.uid)[25:30]
        assert execution_context_sql_repo.list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        execution_context_sql_repo: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        expected = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_sql_repo.create(machine)
            expected.append(machine)
        assert execution_context_sql_repo.list(PageableStatement(page_no=10, page_size=5)) == []


class TestExecutionContextInMemRepository:
    def test_it_creates_a_new_context_from_unknown_uid(
        self, execution_context_in_mem_repo: ExecutionContextRepository, a_machine: Machine
    ):
        assert execution_context_in_mem_repo.create(a_machine)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, execution_context_in_mem_repo: ExecutionContextRepository, a_machine: Machine
    ):
        execution_context_in_mem_repo.create(a_machine)

        with pytest.raises(EntityAlreadyExists, match=f'Machine "{a_machine.uid}" already exists'):
            execution_context_in_mem_repo.create(a_machine)

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self, execution_context_in_mem_repo: ExecutionContextRepository
    ):
        with pytest.raises(EntityNotFound, match='unknown'):
            execution_context_in_mem_repo.get('unknown')

    def test_it_counts_0_when_the_repository_is_empty(self, execution_context_in_mem_repo: ExecutionContextRepository):
        assert execution_context_in_mem_repo.count() == 0

    def test_it_counts_3_elements_when_3_elements_have_been_inserted(
        self, execution_context_in_mem_repo: ExecutionContextRepository
    ):
        generator = MachineGenerator()
        for xc in [generator() for _ in range(3)]:
            execution_context_in_mem_repo.create(xc)
        assert execution_context_in_mem_repo.count() == 3

    def test_it_lists_all_execution_contexts_when_no_page_info_is_given(
        self,
        execution_context_in_mem_repo: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        expected = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_in_mem_repo.create(machine)
            expected.append(machine)
        assert execution_context_in_mem_repo.list() == sorted(expected, key=lambda m: m.uid)

    def test_it_lists_all_execution_contexts_in_the_given_page(
        self,
        execution_context_in_mem_repo: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        expected = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_in_mem_repo.create(machine)
            expected.append(machine)
        expected = sorted(expected, key=lambda m: m.uid)[25:30]
        assert execution_context_in_mem_repo.list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        execution_context_in_mem_repo: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        expected = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_in_mem_repo.create(machine)
            expected.append(machine)
        assert execution_context_in_mem_repo.list(PageableStatement(page_no=10, page_size=5)) == []
