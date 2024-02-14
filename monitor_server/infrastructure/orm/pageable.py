import typing as t

from pydantic import BaseModel, ConfigDict, Field

PAGINATION_TYPE = t.TypeVar('PAGINATION_TYPE')


class PaginatedResponse(BaseModel, t.Generic[PAGINATION_TYPE]):
    model_config = ConfigDict(frozen=True)

    page_no: int | None
    next_page: int | None = None
    data: PAGINATION_TYPE


class PageableStatement(BaseModel):
    model_config = ConfigDict(frozen=True)

    page_no: int = Field(ge=0)
    page_size: int = Field(gt=0)

    @property
    def offset(self) -> int:
        return self.page_size * self.page_no

    def build_response(self, data: PAGINATION_TYPE, elements_count: int) -> PaginatedResponse[PAGINATION_TYPE]:
        page_count = int(elements_count / self.page_size)
        # page index starts at 0
        page_count = page_count - 1 if self.page_size * page_count >= elements_count else page_count
        next_page = None if self.page_no >= page_count else self.page_no + 1
        return PaginatedResponse[PAGINATION_TYPE](data=data, page_no=self.page_no, next_page=next_page)
