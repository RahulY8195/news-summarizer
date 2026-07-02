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


class StoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    query: str
    summary: str | None
    created_at: datetime_type


class StoryDetail(StoryOut):
    articles: list[ArticleOut]


class TopicSummaryOut(BaseModel):
    topic: str
    fetched: int
    new: int
    articles: list[ArticleOut]
