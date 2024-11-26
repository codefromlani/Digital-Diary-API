from pydantic import BaseModel, Field
from models import MoodEnum
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=5)

class UserResponse(UserBase):
    id: int

    class Config:  
        orm_mode = True

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int

    class Config:  
        orm_mode = True


class GratitudeItemBase(BaseModel):
    content: str = Field(..., min_length=3, max_length=500)

class GratitudeItemCreate(GratitudeItemBase):
    pass 

class GratitudeItemResponse(GratitudeItemBase):
    id: int
    entry_id: int

    class Config:  
        orm_mode = True


class DiaryEntryBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=10)
    mood: Optional[MoodEnum] = None
    tags:  Optional[List[str]] = Field(default_factory=list)
    gratitude_items: Optional[List[str]] = Field(default_factory=list)

class DiaryEntryCreate(DiaryEntryBase):
    pass

class DiaryEntryResponse(DiaryEntryBase):
    id: int
    user_id: int
    created_at: datetime
    tags: List[TagResponse] = []
    gratitude_items: List[GratitudeItemResponse] = []

    class Config:  
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None