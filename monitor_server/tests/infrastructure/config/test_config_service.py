import yaml

from monitor_server.infrastructure.config.app import ApplicationConfig
from monitor_server.infrastructure.config.loader import (
    FileDiscoveryService,
    MemoryDiscoveryService,
    MemoryReader,
    YamlReader,
)
from monitor_server.infrastructure.config.service import ConfigService
from monitor_server.tests.sdk.config.builders import (
    InMemoryConfigBuilder,
    InMemoryHolder,
    InMemoryObject,
    InMemorySection,
)


class TestConfigService:
    def setup_method(self):
        self.builder = InMemoryConfigBuilder()
        self.simple_object = InMemoryObject('simple').with_values(name='name', label='label', value=3.14, age=50)
        self.global_holder = InMemoryHolder('global').with_section(
            InMemorySection('definitions').with_object(self.simple_object)
        )
        self.compound_object = (
            InMemoryObject('composite')
            .with_ref(self.global_holder.compute_object_ref_for(self.simple_object))
            .with_value('name', 'Composite')
        )

        self.main_holder = InMemoryHolder('main').with_object(self.compound_object)
        self.builder.with_holder(self.global_holder).with_holder(self.main_holder)
        self.app_config = ApplicationConfig()

    def test_it_loads_from_yaml_files(self, tmp_path, simple_mapping, composite_mapping):
        # We dump the data in yaml format
        for holder in (self.global_holder, self.main_holder):
            yaml_file_path = tmp_path / f'{holder.name}.{YamlReader.suffixes}'
            yaml_file_path.write_text(yaml.dump(holder.build()))

        self.app_config.declare_config_element(simple_mapping).declare_config_element(composite_mapping)

        config = ConfigService(YamlReader(), FileDiscoveryService(tmp_path, YamlReader.suffixes), self.app_config)
        config.resolve()

        assert config.app_config[composite_mapping] == composite_mapping(
            name='Composite', simple=simple_mapping(name='name', label='label', value=3.14, age=50)
        )

    def test_it_loads_from_memory(self, tmp_path, composite_mapping, simple_mapping):
        self.app_config.declare_config_element(simple_mapping).declare_config_element(composite_mapping)
        config = ConfigService(MemoryReader(), MemoryDiscoveryService(self.builder.build()), self.app_config)
        config.resolve()

        assert config.app_config[composite_mapping] == composite_mapping(
            name='Composite', simple=simple_mapping(name='name', label='label', value=3.14, age=50)
        )
