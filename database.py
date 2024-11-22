from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv()

engine = create_engine(DATABASE_URL, echo=True)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base

def get_db():
    db = Sessionlocal
    try:
        yield db
    finally:
        db.close()