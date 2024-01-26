import datetime
from typing import Any

from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.dialects.mysql import DATETIME


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
