from datetime import datetime, date
import os
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

## Database handler
# Defining Table

class Entry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: str
    employer: str
    location: str
    apply_date: date
    start_date: date

# Database file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sqlite_file_name = os.path.join(BASE_DIR, "database.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

# The engine

engine = create_engine(sqlite_url, echo=True) # echo true shows sql in the terminal

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)