from monitor_server.infrastructure.persistence.converters import (
    MachineToORMMachine,
    MetricToORMMetric,
    ORMMachineToMachine,
    ORMMetricToMetric,
    ORMSessionToDomain,
    SessionToORMSession,
)

_converters = [
    MachineToORMMachine,
    MetricToORMMetric,
    ORMMachineToMachine,
    ORMMetricToMetric,
    ORMSessionToDomain,
    SessionToORMSession,
]
