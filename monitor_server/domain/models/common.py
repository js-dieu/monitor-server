from monitor_server.domain.models.abc import Model


class CountInfo(Model):
    metrics: int
    sessions: int
    machines: int
