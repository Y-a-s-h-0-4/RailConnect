from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas

def resolve_station_code(db: Session, search_term: str):
    if not search_term: return None
    search_term = search_term.strip()
    station = db.query(models.Station).filter(
        or_(
            models.Station.code.ilike(search_term),
            models.Station.name.ilike(f"%{search_term}%"),
            models.Station.city.ilike(f"%{search_term}%")
        )
    ).first()
    return station.code if station else None

def get_station(db: Session, code: str):
    return db.query(models.Station).filter(models.Station.code == code).first()

def get_stations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Station).offset(skip).limit(limit).all()

def get_train(db: Session, train_number: str):
    return db.query(models.Train).filter(models.Train.train_number == train_number).first()

def get_schedules_by_station(db: Session, station_code: str):
    return db.query(models.Schedule).filter(models.Schedule.station_code == station_code).all()

def get_schedules_by_train(db: Session, train_number: str):
    return db.query(models.Schedule).filter(models.Schedule.train_number == train_number).order_by(models.Schedule.stop_number).all()
