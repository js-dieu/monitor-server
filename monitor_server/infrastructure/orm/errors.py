class ORMError(Exception):
    """Base class for orm related exceptions (apart from SQLAlchemy"""


class ORMInvalidMapping(ORMError):
    """Raised whenever a repository is defined without being specialized on a type."""
