from typing import Any, Callable, Dict, Mapping, Self, Type, TypeVar, cast

from pydantic import BaseModel

from monitor_server.infrastructure.config.base import RAW_CONFIG, ConfigurationBase
from monitor_server.infrastructure.config.errors import (
    ConfigurationError,
    ConfigurationHolderNotFound,
    ConfigurationKeyAlreadyExists,
    ConfigurationKeyNotFound,
    ConfigurationRefUnsolvable,
)

ConfigurationModel = TypeVar('ConfigurationModel', bound=ConfigurationBase)
ConfigurationMapping = TypeVar('ConfigurationMapping', bound=BaseModel)


def _solve_path(mapping: Mapping, path: str, default: Any = None) -> Any:
    this_mapping = mapping
    path_elements = path.split('.')
    for element in path_elements[:-1]:
        if element in this_mapping:
            this_mapping = this_mapping[element]
        else:
            return default
    return this_mapping.get(path_elements[-1], default)


class ApplicationConfig:
    def __init__(self, *declares: Type[BaseModel]) -> None:
        self._parts: Dict[str, ConfigurationBase] = {}
        self._views: Dict[str, ConfigurationBase.ConfigKey] = {}
        for base_model in declares:
            self.declare(base_model)

    def declare(self, application_config: Type[BaseModel]) -> None:
        def get_config_key_from_model(model: Any) -> ConfigurationBase.ConfigKey | None:
            if model is None or model.annotation is None:
                return None
            if issubclass(model.annotation, (ConfigurationBase,)):
                return model.annotation.config_key()
            return None

        for config_part_model in application_config.model_fields.values():
            if (config_key := get_config_key_from_model(config_part_model)) is not None:
                if config_key.name in self._views:
                    raise ConfigurationKeyAlreadyExists(f'The key "{config_key.name}" already exists.')
                self._views[config_key.name] = config_key

    def get_specs_from_declaration(self, declared_as: str) -> Type[ConfigurationBase]:
        try:
            return self._views[declared_as].model
        except KeyError as e:
            raise ConfigurationKeyNotFound(str(e)) from e

    def __resolve_reference(self, data: Dict[str, Any], view: Dict[str, Any]) -> Dict[str, Any]:
        if '.ref' in view:
            holder, path = view['.ref'].split('.', 1)
            try:
                referenced = data[holder]
            except KeyError as e:
                raise ConfigurationHolderNotFound(f'This .ref references an unknown holder: {e}') from e
            index = 0
            path_elements = path.split('.')
            if not path_elements:
                raise ConfigurationRefUnsolvable(f'This .ref cannot be resolved: {view['.ref']} due to incomplete path')
            if len(path_elements) == 1:
                try:
                    referenced = referenced[path]
                except KeyError as e:
                    raise ConfigurationRefUnsolvable(
                        f'This .ref cannot be resolved: {view['.ref']} (while resolving {e} '
                        f'at path position {index})'
                    ) from e
                del view['.ref']
                view.update({path: self.__resolve_reference(data, referenced)})
            else:
                try:
                    for sub_path in path.split('.')[:-1]:
                        referenced = referenced[sub_path]
                        index += 1
                except KeyError as e:
                    raise ConfigurationRefUnsolvable(
                        f'This .ref cannot be resolved: {view['.ref']} (while resolving {e} '
                        f'at path position {index})'
                    ) from e
                del view['.ref']
                view.update(self.__resolve_reference(data, referenced))
        # Time to check for inner referenced models
        for sub_key, sub_element in view.items():
            if isinstance(sub_element, dict):
                view[sub_key] = self.__resolve_reference(data, sub_element)
        return view

    def declare_config_element(self, config_part: Type[ConfigurationBase]) -> Self:
        if config_part.declared_as in self._views:
            raise ConfigurationKeyAlreadyExists(f'The key "{config_part.declared_as}" already exists.')
        self._views[config_part.declared_as] = config_part.config_key()
        return self

    def ingest(self, data: Dict[str, RAW_CONFIG]) -> None:
        for view_name, view_spec in self._views.items():
            views = view_name.split('.')
            for config in filter(lambda d: views[0] in d, data.values()):
                view = _solve_path(config, view_name)
                if view is not None:
                    final_view = self.__resolve_reference(data, view)
                    self._parts[view_name] = view_spec.model.model_validate(final_view)

    def __getitem__(self, item_model: Type[ConfigurationModel]) -> ConfigurationModel:
        return cast(ConfigurationModel, self._parts.get(item_model.config_key().name))

    def map_to(self, model: Type[ConfigurationMapping]) -> ConfigurationMapping:
        data = {}
        for config_name, config_model in model.model_fields.items():
            if config_model.annotation and issubclass(config_model.annotation, (ConfigurationBase,)):
                element = self._parts.get(config_model.annotation.config_key().name)
                if not element:
                    raise ConfigurationError(
                        f'Unable to map configuration:'
                        f' configuration object {config_model.annotation.config_key().name} cannot be found'
                    )
                data[config_name] = element.model_dump()
        return model(**data)


def _initiate_app_config() -> Callable[[], ApplicationConfig]:
    a_config = ApplicationConfig()

    def _an_app_config() -> ApplicationConfig:
        return a_config

    return _an_app_config


get_app_config = _initiate_app_config()
app_config = get_app_config()
