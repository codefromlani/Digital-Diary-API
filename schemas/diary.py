from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

from db.models import MoodEnum


class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class GratitudeItemBase(BaseModel):
    content: str 

class GratitudeItemCreate(GratitudeItemBase):
    pass 

class GratitudeItemResponse(GratitudeItemBase):
    id: int
    entry_id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class DiaryEntryBase(BaseModel):
    title: str 
    content: str 
    mood: Optional[MoodEnum] = None
    tags:  Optional[List[str]] 
    gratitude_items: Optional[List[str]] 

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
