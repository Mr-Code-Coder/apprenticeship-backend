from contextlib import asynccontextmanager
import threading
from fastapi import FastAPI, Depends
from sqlmodel import Session, func, select
from typing import List
from database import create_db_and_tables, engine, Entry
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ucas_scaper import scrape

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure tables exist
    create_db_and_tables()
    
    # 2. Check if DB is empty
    with Session(engine) as session:
        count = session.exec(select(func.count(Entry.id))).one()
        
        if count == 0:
            print("Database empty! Starting initial scrape in background...")
            # Run in a separate thread so the API doesn't "freeze" while scraping
            thread = threading.Thread(target=scrape)
            thread.start()
        else:
            print(f"Database contains {count} records. Skipping initial scrape.")
    
    yield 

app = FastAPI(lifespan=lifespan, title="Apprenticeship API")

origins = [
    "http://localhost:5173",
    "localhost:5173",
    "https://mr-code-coder.github.io/apprenticeship-tracker-and-site/"
    "https://mr-code-coder.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get('/')
def root():
    return {"message" : "The API is live"}

# Gets the session safely by using "with"
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/jobs", response_model=List[Entry]) # response_model means when using react I can know what to expect as the data output
def get_all_jobs(session: Session = Depends(get_session)): # safely open a session
    statement = select(Entry).order_by(Entry.apply_date)
    results = session.exec(statement).all()
    return results


if __name__ == "__main__":
    uvicorn.run("main:app", host="https://apprenticeship-backend.onrender.com", port=8000, reload=True)