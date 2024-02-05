import datetime
import uuid
from typing import Any

from sqlalchemy import CHAR, DateTime, TypeDecorator
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.dialects.postgresql import UUID


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime.datetime | None, dialect: Any) -> datetime.datetime | None:
        if value is not None:
            if not value.tzinfo:
                raise TypeError('Time Zone information is required')
            value = value.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value: datetime.datetime | None, dialect: Any) -> datetime.datetime | None:
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == 'mysql':
            return dialect.type_descriptor(DATETIME())
        return dialect.type_descriptor(self._default_type)


class GUID(TypeDecorator):
    cache_ok = False
    impl = CHAR

    _default_type = CHAR(32)

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(self._default_type)

    def process_bind_param(self, value: uuid.UUID | str | None, dialect: Any) -> str | None:
        if value is None:
            return value
        return value if isinstance(value, str) else value.hex

    def process_result_value(self, value: str | None, dialect: Any) -> uuid.UUID | None:
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value
