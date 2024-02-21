import typing as t
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

Attribute = Field


class Model(BaseModel):
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    def to_dict(self) -> t.Dict[str, t.Any]:
        return self.model_dump()


class PageableRequest(Model):
    page_no: int = Field(default=0)
    page_size: int = Field(default=0)

    @property
    def with_pagination(self) -> bool:
        return self.page_size > 0


class Entity(Model):
    uid: UUID = Field(default_factory=uuid4)

    @classmethod
    def from_dict(cls, data: t.Dict[str, t.Any]) -> 'Entity':
        return cls.model_validate(data)
