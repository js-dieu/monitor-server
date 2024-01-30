import typing as t

from pydantic import BaseModel, ConfigDict


class Entity(BaseModel):
    model_config = ConfigDict(
        ser_json_timedelta='iso8601',
    )

    @classmethod
    def from_dict(cls, data: t.Dict[str, t.Any]) -> 'Entity':
        return cls.model_validate(data)

    def as_dict(self) -> t.Dict[str, t.Any]:
        return self.model_dump()
