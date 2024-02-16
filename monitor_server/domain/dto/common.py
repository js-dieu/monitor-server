from monitor_server.domain.dto.abc import DTO


class CountInfo(DTO):
    metrics: int
    sessions: int
    machines: int
