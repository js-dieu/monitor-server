from monitor_server.infrastructure.config.loader import FileDiscoveryService, MemoryDiscoveryService
from monitor_server.tests.sdk.config.builders import (
    InMemoryConfig,
    InMemoryConfigBuilder,
    InMemoryHolder,
    InMemoryObject,
    InMemorySection,
)


class TestFileDiscovery:
    def test_it_does_not_consider_a_file_on_an_empty_directory(self, tmp_path) -> None:
        fds = FileDiscoveryService(tmp_path, '.some')
        assert not list(fds)

    def test_it_does_not_consider_a_file_on_a_dir_with_no_matching_entry(self, tmp_path):
        for suffix in ['it', 'en', 'fr', 'es', 'de', 'uk']:
            p = tmp_path / f'test.{suffix}'
            p.touch()
        assert not list(FileDiscoveryService(tmp_path, 'some'))

    def test_it_does_not_consider_files_with_a_different_extension(self, tmp_path):
        for suffix in ['it', 'en', 'fr', 'es', 'some', 'de', 'uk']:
            p = tmp_path / f'test.{suffix}'
            p.touch()
        assert list(FileDiscoveryService(tmp_path, 'some')) == [('test', (tmp_path / 'test.some'))]

    def test_it_does_not_consider_symlink_even_when_matching_suffix(self, tmp_path):
        for suffix in ['it', 'en', 'fr', 'es', 'de', 'uk']:
            p = tmp_path / f'test.{suffix}'
            p.touch()
        p = tmp_path / 'test.some'
        p.symlink_to(tmp_path / 'test.fr')
        assert not list(FileDiscoveryService(tmp_path, 'some'))


class TestMemoryDiscovery:
    def setup_method(self):
        self.memory_config = (
            InMemoryConfigBuilder()
            .with_holder(
                second_holder := InMemoryHolder('second').with_section(
                    InMemorySection('definitions').with_object(
                        simple := InMemoryObject('simple').with_values(name='name', label='label', value=3.14, age=50)
                    )
                )
            )
            .with_holder(
                InMemoryHolder('main').with_object(
                    InMemoryObject('compound')
                    .with_ref(second_holder.compute_object_ref_for(simple))
                    .with_value('name', 'Compound')
                )
            )
            .build()
        )

    def test_it_lists_all_known_holders(self):
        mds = MemoryDiscoveryService(self.memory_config)
        assert sorted(element[0] for element in mds) == ['main', 'second']

    def test_it_returns_an_empty_list_for_an_empty_memory_config(self):
        mds = MemoryDiscoveryService(InMemoryConfig(config={}))
        assert not list(mds)
