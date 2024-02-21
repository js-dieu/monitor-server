import typing as t

from monitor_server.domain.models.abc import Attribute, Entity, Model


class Machine(Entity):
    cpu_frequency: int
    cpu_vendor: str
    cpu_count: int
    cpu_type: str
    total_ram: int
    hostname: str
    machine_type: str
    machine_arch: str
    system_info: str
    python_info: str

    def __eq__(self, other: object) -> bool:
        if type(other) is not Machine:
            return False
        other_machine = t.cast(Machine, other)
        return (
            self.uid == other_machine.uid
            and self.cpu_frequency == other_machine.cpu_frequency
            and self.cpu_vendor == other_machine.cpu_vendor
            and self.cpu_count == other_machine.cpu_count
            and self.cpu_type == other_machine.cpu_type
            and self.total_ram == other_machine.total_ram
            and self.hostname == other_machine.hostname
            and self.machine_type == other_machine.machine_type
            and self.machine_arch == other_machine.machine_arch
            and self.system_info == other_machine.system_info
            and self.python_info == other_machine.python_info
        )


class NewMachineCreated(Model):
    uid: str | None = None


class MachineListing(Model):
    data: t.List[Machine]
    next_page: int | None = Attribute(default=None)
