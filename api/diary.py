from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from schemas.diary import DiaryEntryResponse, DiaryEntryCreate
from db.models import User, DiaryEntry, Tag, GratitudeItem
from db.database import get_db
from core.auth import get_current_user


router = APIRouter(tags=["Diary"])

@router.post("/entries", response_model=DiaryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: DiaryEntryCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_entry = DiaryEntry(
        user_id=user.id,
        title=entry.title,
        content=entry.content,
        mood=entry.mood
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    # Add tags
    if entry.tags:
        for tag_name in entry.tags:
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            db_entry.tags.append(tag)

    # Add gratitude items
    if entry.gratitude_items:
        for content in entry.gratitude_items:
            gratitude = GratitudeItem(entry_id=db_entry.id, content=content)
            db.add(gratitude)

    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.get("/entries", response_model=List[DiaryEntryResponse])
def get_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return (
        db.query(DiaryEntry)
        .filter(DiaryEntry.user_id == user.id)
        .order_by(DiaryEntry.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/entries/{entry_id}", response_model=DiaryEntryResponse)
def read_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    entry = db.query(DiaryEntry).filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Entry not found"
        )
    return entry


@router.put("/entries/{entry_id}", response_model=DiaryEntryResponse)
def update_entry(
    entry_id: int,
    entry_update: DiaryEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_entry = db.query(DiaryEntry).filter_by(id=entry_id, user_id=user.id).first()
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Entry not found"
        )

    db_entry.title = entry_update.title
    db_entry.content = entry_update.content
    db_entry.mood = entry_update.mood

    # Update tags
    db_entry.tags.clear()
    for tag_name in entry_update.tags or []:
        tag = db.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db_entry.tags.append(tag)

    # Update gratitude items
    db.query(GratitudeItem).filter_by(entry_id=entry_id).delete()
    for content in entry_update.gratitude_items or []:
        db.add(GratitudeItem(entry_id=entry_id, content=content))

    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_entry = db.query(DiaryEntry).filter_by(id=entry_id, user_id=user.id).first()
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Entry not found"
        )

    # Delete gratitude items and tags association
    db.query(GratitudeItem).filter_by(entry_id=entry_id).delete()
    db_entry.tags.clear()

    db.delete(db_entry)
    db.commit()
    return
