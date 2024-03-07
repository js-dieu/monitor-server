import typing as t

from monitor_server.domain.models.abc import Entity
from monitor_server.infrastructure.orm.errors import ORMError


class EntityAlreadyExists(ORMError):
    """Raised when the system tries to insert a new machine with uid already taken."""

    def __init__(self, entity_type: t.Type[Entity], entity_id: str) -> None:
        self._entity_typename = entity_type.entity_name()
        self._entity_id = entity_id
        super().__init__(f'{self._entity_typename} "{entity_id}" already exists')

    @property
    def entity_typename(self) -> str:
        return self._entity_typename

    @property
    def entity_id(self) -> str:
        return self._entity_id


class EntityNotFound(ORMError):
    """Raised when querying a machine whose uid cannot be found."""

    def __init__(self, entity_type: t.Type[Entity], entity_id: str) -> None:
        self._entity_typename = entity_type.entity_name()
        self._entity_id = entity_id
        super().__init__(f'{self._entity_typename} "{entity_id}" cannot be found')

    @property
    def entity_typename(self) -> str:
        return self._entity_typename

    @property
    def entity_id(self) -> str:
        return self._entity_id


class LinkedEntityMissing(ORMError):
    """Raised when an entity linked to other entities"""

    def __init__(
        self,
        missing_entity_type: t.Type[Entity],
        missing_entity_id: str,
        linked_entity_type: t.Type[Entity],
        linked_entity_id: str,
    ) -> None:
        self._missing_entity_typename = missing_entity_type.entity_name()
        self._missing_entity_id = missing_entity_id
        super().__init__(
            f'{self._missing_entity_typename} {self.missing_entity_id} cannot be found. '
            f'{linked_entity_type.entity_name()} {linked_entity_id} cannot be processed'
        )

    @property
    def missing_entity_typename(self) -> str:
        return self._missing_entity_typename

    @property
    def missing_entity_id(self) -> str:
        return self._missing_entity_id
