from __future__ import annotations
from backend.database import SessionLocal
from backend import models, crud, graph
import json

db = SessionLocal()

ndls = crud.resolve_station_code(db, "NDLS")
bct = crud.resolve_station_code(db, "BCT")

print(f"Resolved NDLS: {ndls}")
print(f"Resolved BCT: {bct}")

ndls_schedules = db.query(models.Schedule).filter(models.Schedule.station_code == ndls).limit(5).all()
print("\nSample NDLS schedules:")
for s in ndls_schedules:
    print(f"Train {s.train_number}, arr: {s.arrival_time}, dep: {s.departure_time}, day: {s.day_count}, seq: {s.stop_number}")

routes = graph.find_routes(db, "NDLS", "BCT")
print(f"\nFound {len(routes)} routes")
if routes:
    print(json.dumps(routes[0], indent=2))
