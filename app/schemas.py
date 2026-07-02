from datetime import datetime as datetime_type

from pydantic import BaseModel, ConfigDict


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str
    url: str
    published_at: datetime_type | None
    summary: str | None
    query: str


class ArticleDetail(ArticleOut):
    content: str
