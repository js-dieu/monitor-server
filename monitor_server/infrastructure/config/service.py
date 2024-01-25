import pathlib
from typing import Dict

from monitor_server.infrastructure.config.app import ApplicationConfig, app_config
from monitor_server.infrastructure.config.base import RAW_CONFIG, DiscoveryService, Reader
from monitor_server.infrastructure.config.loader import (
    FileDiscoveryService,
    InMemoryConfig,
    MemoryDiscoveryService,
    MemoryReader,
    YamlReader,
)


class ConfigService:
    def __init__(
        self, reader: Reader, discovery_service: DiscoveryService, application_config: ApplicationConfig = app_config
    ) -> None:
        self._reader = reader
        self._app_config = application_config
        self._loaded_data: Dict[str, RAW_CONFIG] = {}
        self._discovery_service = discovery_service

    @property
    def app_config(self) -> ApplicationConfig:
        return self._app_config

    def _fetch(self) -> None:
        if not self._discovery_service.check():
            raise FileNotFoundError(f"Configuration folder '{self._discovery_service.root_path}' cannot be found.")

        for key, holder in self._discovery_service:
            config = self._reader(key, holder)
            self._loaded_data[config.holder_name] = config.data

    def _load(self) -> ApplicationConfig:
        self.app_config.ingest(self._loaded_data)
        return self.app_config

    def resolve(self) -> ApplicationConfig:
        self._fetch()
        return self._load()


class YamlFileConfigService(ConfigService):
    def __init__(self, root_path: pathlib.Path, application_config: ApplicationConfig = app_config) -> None:
        super().__init__(YamlReader(), FileDiscoveryService(root_path, YamlReader.suffixes), application_config)


class MemoryConfigService(ConfigService):
    def __init__(self, in_memory_config: InMemoryConfig, application_config: ApplicationConfig = app_config) -> None:
        super().__init__(MemoryReader(), MemoryDiscoveryService(in_memory_config), application_config)
