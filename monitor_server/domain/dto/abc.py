import typing as t

from pydantic import BaseModel, ConfigDict, Field

Attrib = Field


class DTO(BaseModel):
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    def to_dict(self) -> t.Dict[str, t.Any]:
        return self.model_dump()
