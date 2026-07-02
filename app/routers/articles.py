from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, news_client, schemas, summarizer
from app.database import get_db

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/fetch")
def fetch_and_summarize(query: str = "technology", db: Session = Depends(get_db)):
    fetched = news_client.fetch_articles(query=query)
    created = []
    for item in fetched:
        if crud.get_article_by_url(db, item["url"]) is not None:
            continue
        item["query"] = query
        article = crud.create_article(db, item)
        summary = summarizer.summarize(article.content)
        article = crud.save_summary(db, article.id, summary)
        created.append(article)
    return {"fetched": len(fetched), "new": len(created)}


@router.get("/", response_model=list[schemas.ArticleOut])
def list_articles(query: str | None = None, db: Session = Depends(get_db)):
    return crud.get_articles(db, query=query)


@router.get("/{article_id}", response_model=schemas.ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
