from monitor_server.domain.dto.abc import DTO, Attrib


class CreateMachine(DTO):
    uid: str
    cpu_frequency: int = Attrib(gt=0)
    cpu_vendor: str
    cpu_count: int = Attrib(gt=0)
    cpu_type: str
    total_ram: int = Attrib(gt=0)
    hostname: str
    machine_type: str
    machine_arch: str
    system_info: str
    python_info: str


class NewMachine(DTO):
    uid: str | None = None
