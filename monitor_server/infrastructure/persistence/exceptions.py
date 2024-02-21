import typing as t

from monitor_server.domain.models.abc import Entity
from monitor_server.infrastructure.orm.errors import ORMError


class EntityAlreadyExists(ORMError):
    """Raised when the system tries to insert a new machine with uid already taken."""

    def __init__(self, msg: str, entity_type: t.Type[Entity], entity_id: str) -> None:
        self._entity_type = entity_type.__name__
        self._entity_id = entity_id
        super().__init__(msg)

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def entity_id(self) -> str:
        return self._entity_id


class EntityNotFound(ORMError):
    """Raised when querying a machine whose uid cannot be found."""

    def __init__(self, msg: str, entity_type: t.Type[Entity], entity_id: str) -> None:
        self._entity_type = entity_type.__name__
        self._entity_id = entity_id
        super().__init__(msg)

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def entity_id(self) -> str:
        return self._entity_id


class LinkedEntityMissing(ORMError):
    """Raised when an entity linked to other entities"""

    def __init__(self, msg: str, missing_entity_type: t.Type[Entity], missing_entity_id: str) -> None:
        self._missing_entity_type = missing_entity_type.__class__.__name__
        self._missing_entity_id = missing_entity_id
        super().__init__(msg)

    @property
    def missing_entity(self) -> str:
        return self._missing_entity_type

    @property
    def missing_entity_id(self) -> str:
        return self._missing_entity_id
