from backend.database import SessionLocal
from backend import models

db = SessionLocal()

train_12260_stops = db.query(models.Schedule).filter(models.Schedule.train_number == "12260").order_by(models.Schedule.stop_number).all()

print(f"Train 12260 has {len(train_12260_stops)} stops.")
for s in train_12260_stops:
    print(f"Station: {s.station_code}, Seq: {s.stop_number}")
