from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from typing import List
from database import engine, Entry
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Apprenticeship API")

origins = [
    "http://localhost:5173",
    "localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allow all websites (fine for a local project)
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