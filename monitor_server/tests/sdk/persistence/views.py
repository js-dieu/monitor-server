import typing as t
from collections import defaultdict

from monitor_server.domain.models.abc import Entity

AnyEntity = t.TypeVar('AnyEntity', bound=Entity)


class EntityView(t.Generic[AnyEntity]):
    def __init__(self, key: t.Callable[[AnyEntity], str]) -> None:
        self._view: t.DefaultDict[str, t.List[AnyEntity]] = defaultdict(list)
        self._key_of = key

    def add(self, entity: AnyEntity) -> AnyEntity:
        self._view[self._key_of(entity)].append(entity)
        return entity

    def view(self, key: str) -> t.List[AnyEntity]:
        return self._view.get(key, [])

    def all_(self) -> t.List[AnyEntity]:
        result: t.List[AnyEntity] = []
        for values in self._view.values():
            result.extend(values)
        return result
