import datetime
import uuid
from typing import ClassVar, Mapping

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, declared_attr

from monitor_server.infrastructure.orm.custom_types import GUID, TZDateTime


class ORMModel(MappedAsDataclass, DeclarativeBase):
    type_annotation_map: ClassVar[Mapping] = {datetime.datetime: TZDateTime, uuid.UUID: GUID}

    __allow_unmapped__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        return cls.__name__
