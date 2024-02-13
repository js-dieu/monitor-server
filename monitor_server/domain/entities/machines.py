import hashlib
import typing as t
from functools import cached_property

from monitor_server.domain.entities.abc import Entity


class Machine(Entity):
    uid: str
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

    @cached_property
    def footprint(self) -> str:
        if not self.uid:
            hr = hashlib.md5()
            hr.update(str(self.cpu_count).encode())
            hr.update(str(self.cpu_frequency).encode())
            hr.update(str(self.cpu_type).encode())
            hr.update(str(self.cpu_vendor).encode())
            hr.update(str(self.total_ram).encode())
            hr.update(str(self.hostname).encode())
            hr.update(str(self.machine_type).encode())
            hr.update(str(self.machine_arch).encode())
            hr.update(str(self.system_info).encode())
            hr.update(str(self.python_info).encode())
            return hr.hexdigest()
        return self.uid
