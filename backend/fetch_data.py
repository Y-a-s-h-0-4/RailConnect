import urllib.request
import ssl
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models
import time

Base.metadata.create_all(bind=engine)

MAJOR_STATIONS = [
    ("NDLS", "New Delhi", "Delhi"),
    ("BCT", "Mumbai Central", "Mumbai"),
    ("MAS", "Chennai Central", "Chennai"),
    ("HWH", "Howrah", "Kolkata"),
    ("SBC", "KSR Bengaluru", "Bengaluru"),
    ("SC", "Secunderabad", "Hyderabad"),
    ("PNQ", "Pune", "Pune"),
    ("ALD", "Prayagraj", "Prayagraj"),
]

def fetch_erail_trains(src, dest):
    url = f"https://erail.in/rail/getTrains.aspx?Station_From={src}&Station_To={dest}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    context = ssl._create_unverified_context()
    try:
        response = urllib.request.urlopen(req, context=context, timeout=5)
        text = response.read().decode('utf-8')
        return text
    except Exception as e:
        print(f"Error fetching {src} to {dest}: {e}")
        return ""

def parse_and_seed():
    db = SessionLocal()

    # 1. Seed Stations
    for code, name, city in MAJOR_STATIONS:
        if not db.query(models.Station).filter_by(code=code).first():
            db.add(models.Station(code=code, name=name, city=city))
    db.commit()

    # 2. Fetch routes between all pairs
    for i in range(len(MAJOR_STATIONS)):
        for j in range(len(MAJOR_STATIONS)):
            if i == j: continue
            src = MAJOR_STATIONS[i][0]
            dest = MAJOR_STATIONS[j][0]
            
            print(f"Fetching trains {src} -> {dest}...")
            data = fetch_erail_trains(src, dest)
            if not data:
                continue
                
            trainsRaw = data.split('^')
            for tRaw in trainsRaw[1:]:  # skip first chunk before first ^
                fields = tRaw.split('~')
                if len(fields) > 12:
                    train_no = fields[0]
                    train_name = fields[1]
                    dep_time = fields[10]
                    arr_time = fields[11]
                    # basic safety
                    if dep_time == "First" or arr_time == "Last":
                        continue
                        
                    # Add Train
                    if not db.query(models.Train).filter_by(train_number=train_no).first():
                        db.add(models.Train(train_number=train_no, train_name=train_name))
                        db.commit()

                    # Add Schedule edges (mock intermediate logic: direct edge)
                    # We store it as stop 1 and stop 2
                    existing_src = db.query(models.Schedule).filter_by(train_number=train_no, station_code=src).first()
                    if not existing_src:
                        db.add(models.Schedule(
                            train_number=train_no, station_code=src,
                            arrival_time="None", departure_time=dep_time, day_count=1, distance=0, stop_number=1
                        ))
                    
                    existing_dest = db.query(models.Schedule).filter_by(train_number=train_no, station_code=dest).first()
                    if not existing_dest:
                        db.add(models.Schedule(
                            train_number=train_no, station_code=dest,
                            arrival_time=arr_time, departure_time="None", day_count=2, distance=1000, stop_number=2
                        ))
            db.commit()
            time.sleep(1) # rate limit

    db.close()
    print("Real database populated successfully!")

if __name__ == "__main__":
    parse_and_seed()
