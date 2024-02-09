from pydantic import BaseModel, ConfigDict, Field


class PageableStatement(BaseModel):
    model_config = ConfigDict(frozen=True)

    page_no: int = Field(ge=0)
    page_size: int = Field(gt=0)

    @property
    def offset(self) -> int:
        return self.page_size * self.page_no

    @property
    def next_page(self) -> 'PageableStatement':
        return PageableStatement(page_no=self.page_no + 1, page_size=self.page_size)
