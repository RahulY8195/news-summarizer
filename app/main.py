from fastapi import FastAPI

from app.database import Base, engine
from app.routers import articles

Base.metadata.create_all(bind=engine)

app = FastAPI(title="News Summarizer API")

app.include_router(articles.router)


@app.get("/")
def root():
    return {"message": "News Summarizer API is running"}
