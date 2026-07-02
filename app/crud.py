from sqlalchemy.orm import Session

from app import models


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
