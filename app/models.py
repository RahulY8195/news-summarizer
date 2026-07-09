from datetime import datetime as datetime_type

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

EMBEDDING_DIM = 768


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    query = Column(String, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime_type.utcnow, nullable=False)

    articles = relationship("Article", back_populates="story")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    published_at = Column(DateTime, nullable=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    query = Column(String, nullable=False, index=True)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    story_id = Column(Integer, ForeignKey("stories.id"), nullable=True, index=True)
    story = relationship("Story", back_populates="articles")
