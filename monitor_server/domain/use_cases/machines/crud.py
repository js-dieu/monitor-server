import typing as t

from monitor_server.domain.dto.machines import CreateMachine, NewMachineCreated
from monitor_server.domain.entities.machines import Machine
from monitor_server.domain.use_cases.abc import UseCase, UseCaseResult
from monitor_server.infrastructure.persistence.exceptions import ORMError
from monitor_server.infrastructure.persistence.machines import ExecutionContextRepository


class AddMachine(UseCase[CreateMachine, NewMachineCreated]):
    def __init__(self, machine_repository: ExecutionContextRepository) -> None:
        self._repository = machine_repository

    def execute(self, input_dto: CreateMachine) -> UseCaseResult[NewMachineCreated]:
        try:
            machine = t.cast(Machine, Machine.from_dict(input_dto.to_dict()))
            self._repository.create(machine)
            return UseCaseResult(status=True, data=NewMachineCreated(uid=machine.uid))
        except ORMError as e:
            return UseCaseResult(status=False, msg=str(e), data=NewMachineCreated())
