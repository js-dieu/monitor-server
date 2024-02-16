import datetime

from monitor_server.domain.dto.common import CountInfo
from monitor_server.domain.use_cases.common import CollectInfoUseCase
from monitor_server.infrastructure.persistence.services import MonitoringMetricsService
from monitor_server.tests.sdk.persistence.generators import MachineGenerator, MetricGenerator, MonitorSessionGenerator


class TestCollectInfoUseCase:
    def test_it_counts_no_elements_when_nothing_has_been_stored(self, metrics_service: MonitoringMetricsService):
        assert CollectInfoUseCase(metrics_service).execute() == CountInfo(metrics=0, sessions=0, machines=0)

    def test_it_counts_elements(self, metrics_service: MonitoringMetricsService):
        sessions_generator, machine_generator = MonitorSessionGenerator(), MachineGenerator()
        a_start_time = datetime.datetime.now(tz=datetime.UTC)
        sessions = [sessions_generator(start_time=a_start_time) for _ in range(5)]
        machines = [machine_generator() for _ in range(2)]
        for session in sessions:
            metrics_service.add_session(session)
        for machine in machines:
            metrics_service.add_machine(machine)
        metrics_generator = MetricGenerator(
            start_date=a_start_time,
            session_uid_cb=lambda step: sessions[step % 5].uid,
            machine_uid_cb=lambda step: machines[step % 2].uid,
        )
        metrics = [metrics_generator() for _ in range(50)]
        metrics_service.add_metrics(metrics)
        assert CollectInfoUseCase(metrics_service).execute() == CountInfo(
            metrics=len(metrics), sessions=len(sessions), machines=len(machines)
        )
