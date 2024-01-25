from typing import Type

import pytest
from pydantic import BaseModel

from monitor_server.infrastructure.config import ConfigurationBase


class Simple(ConfigurationBase, declared_as='simple'):
    name: str
    label: str
    value: float
    age: int


class Composite(ConfigurationBase, declared_as='composite'):
    name: str = 'composite_name'
    simple: Simple


class Extras(BaseModel):
    value: float
    age: int


class CompositeNoRef(ConfigurationBase, declared_as='composite'):
    name: str
    label: str
    extras: Extras


class AppTestConfig(BaseModel):
    simple: Simple
    composite_no_ref: CompositeNoRef


@pytest.fixture()
def simple_mapping() -> Type[Simple]:
    return Simple


@pytest.fixture()
def composite_mapping() -> Type[Composite]:
    return Composite


@pytest.fixture()
def composite_no_ref_mapping() -> Type[CompositeNoRef]:
    return CompositeNoRef


@pytest.fixture()
def app_test_config() -> Type[AppTestConfig]:
    return AppTestConfig
