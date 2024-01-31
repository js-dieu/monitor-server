from monitor_server.infrastructure.exceptions import InfrastructureError


class ORMError(InfrastructureError):
    """Base class for orm related exceptions (apart from SQLAlchemy"""


class ORMInvalidMapping(ORMError):
    """Raised whenever a repository is defined without being specialized on a type."""
