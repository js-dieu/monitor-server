import hashlib
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
