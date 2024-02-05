from monitor_server.infrastructure.orm.errors import ORMError


class EntityAlreadyExists(ORMError):
    """Raised when the system tries to insert a new machine with uid already taken."""


class EntityNotFound(ORMError):
    """Raised when querying a machine whose uid cannot be found."""


class LinkedEntityMissing(ORMError):
    """Raised when an entity linked to other entities"""
