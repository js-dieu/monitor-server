import typing as t

from monitor_server.domain.models.abc import PageableRequest
from monitor_server.domain.models.metrics import Metric, MetricsListing, NewMetricCreated
from monitor_server.domain.use_cases.abc import UseCase
from monitor_server.domain.use_cases.exceptions import InvalidMetric, MetricAlreadyExists, UseCaseError
from monitor_server.infrastructure.orm.pageable import PageableStatement
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, LinkedEntityMissing, ORMError
from monitor_server.infrastructure.persistence.metrics import MetricRepository
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService


class AddMetric(UseCase[Metric, NewMetricCreated]):
    def __init__(self, metric_service: MonitoringMetricsService) -> None:
        super().__init__()
        self._metric_svc = metric_service

    def execute(self, input_dto: Metric) -> NewMetricCreated:
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


class ListMetrics(UseCase[PageableRequest, MetricsListing]):
    def __init__(self, metric_repo: MetricRepository) -> None:
        super().__init__()
        self._repo = metric_repo

    def execute(self, input_dto: PageableRequest) -> MetricsListing:
        try:
            page_info = None
            if input_dto.with_pagination:
                page_info = PageableStatement(page_no=input_dto.page_no, page_size=input_dto.page_size)
            result = self._repo.list(page_info)
            return MetricsListing(data=result.data, next_page=result.next_page)
        except ORMError as e:
            raise UseCaseError(str(e)) from e
