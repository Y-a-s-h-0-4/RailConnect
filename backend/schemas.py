from pydantic import BaseModel
from typing import List, Optional

class StationBase(BaseModel):
    code: str
    name: str
    city: Optional[str] = None

class Station(StationBase):
    class Config:
        from_attributes = True

class TrainBase(BaseModel):
    train_number: str
    train_name: str

class Train(TrainBase):
    class Config:
        from_attributes = True

class ScheduleBase(BaseModel):
    train_number: str
    station_code: str
    arrival_time: str
    departure_time: str
    day_count: int
    distance: float
    stop_number: int

class Schedule(ScheduleBase):
    id: int

    class Config:
        from_attributes = True

class RouteQuery(BaseModel):
    source: str
    destination: str
    date: str
    criteria: str = "fastest" # can be 'fastest', 'cheapest', 'fewest_switches'
