from monitor_server.domain.dto.common import CountInfo
from monitor_server.domain.use_cases.abc import UseCaseWithoutInput
from monitor_server.domain.use_cases.exceptions import UseCaseError
from monitor_server.infrastructure.orm.errors import ORMError
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService


class CollectInfoUseCase(UseCaseWithoutInput[CountInfo]):
    def __init__(self, metric_service: MonitoringMetricsService) -> None:
        self._service = metric_service

    def execute(self) -> CountInfo:
        try:
            return CountInfo(
                metrics=self._service.count_metrics(),
                sessions=self._service.count_sessions(),
                machines=self._service.count_machines(),
            )
        except ORMError as e:
            raise UseCaseError(str(e)) from e
