import typing as t

from pydantic import BaseModel, ConfigDict, Field

Attribute = Field


class DTO(BaseModel):
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    def to_dict(self) -> t.Dict[str, t.Any]:
        return self.model_dump()


class PageableRequest(DTO):
    page_no: int = Field(default=0)
    page_size: int = Field(default=0)

    @property
    def with_pagination(self) -> bool:
        return self.page_size > 0
