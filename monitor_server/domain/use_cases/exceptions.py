class UseCaseError(Exception):
    """Base class for error issued by use case"""


class MachineAlreadyExists(UseCaseError):
    """Used to signify that a machine cannot be added because its uid is already taken by another machine"""


class SessionAlreadyExists(UseCaseError):
    """Used to signify that a session cannot be added because its uid is already taken by another session"""


class InvalidMetric(UseCaseError):
    """Used to indicate that a metric is being inserted without a valid session or machine"""


class MetricAlreadyExists(UseCaseError):
    """Used to signify that a metric cannot be added because its uid is already taken by another metric.
    This usually tells that a metric is inserted twice for the same session/context.
    """
