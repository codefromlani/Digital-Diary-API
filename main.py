from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db, engine
from datetime import timedelta
from typing import List
import models
import schemas
import auth
import crud


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Diary API",
    description="A simple API for managing your digital diary entries with mood tracking and gratitude lists"
)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint to get access token"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    return crud.create_user(db=db, user=user)
    

@app.get("/users/me", response_model=schemas.UserResponse)
def get_user_by_me(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
    ):
    """Get the authenticated user's profile"""
    return crud.get_user(db=db, user=user)

@app.put("/users/me", response_model=schemas.UserResponse)
def update_user(
    updated_data: schemas.UserCreate, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(auth.get_current_user)
    ):
    """Update current authenticated user's data"""
    return crud.update_user(db=db, user=user, updated_data=updated_data)

@app.delete("/users/me", response_model=schemas.UserResponse)
def delete_user(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)  
):
    """Delete current authenticated user"""
    crud.delete_user(db=db, user=user)
    return {"detail": "User deleted successfully"}

@app.post("/entries/", response_model=schemas.DiaryEntryResponse)
def create_entry(
    entry: schemas.DiaryEntryCreate, 
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
    ):
    """Create a new diary entry"""
    return crud.create_diary_entry(entry=entry, db=db, user=user)

@app.get("/entries/", response_model=List[schemas.DiaryEntryResponse])
def get_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    """Get all diary entries for the current user"""
    entries = crud.get_diary_entries(db=db, user=user, skip=skip, limit=limit)
    return entries

@app.get("/entry/{entry_id}", response_model=schemas.DiaryEntryResponse)
def read_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    """Get a specific diary entry"""
    entry = crud.get_entry_diary(db=db, entry=entry_id, user=user)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry no found")
    return entry