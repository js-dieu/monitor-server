import typing as t

from monitor_server.domain.dto.metrics import CreateMetricRequest, NewMetricCreated
from monitor_server.domain.entities.metrics import Metric
from monitor_server.domain.use_cases.abc import UseCase
from monitor_server.domain.use_cases.exceptions import InvalidMetric, MetricAlreadyExists, UseCaseError
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, LinkedEntityMissing, ORMError
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService


class AddMetric(UseCase[CreateMetricRequest, NewMetricCreated]):
    def __init__(self, metric_service: MonitoringMetricsService) -> None:
        self._metric_svc = metric_service

    def execute(self, input_dto: CreateMetricRequest) -> NewMetricCreated:
        try:
            metric = t.cast(Metric, Metric.from_dict(input_dto.to_dict()))
            self._metric_svc.add_metric(metric)
            return NewMetricCreated(uid=metric.uid.hex)
        except EntityAlreadyExists as e:
            raise MetricAlreadyExists(str(e)) from e
        except LinkedEntityMissing as e:
            raise InvalidMetric(str(e)) from e
        except ORMError as e:
            raise UseCaseError(str(e)) from e
