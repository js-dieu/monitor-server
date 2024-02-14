import typing as t

from monitor_server.domain.dto.abc import DTO, Attribute
from monitor_server.domain.entities.machines import Machine


class CreateMachine(DTO):
    uid: str
    cpu_frequency: int = Attribute(gt=0)
    cpu_vendor: str
    cpu_count: int = Attribute(gt=0)
    cpu_type: str
    total_ram: int = Attribute(gt=0)
    hostname: str
    machine_type: str
    machine_arch: str
    system_info: str
    python_info: str


class NewMachineCreated(DTO):
    uid: str | None = None


class MachineListing(DTO):
    data: t.List[Machine]
    next_page: int | None = Attribute(default=None)
