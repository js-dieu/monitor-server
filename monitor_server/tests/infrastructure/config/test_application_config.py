import pytest

from monitor_server.infrastructure.config.app import ApplicationConfig, app_config, get_app_config
from monitor_server.infrastructure.config.errors import (
    ConfigurationHolderNotFound,
    ConfigurationKeyAlreadyExists,
    ConfigurationKeyNotFound,
)
from monitor_server.tests.sdk.config.builders import (
    InMemoryConfigBuilder,
    InMemoryHolder,
    InMemoryObject,
    InMemorySection,
)


class TestApplicationConfig:
    def setup_method(self):
        self.builder = InMemoryConfigBuilder()
        self.app_config = ApplicationConfig()

    def test_that_declaring_an_object_allows_it_to_be_found_by_its_declaration(self, simple_mapping):
        self.app_config.declare_config_element(simple_mapping)
        got = self.app_config.get_specs_from_declaration(simple_mapping.declared_as)
        assert issubclass(got, simple_mapping)

    def test_that_declaring_the_same_config_twice_raises_a_configuration_key_already_exists(self, simple_mapping):
        self.app_config.declare_config_element(simple_mapping)
        with pytest.raises(
            ConfigurationKeyAlreadyExists, match=f'The key "{simple_mapping.declared_as}" already exists.'
        ):
            self.app_config.declare_config_element(simple_mapping)

    def test_it_raises_configuration_key_not_found_when_a_non_registered_object_is_passed_for_fetching_specs(self):
        with pytest.raises(ConfigurationKeyNotFound):
            assert None is self.app_config.get_specs_from_declaration('simple_mapping')

    def test_it_returns_none_when_queried_object_is_not_found(self, simple_mapping):
        assert self.app_config[simple_mapping] is None

    def test_it_can_resolve_a_simple_mapping_mapped_object(self, simple_mapping):
        self.app_config.declare_config_element(simple_mapping)
        memory_config = self.builder.with_holder(
            InMemoryHolder('main').with_object(
                InMemoryObject(simple_mapping.declared_as).with_values(name='name', label='label', value=3.14, age=50)
            )
        ).build()
        self.app_config.ingest(memory_config['main'])
        assert self.app_config[simple_mapping] == simple_mapping(name='name', label='label', value=3.14, age=50)

    def test_it_can_resolve_a_compound_object(self, composite_mapping, simple_mapping):
        self.app_config.declare_config_element(composite_mapping)
        memory_config = self.builder.with_holder(
            InMemoryHolder('main').with_object(
                InMemoryObject(composite_mapping.declared_as).with_value(
                    simple_mapping.declared_as, {'name': 'name', 'label': 'label', 'value': 3.14, 'age': 50}
                )
            )
        ).build()
        self.app_config.ingest(memory_config['main'])
        assert self.app_config[composite_mapping] == composite_mapping(
            name='composite_name', simple=simple_mapping(name='name', label='label', value=3.14, age=50)
        )

    def test_it_can_resolve_a_compound_object_with_referenced_model_in_a_section(
        self, composite_mapping, simple_mapping
    ):
        self.app_config.declare_config_element(composite_mapping)
        memory_config = (
            self.builder.with_holder(
                second_holder := InMemoryHolder('second').with_section(
                    InMemorySection('definitions').with_object(
                        simple := InMemoryObject(simple_mapping.declared_as).with_values(
                            name='name', label='label', value=3.14, age=50
                        )
                    )
                )
            )
            .with_holder(
                InMemoryHolder('main').with_object(
                    InMemoryObject(composite_mapping.declared_as)
                    .with_ref(second_holder.compute_object_ref_for(simple))
                    .with_value('name', 'Compound')
                )
            )
            .build()
        )
        self.app_config.ingest(memory_config.data())
        assert self.app_config[composite_mapping] == composite_mapping(
            name='Compound', simple=simple_mapping(name='name', label='label', value=3.14, age=50)
        )

    def test_it_can_resolve_a_compound_object_with_referenced_model_under_root(self, composite_mapping, simple_mapping):
        self.app_config.declare_config_element(composite_mapping)
        memory_config = (
            self.builder.with_holder(
                second_holder := InMemoryHolder('second').with_object(
                    simple := InMemoryObject(simple_mapping.declared_as).with_values(
                        name='name', label='label', value=3.14, age=50
                    )
                )
            )
            .with_holder(
                InMemoryHolder('main').with_object(
                    InMemoryObject(composite_mapping.declared_as)
                    .with_ref(second_holder.compute_object_ref_for(simple))
                    .with_value('name', 'Compound')
                )
            )
            .build()
        )
        self.app_config.ingest(memory_config.data())
        assert self.app_config[composite_mapping] == composite_mapping(
            name='Compound', simple=simple_mapping(name='name', label='label', value=3.14, age=50)
        )

    def test_it_raises_configuration_holder_not_found_when_a_compound_object_references_an_unknown_object(
        self, composite_mapping, simple_mapping
    ):
        self.app_config.declare_config_element(composite_mapping)
        memory_config = (
            self.builder.with_holder(
                InMemoryHolder('second').with_object(
                    InMemoryObject(simple_mapping.declared_as).with_values(
                        name='name', label='label', value=3.14, age=50
                    )
                )
            )
            .with_holder(
                InMemoryHolder('main').with_object(
                    InMemoryObject(composite_mapping.declared_as)
                    .with_ref('some.unknown.path')
                    .with_value('name', 'Compound')
                )
            )
            .build()
        )
        with pytest.raises(ConfigurationHolderNotFound, match="This .ref references an unknown holder: 'some'"):
            self.app_config.ingest(memory_config.data())

    def test_it_can_map_a_pydantic_model_with_configuration_bases_members(
        self, app_test_config, composite_no_ref_mapping, simple_mapping
    ):
        self.app_config.declare(app_test_config)

        main_holder = InMemoryHolder('main').with_object(
            InMemoryObject(simple_mapping.declared_as).with_values(name='name', label='label', value=3.14, age=50)
        )
        second_holder = InMemoryHolder('second').with_object(
            InMemoryObject(composite_no_ref_mapping.declared_as)
            .with_values(name='name', label='label')
            .with_values(extras={'value': 3.14, 'age': 50})
        )

        memory_config = self.builder.with_holder(main_holder).with_holder(second_holder).build()
        self.app_config.ingest(memory_config.data())
        assert self.app_config.map_to(app_test_config) == app_test_config(
            simple=simple_mapping(name='name', label='label', value=3.14, age=50),
            composite_no_ref=composite_no_ref_mapping(name='name', label='label', extras={'value': 3.14, 'age': 50}),
        )


class TestDefaultApplicationConfig:
    def test_it_always_bring_the_same_object(self):
        assert get_app_config() == app_config
