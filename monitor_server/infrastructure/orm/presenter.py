import abc
import inspect
import typing as t

from monitor_server.domain.models.abc import Entity
from monitor_server.infrastructure.orm.declarative import ORMModel

T_Domain = t.TypeVar('T_Domain', bound=Entity)
T_Domain_co = t.TypeVar('T_Domain_co', bound=Entity, covariant=True)
T_Model = t.TypeVar('T_Model', bound=ORMModel)
T_Model_co = t.TypeVar('T_Model_co', bound=ORMModel, covariant=True)
T_Type = t.TypeVar('T_Type')
T_Result = t.TypeVar('T_Result')


def _get_types(of: object) -> tuple[t.Type[ORMModel] | t.Type[Entity], ...]:
    models: t.List[t.Type[ORMModel] | t.Type[Entity]] = []
    for generic_base in of.__orig_bases__:  # type: ignore
        for arg in t.get_args(generic_base):
            if not inspect.isclass(arg) or not issubclass(arg, (ORMModel, Entity)):
                continue
            models.append(arg)
    if len(models) != 2:
        raise TypeError(f'Exactly two generics are expected, got {len(models)}.')
    return tuple(models)


@t.overload
def _build_key(right: ORMModel, left: t.Type[Entity]) -> str: ...


@t.overload
def _build_key(right: Entity, left: t.Type[ORMModel]) -> str: ...


def _build_key(right: ORMModel | Entity, left: t.Type[ORMModel] | t.Type[Entity]) -> str:
    return f'{right.__class__.__name__}::{left.__name__}'


class Converter(t.Generic[T_Type, T_Result], abc.ABC):
    @abc.abstractmethod
    def __call__(self, value: T_Type) -> T_Result: ...


class Presenter:
    def __init__(self) -> None:
        self.__presenter: t.Dict[str, Converter] = {}

    def register(self) -> t.Callable[[t.Type[Converter]], None]:
        def _store(converter: t.Type[Converter]) -> None:
            cvt = converter()
            tp, res = _get_types(cvt)  # type: ignore[assignment]
            key: str = f'{tp.__name__}::{res.__name__}'
            self.__presenter[key] = converter()

        return _store

    def to_orm(self, value: T_Domain, as_: t.Type[T_Model_co]) -> T_Model_co:
        return self.__presenter[_build_key(value, as_)](value)

    def from_orm(self, value: T_Model, as_: t.Type[T_Domain_co]) -> T_Domain_co:
        return self.__presenter[_build_key(value, as_)](value)


def _initiate_presenter() -> t.Callable[[], Presenter]:
    a_mapper: Presenter = Presenter()

    def _get_mapper() -> Presenter:
        return a_mapper

    return _get_mapper


get_presenter = _initiate_presenter()
presenter = get_presenter()
