from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = models.hash_password(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(db: Session, user: models.User) -> models.User:
    """Retrieve user from the database"""
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    if db_user is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

def update_user(db: Session, user: models.User, updated_data: schemas.UserCreate) -> models.User:
    """Update user"""
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    if not db_user: # Checks if db_user is none
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if updated_data.username:
        db_user.username = updated_data.username
    if updated_data.password:
        db_user.hashed_password = models.hash_password(updated_data.password)
   
    db.commit()
    db.refresh(db_user)
    
    return db_user

def delete_user(db: Session, user: models.User) -> None:
    """Delete user"""
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(db_user)
    db.commit()

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