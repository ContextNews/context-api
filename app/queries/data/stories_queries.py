from context_db.models import Story, StoryIndicator
from sqlalchemy.orm import Session


def query_story_exists(db: Session, story_id: str) -> bool:
    return db.query(Story.id).filter(Story.id == story_id).first() is not None


def query_indicator_ids_for_story(db: Session, story_id: str) -> list[str]:
    rows = (
        db.query(StoryIndicator.indicator_id)
        .filter(StoryIndicator.story_id == story_id)
        .all()
    )
    return [r.indicator_id for r in rows]
