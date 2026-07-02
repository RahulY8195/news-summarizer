from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


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
