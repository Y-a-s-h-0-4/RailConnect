import json
import urllib.request
import ssl
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models
import os

STATIONS_URL = "https://raw.githubusercontent.com/datameet/railways/master/stations.json"
TRAINS_URL = "https://raw.githubusercontent.com/datameet/railways/master/trains.json"
SCHEDULES_URL = "https://raw.githubusercontent.com/datameet/railways/master/schedules.json"

def fetch_json(url):
    print(f"Downloading {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    context = ssl._create_unverified_context()
    response = urllib.request.urlopen(req, context=context)
    return json.loads(response.read().decode('utf-8'))

def seed_database():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear old data for a fresh start (optional, but good for consistency)
    print("Clearing old data...")
    db.query(models.Schedule).delete()
    db.query(models.Train).delete()
    db.query(models.Station).delete()
    db.commit()

    try:
        # 1. Fetch and Seed Stations
        stations_data = fetch_json(STATIONS_URL)
        print(f"Loaded {len(stations_data['features'])} stations from JSON")
        station_objects = []
        station_codes = set()
        for feature in stations_data['features']:
            props = feature.get('properties', {})
            code = props.get('code')
            if not code or code in station_codes: continue
            
            name = props.get('name', '')
            state = props.get('state', '')
            station_objects.append(models.Station(code=code, name=name, city=state))
            station_codes.add(code)
            
        print(f"Inserting {len(station_objects)} unique stations...")
        db.bulk_save_objects(station_objects)
        db.commit()

        # 2. Fetch and Seed Trains
        trains_data = fetch_json(TRAINS_URL)
        print(f"Loaded {len(trains_data['features'])} trains from JSON")
        train_objects = []
        train_numbers = set()
        
        for feature in trains_data['features']:
            props = feature.get('properties', {})
            number = props.get('number')
            if not number or number in train_numbers: continue
            
            name = props.get('name', '')
            train_objects.append(models.Train(train_number=str(number), train_name=name))
            train_numbers.add(number)
            
        print(f"Inserting {len(train_objects)} unique trains...")
        db.bulk_save_objects(train_objects)
        db.commit()

        # 3. Fetch and Seed Schedules
        schedules_data = fetch_json(SCHEDULES_URL)
        print(f"Loaded {len(schedules_data)} schedule entries from JSON")
        
        schedule_objects = []
        batch_size = 10000
        
        for i, entry in enumerate(schedules_data):
            train_number = str(entry.get('train_number', ''))
            station_code = entry.get('station_code')
            
            # Constraints checking
            if train_number not in train_numbers or station_code not in station_codes:
                continue
                
            arrival = entry.get('arrival', 'None')
            departure = entry.get('departure', 'None')
            day = entry.get('day', 1)
            dist = entry.get('distance', 0.0)
            seq = entry.get('id', 0)
            
            try:
                distance_float = float(dist)
            except (ValueError, TypeError):
                distance_float = 0.0
                
            schedule_objects.append(models.Schedule(
                train_number=train_number,
                station_code=station_code,
                arrival_time=arrival,
                departure_time=departure,
                day_count=int(day) if day else 1,
                distance=distance_float,
                stop_number=int(seq) if seq else 0
            ))
            
            # Batch commit to avoid memory issues
            if len(schedule_objects) >= batch_size:
                db.bulk_save_objects(schedule_objects)
                db.commit()
                schedule_objects = []
                print(f"Inserted {i+1} schedule entries...")
                
        # Insert remaining
        if schedule_objects:
            db.bulk_save_objects(schedule_objects)
            db.commit()
            print(f"Inserted all {len(schedules_data)} schedule entries!")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
        print("Done populating realistic data.")

if __name__ == "__main__":
    seed_database()
