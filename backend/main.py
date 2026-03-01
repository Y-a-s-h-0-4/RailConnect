import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, Base, SessionLocal
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rail Connect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Rail Connect API"}

@app.get("/api/stations", response_model=list[schemas.Station])
def read_stations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stations = crud.get_stations(db, skip=skip, limit=limit)
    return stations

@app.get("/api/routes")
def get_routes(source: str, destination: str, date: str, criteria: str = "fastest", switches: str = "0,1", db: Session = Depends(get_db)):
    import graph
    routes = graph.find_routes(db, source=source, destination=destination, date_str=date, criteria=criteria, switches=switches)
    return {"routes": routes}
