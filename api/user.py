from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.user import UserResponse, UserCreate
from db.models import User, hash_password
from db.database import get_db
from core.auth import get_current_user


router = APIRouter(tags=["User"])

@router.post("/register", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = hash_password(user_data.password)
    new_user =User(username=user_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=UserResponse)
def get_user(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if db_user is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.put("/users", response_model=UserResponse)
def update_user(updated_data: UserCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
   
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if updated_data.username:
        db_user.username = updated_data.username
    if updated_data.password:
        db_user.hashed_password = hash_password(updated_data.password)
   
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.delete("/users", response_model=UserResponse)
def delete_user(db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    db_user = db.query(User).filter(User.id == user.id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(db_user)
    db.commit()

    return {"detail": "User deleted successfully"}