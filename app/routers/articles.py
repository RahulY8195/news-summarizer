from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import clustering, crud, embeddings, news_client, schemas, summarizer
from app.auth import require_api_key
from app.crud import RECENT_STORY_WINDOW
from app.database import get_db

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post(
    "/fetch",
    dependencies=[Depends(require_api_key)],
    response_model=schemas.TopicSummaryOut,
)
def fetch_and_summarize(query: str = "technology", db: Session = Depends(get_db)):
    fetched = news_client.fetch_articles(query=query)
    created = []
    for item in fetched:
        if crud.get_article_by_url(db, item["url"]) is not None:
            continue
        item["query"] = query
        article = crud.create_article(db, item)

        embedding = embeddings.get_embedding(article.content)
        crud.save_embedding(db, article.id, embedding)

        since = datetime.now(timezone.utc) - RECENT_STORY_WINDOW
        candidates = crud.get_recent_story_candidates(db, query, since)
        story_id = clustering.find_matching_story(embedding, candidates)

        if story_id is None:
            story = crud.create_story(db, title=article.title, query=query)
            story_id = story.id

        crud.attach_article_to_story(db, article.id, story_id)

        summary = summarizer.summarize(article.content)
        article = crud.save_summary(db, article.id, summary)

        story = crud.get_story(db, story_id)
        story_summary = summarizer.summarize_story(
            texts=[a.content for a in story.articles],
            sources=[a.source for a in story.articles],
        )
        crud.update_story_summary(db, story_id, story_summary)

        created.append(article)

    articles = crud.get_articles(db, query=query)
    return {
        "topic": query,
        "fetched": len(fetched),
        "new": len(created),
        "articles": articles,
    }


@router.get("/", response_model=list[schemas.ArticleOut])
def list_articles(query: str | None = None, db: Session = Depends(get_db)):
    return crud.get_articles(db, query=query)


@router.get("/{article_id}", response_model=schemas.ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
