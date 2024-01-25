from typing import Any, Dict, Self, Set

from monitor_server.infrastructure.config.loader import InMemoryConfig

SetOfMemoryObject = Set['InMemoryObject']
SetOfMemorySection = Set['InMemorySection']
SetOfMemoryHolder = Set['InMemoryHolder']


class InMemoryObject:
    def __init__(self, name: str) -> None:
        self._name = name
        self._data: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f'<InMemoryObject> {self.name}'

    def __hash__(self) -> int:
        return hash(self._name)

    def with_value(self, name: str, value: Any) -> Self:
        self._data[name] = value
        return self

    def with_values(self, **kwargs: Any) -> Self:
        for name, value in kwargs.items():
            self._data[name] = value
        return self

    def with_ref(self, ref_path: str) -> Self:
        self._data['.ref'] = ref_path
        return self

    def build(self) -> Dict[str, Any]:
        return {self._name: self._data}


class InMemorySection:
    def __init__(self, name: str) -> None:
        self._name = name
        self._objects: SetOfMemoryObject = set()

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f'<InMemorySection> {self.name} ({len(self._objects)} objects)'

    def __contains__(self, an_item: InMemoryObject | str) -> bool:
        ident = an_item if isinstance(an_item, str) else an_item.name
        obj = list(filter(lambda o: o.name == ident, self._objects))
        return bool(obj)

    def __hash__(self) -> int:
        return hash(self._name)

    def with_object(self, an_object: InMemoryObject) -> Self:
        self._objects.add(an_object)
        return self

    def compute_object_ref_for(self, an_object: InMemoryObject | str) -> str:
        ident = an_object if isinstance(an_object, str) else an_object.name
        obj = list(filter(lambda o: o.name == ident, self._objects))
        if obj:
            return f'{self._name}.{ident}'
        raise KeyError(f'Object {ident} not found under section {self._name}.')

    def build(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for an_object in self._objects:
            data.update(an_object.build())
        return {self._name: data}


class InMemoryHolder:
    def __init__(self, identifier: str) -> None:
        self._ident = identifier
        self._objects: SetOfMemoryObject = set()
        self._sections: SetOfMemorySection = set()

    @property
    def name(self) -> str:
        return self._ident

    def __repr__(self) -> str:
        return f'<InMemoryHolder> {self.name} ({len(self._objects)} objects / {len(self._sections)} sections)'

    def __hash__(self) -> int:
        return hash(self._ident)

    def with_object(self, an_object: InMemoryObject) -> Self:
        self._objects.add(an_object)
        return self

    def with_section(self, a_section: InMemorySection) -> Self:
        self._sections.add(a_section)
        return self

    def compute_object_ref_for(self, an_object: InMemoryObject) -> str:
        if an_object in self._objects:
            return f'{self._ident}.{an_object.name}'
        for section in self._sections:
            if an_object in section:
                return f'{self._ident}.{section.compute_object_ref_for(an_object)}'
        raise KeyError(f'Object {an_object.name} not found under holder {self._ident}.')

    def build(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for an_object in self._objects:
            data.update(an_object.build())
        for a_section in self._sections:
            data.update(a_section.build())
        return data


class InMemoryConfigBuilder:
    def __init__(self) -> None:
        self._holders: SetOfMemoryHolder = set()

    def with_holder(self, holder: InMemoryHolder) -> Self:
        self._holders.add(holder)
        return self

    def build(self) -> InMemoryConfig:
        return InMemoryConfig({holder.name: holder.build() for holder in self._holders})
