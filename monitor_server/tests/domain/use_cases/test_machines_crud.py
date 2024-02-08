import pytest

from monitor_server.domain.dto.machines import CreateMachine, NewMachineCreated
from monitor_server.domain.use_cases.machines.crud import AddMachine, MachineAlreadyExists
from monitor_server.infrastructure.persistence.machines import ExecutionContextRepository


@pytest.mark.int()
class TestAddMachineDB:
    def test_it_return_ok_when_the_machine_is_valid(self, execution_context_sql_repo: ExecutionContextRepository):
        use_case = AddMachine(execution_context_sql_repo)
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
        self, execution_context_sql_repo: ExecutionContextRepository
    ):
        use_case = AddMachine(execution_context_sql_repo)
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


class TestAddMachineInMem:
    def test_it_return_ok_when_the_machine_is_valid(self, execution_context_in_mem_repo: ExecutionContextRepository):
        use_case = AddMachine(execution_context_in_mem_repo)
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
        self, execution_context_in_mem_repo: ExecutionContextRepository
    ):
        use_case = AddMachine(execution_context_in_mem_repo)
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
