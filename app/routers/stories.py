from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/", response_model=list[schemas.StoryOut])
def list_stories(query: str | None = None, db: Session = Depends(get_db)):
    return crud.get_stories(db, query=query)


@router.get("/{story_id}", response_model=schemas.StoryDetail)
def get_story(story_id: int, db: Session = Depends(get_db)):
    story = crud.get_story(db, story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story
