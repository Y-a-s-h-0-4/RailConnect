from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Station(Base):
    __tablename__ = "stations"
    code = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    city = Column(String, index=True, nullable=True)

class Train(Base):
    __tablename__ = "trains"
    train_number = Column(String, primary_key=True, index=True)
    train_name = Column(String, index=True)

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String, ForeignKey("trains.train_number"))
    station_code = Column(String, ForeignKey("stations.code"))
    arrival_time = Column(String)  # format: "HH:MM", "None" for source
    departure_time = Column(String) # format: "HH:MM", "None" for destination
    day_count = Column(Integer)  # 1 for first day, 2 for next, etc.
    distance = Column(Float)
    stop_number = Column(Integer)

    train = relationship("Train")
    station = relationship("Station")
