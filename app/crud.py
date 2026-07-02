from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models

RECENT_STORY_WINDOW = timedelta(days=3)


def get_articles(db: Session, query: str | None = None) -> list[models.Article]:
    q = db.query(models.Article)
    if query is not None:
        q = q.filter(models.Article.query.ilike(f"%{query}%"))
    return q.order_by(models.Article.published_at.desc()).all()


def get_article(db: Session, article_id: int) -> models.Article | None:
    return db.query(models.Article).filter(models.Article.id == article_id).first()


def get_article_by_url(db: Session, url: str) -> models.Article | None:
    return db.query(models.Article).filter(models.Article.url == url).first()


def create_article(db: Session, article_data: dict) -> models.Article:
    db_article = models.Article(**article_data)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def save_summary(db: Session, article_id: int, summary: str) -> models.Article | None:
    db_article = get_article(db, article_id)
    if db_article is None:
        return None
    db_article.summary = summary
    db.commit()
    db.refresh(db_article)
    return db_article


def save_embedding(db: Session, article_id: int, embedding: list[float]) -> models.Article | None:
    db_article = get_article(db, article_id)
    if db_article is None:
        return None
    db_article.embedding = embedding
    db.commit()
    db.refresh(db_article)
    return db_article


def get_recent_story_candidates(
    db: Session, query: str, since: datetime
) -> list[tuple[int, list[float]]]:
    """One representative embedding per recent story for this query, for clustering."""
    articles = (
        db.query(models.Article)
        .filter(
            models.Article.query == query,
            models.Article.story_id.isnot(None),
            models.Article.embedding.isnot(None),
            models.Article.published_at >= since,
        )
        .all()
    )
    seen_stories: dict[int, list[float]] = {}
    for article in articles:
        seen_stories.setdefault(article.story_id, list(article.embedding))
    return list(seen_stories.items())


def create_story(db: Session, title: str, query: str) -> models.Story:
    story = models.Story(title=title, query=query)
    db.add(story)
    db.commit()
    db.refresh(story)
    return story


def attach_article_to_story(db: Session, article_id: int, story_id: int) -> models.Article | None:
    db_article = get_article(db, article_id)
    if db_article is None:
        return None
    db_article.story_id = story_id
    db.commit()
    db.refresh(db_article)
    return db_article


def update_story_summary(db: Session, story_id: int, summary: str) -> models.Story | None:
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story is None:
        return None
    story.summary = summary
    db.commit()
    db.refresh(story)
    return story


def get_stories(db: Session, query: str | None = None) -> list[models.Story]:
    q = db.query(models.Story)
    if query is not None:
        q = q.filter(models.Story.query.ilike(f"%{query}%"))
    return q.order_by(models.Story.created_at.desc()).all()


def get_story(db: Session, story_id: int) -> models.Story | None:
    return db.query(models.Story).filter(models.Story.id == story_id).first()
