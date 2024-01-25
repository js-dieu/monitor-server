import abc
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Generic, Iterator, Protocol, Tuple, Type, TypeVar

from pydantic import BaseModel

URI = TypeVar('URI', contravariant=True)
ROOT = TypeVar('ROOT')
ELEMENT = TypeVar('ELEMENT')
RAW_CONFIG = Dict[str, Any]


class ConfigurationBase(BaseModel):
    """Base class for configuration wrapping pydantic BaseModel."""

    declared_as: ClassVar[str]

    class ConfigKey:
        def __init__(self, name: str, model: Type['ConfigurationBase']) -> None:
            self._name = name
            self._model = model

        def __repr__(self) -> str:
            return f'{self._name} ({self._model.__name__})'

        @property
        def model(self) -> Type['ConfigurationBase']:
            return self._model

        @property
        def name(self) -> str:
            return self._name

    def __init_subclass__(cls, **kwargs: str) -> None:
        super().__init_subclass__()
        key = kwargs.get('declared_as')
        if key is None:
            raise KeyError('Missing configuration mapping')
        if not isinstance(key, str):
            try:
                key = str(key)
            except (ValueError, TypeError) as e:
                raise KeyError(f'Not a valid mapping type: {e}') from e
        cls.declared_as = key

    @classmethod
    def config_key(cls) -> ConfigKey:
        return cls.ConfigKey(cls.declared_as, cls)


# ConfigurationModel = TypeVar('ConfigurationModel', bound=ConfigurationBase)


@dataclass(frozen=True)
class Input:
    """Config input produced by Config readers."""

    holder_name: str
    data: Dict[str, Any]


class Reader(Protocol[URI]):
    """Protocol that each reader must fulfill"""

    def __call__(self, holder_name: str, holder: URI) -> Input:
        """This method reads from the path on the given storage and return the loaded data"""


class DiscoveryService(Generic[ROOT, ELEMENT], abc.ABC):
    def __init__(self, root_path: ROOT, ext: str | None = None) -> None:
        self._root_path = root_path
        self._suffix = ext

    @property
    def root_path(self) -> ROOT:
        return self._root_path

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Tuple[str, ELEMENT]]:
        """Get the path to the next config holder."""

    @abc.abstractmethod
    def check(self) -> bool:
        """Check if the system hosting the configuration about to be queried is ready."""
