from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
import enum
from database import Base
from passlib.context import CryptContext
from datetime import datetime
from sqlalchemy.orm import relationship


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class MoodEnum(enum.Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  

    # one-to-many relationship
    entries = relationship("DiaryEntry", back_populates="user")

def hash_password(plain_password: str) -> str:
    """Generate a hashed password using bcrypt"""
    return pwd_context.hash(plain_password)  

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if the plain password matches the hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


class DiaryEntry(Base):
    __tablename__ ="diary_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    mood = Column(Enum(MoodEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

   # Relationships
    user = relationship("User", back_populates="entries")
    tags = relationship("Tag", secondary="entry_tags", back_populates="entries")
    gratitude_items = relationship("GratitudeItem", back_populates="entry")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Many-to many relationship with entries
    entries = relationship("DiaryEntry", secondary="entry_tags", back_populates="tags")


class EntryTag(Base):
    __tablename__ = "entry_tags"
    entry_id = Column(Integer, ForeignKey("diary_entries.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class GratitudeItem(Base):
    __tablename__ = "gratitude_items"
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("diary_entries.id"))
    content = Column(Text, nullable=False)

    # Relationship to entry
    entry = relationship("DiaryEntry", back_populates="gratitude_items")