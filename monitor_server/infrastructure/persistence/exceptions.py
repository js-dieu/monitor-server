from monitor_server.infrastructure.exceptions import InfrastructureError


class MachineError(InfrastructureError):
    """Base error for machine persistence related operations."""


class MachineAlreadyExists(MachineError):
    """Raised when the system tries to insert a new machine with uid already taken."""


class MachineNotFound(MachineError):
    """Raised when querying a machine whose uid cannot be found."""
