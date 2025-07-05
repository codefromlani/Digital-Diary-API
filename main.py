from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from db.database import get_db, engine, Base
from api.user import router as user_router
from api.diary import router as diary_rouer
from schemas.user import Token
from core.auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Diary API",
    description="A simple API for managing your digital diary entries with mood tracking and gratitude lists"
)

app.include_router(user_router, prefix="/api")
app.include_router(diary_rouer, prefix="/api")

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint to get access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

