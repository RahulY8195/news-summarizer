from fastapi import FastAPI
from sqlalchemy import text

from app.database import Base, engine
from app.routers import articles, stories

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="News Summarizer API")

app.include_router(articles.router)
app.include_router(stories.router)


@app.get("/")
def root():
    return {"message": "News Summarizer API is running"}
