from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = models.hash_password(user.password)
    user_to_create = models.User(username=user.username, hashed_password=hashed_password)
    db.add(user_to_create)
    db.commit()
    db.refresh(user_to_create)
    return user_to_create

def create_diary_entry(db: Session, entry: schemas.DiaryEntryCreate, user_id: int) -> models.DiaryEntry:
    """Create a new diary entry"""
    db_entry = models.DiaryEntry(
        user_id=user_id,
        title=entry.title,
        content=entry.content,
        mood=entry.mood
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)