import typing as t

import pytest

from monitor_server.domain.entities.machines import Machine
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.machines import ExecutionContextRepository
from monitor_server.tests.sdk.persistence.generators import MachineGenerator


class TestExecutionContextRepository:
    def test_it_creates_a_new_context_from_unknown_uid(
        self, execution_context_repository: ExecutionContextRepository, a_machine: Machine
    ):
        assert execution_context_repository.create(a_machine)

    def test_it_raises_entity_already_exists_when_creating_twice_the_same_uid(
        self, execution_context_repository: ExecutionContextRepository, a_machine: Machine
    ):
        execution_context_repository.create(a_machine)

        with pytest.raises(EntityAlreadyExists, match=f'Machine "{a_machine.uid}" already exists'):
            execution_context_repository.create(a_machine)

    def test_it_returns_a_machine_when_querying_a_known_uid(
        self, execution_context_repository: ExecutionContextRepository, a_machine: Machine
    ):
        execution_context_repository.create(a_machine)
        assert execution_context_repository.get(a_machine.uid)

    def test_it_raises_entity_not_found_when_querying_an_unknown_context(
        self, execution_context_repository: ExecutionContextRepository
    ):
        with pytest.raises(EntityNotFound, match='unknown'):
            execution_context_repository.get('unknown')

    def test_an_empty_repository_counts_0_elements(self, execution_context_repository: ExecutionContextRepository):
        assert execution_context_repository.count() == 0

    def test_a_repository_having_3_elements_counts_3(self, execution_context_repository: ExecutionContextRepository):
        generator = MachineGenerator()
        for xc in [generator() for _ in range(3)]:
            execution_context_repository.create(xc)
        assert execution_context_repository.count() == 3

    def test_it_lists_all_execution_contexts_when_no_page_info_is_given(
        self,
        execution_context_repository: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        machines = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_repository.create(machine)
            machines.append(machine)

        expected = PaginatedResponse[t.List[Machine]](
            data=sorted(machines, key=lambda m: m.uid), next_page=None, page_no=None
        )

        assert execution_context_repository.list() == expected

    def test_it_lists_all_execution_contexts_in_the_given_page(
        self,
        execution_context_repository: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        machines = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_repository.create(machine)
            machines.append(machine)
        expected = PaginatedResponse[t.List[Machine]](
            data=list(sorted(machines, key=lambda m: m.uid)[25:30]), page_no=5, next_page=None
        )
        assert execution_context_repository.list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_all_execution_contexts_in_the_given_page_and_provide_next_page_info(
        self,
        execution_context_repository: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        machines = []
        for machine in (machine_generator() for _ in range(30)):
            execution_context_repository.create(machine)
            machines.append(machine)
        expected = PaginatedResponse[t.List[Machine]](
            data=list(sorted(machines, key=lambda m: m.uid)[20:25]), page_no=4, next_page=5
        )
        assert execution_context_repository.list(PageableStatement(page_no=4, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        execution_context_repository: ExecutionContextRepository,
    ):
        machine_generator: MachineGenerator = MachineGenerator()
        for machine in (machine_generator() for _ in range(30)):
            execution_context_repository.create(machine)

        expected = PaginatedResponse[t.List[Machine]](data=[], page_no=10, next_page=None)
        assert execution_context_repository.list(PageableStatement(page_no=10, page_size=5)) == expected

    def test_it_counts_0_when_the_repository_is_empty(self, execution_context_repository: ExecutionContextRepository):
        assert execution_context_repository.count() == 0

    def test_it_counts_3_elements_when_3_elements_have_been_inserted(
        self, execution_context_repository: ExecutionContextRepository
    ):
        generator = MachineGenerator()
        for xc in [generator() for _ in range(3)]:
            execution_context_repository.create(xc)
        assert execution_context_repository.count() == 3
