import pathlib
from typing import Any, Callable, Dict, Generator, Iterator, List, Literal, Mapping, Tuple

from yaml import safe_load

from monitor_server.infrastructure.config.base import RAW_CONFIG, DiscoveryService, Input, Reader

Loader = Callable[[pathlib.Path], Tuple[str, Dict[str, Any]]]


class InMemoryConfig:
    def __init__(self, config: Dict[str, Any]) -> None:
        self._holders = config

    def holders(self) -> List[str]:
        return list(self._holders.keys())

    def __getitem__(self, item: str) -> Dict[str, Any]:
        return {item: self._holders.get(item, {})}

    def data(self) -> RAW_CONFIG:
        return dict(self._holders)


class MemoryDiscoveryService(DiscoveryService[InMemoryConfig, Mapping]):
    def __iter__(self) -> Iterator[Tuple[str, RAW_CONFIG]]:
        def iter_root_dir() -> Generator[Tuple[str, RAW_CONFIG], None, None]:
            for config_holder_key in self.root_path.holders():
                yield config_holder_key, self.root_path[config_holder_key]

        return iter_root_dir()

    def check(self) -> bool:
        return True


class FileDiscoveryService(DiscoveryService[pathlib.Path, pathlib.Path]):
    def __iter__(self) -> Iterator[Tuple[str, pathlib.Path]]:
        def iter_root_dir() -> Generator[Tuple[str, pathlib.Path], None, None]:
            for config_file in self.root_path.glob(f'*.{self._suffix}'):
                if not config_file.is_symlink():
                    yield config_file.stem, config_file

        return iter_root_dir()

    def check(self) -> bool:
        return self.root_path.exists()


class YamlReader(Reader[pathlib.Path]):
    suffixes: Literal['yml'] = 'yml'

    def __call__(self, holder_name: str, holder: pathlib.Path) -> Input:
        return Input(holder_name=holder_name, data=safe_load(holder.read_text()))


class MemoryReader(Reader[InMemoryConfig]):
    def __call__(self, holder_name: str, config: InMemoryConfig) -> Input:
        return Input(holder_name=holder_name, data=config[holder_name])
