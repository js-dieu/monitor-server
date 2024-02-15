import pytest

from monitor_server.domain.dto.abc import PageableRequest
from monitor_server.domain.dto.machines import CreateMachine, MachineListing, NewMachineCreated
from monitor_server.domain.use_cases.machines.crud import AddMachine, ListMachine, MachineAlreadyExists
from monitor_server.infrastructure.persistence.machines import ExecutionContextRepository
from monitor_server.tests.sdk.persistence.generators import MachineGenerator


class TestAddMachine:
    def test_it_return_ok_when_the_machine_is_valid(self, execution_context_repository: ExecutionContextRepository):
        use_case = AddMachine(execution_context_repository)
        assert use_case.execute(
            CreateMachine(
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
        ) == NewMachineCreated(uid='abcd')

    def test_it_raises_machine_already_exists_when_the_machine_already_exists(
        self, execution_context_repository: ExecutionContextRepository
    ):
        use_case = AddMachine(execution_context_repository)
        use_case.execute(
            CreateMachine(
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
        )
        with pytest.raises(MachineAlreadyExists, match='Machine "abcd" already exists'):
            use_case.execute(
                CreateMachine(
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
            )


class TestListMachine:
    def setup_method(self) -> None:
        machine_generator: MachineGenerator = MachineGenerator()
        self.machines = []
        for machine in (machine_generator() for _ in range(30)):
            self.machines.append(machine)
        self.machines = sorted(self.machines, key=lambda m: m.uid)

    def test_it_returns_all_elements_when_no_page_info(self, execution_context_repository: ExecutionContextRepository):
        use_case = ListMachine(execution_context_repository)
        for machine in self.machines:
            execution_context_repository.create(machine)
        result = use_case.execute(PageableRequest())
        assert result == MachineListing(data=self.machines, next_page=None)

    def test_it_returns_no_elements_when_out_of_bounds(self, execution_context_repository: ExecutionContextRepository):
        use_case = ListMachine(execution_context_repository)
        for machine in self.machines:
            execution_context_repository.create(machine)
        result = use_case.execute(PageableRequest(page_no=15, page_size=5))
        assert result == MachineListing(data=[], next_page=None)

    def test_it_returns_elements_with_next_page_when_listing_is_not_complete(
        self, execution_context_repository: ExecutionContextRepository
    ):
        use_case = ListMachine(execution_context_repository)
        for machine in self.machines:
            execution_context_repository.create(machine)
        result = use_case.execute(PageableRequest(page_no=1, page_size=5))
        assert result == MachineListing(data=self.machines[5:10], next_page=2)
