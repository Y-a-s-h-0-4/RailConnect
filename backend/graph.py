from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import crud
import models
import os
import boto3
import json
from dotenv import load_dotenv

load_dotenv()

dynamodb = None
cache_table = None
try:
    if os.getenv('AWS_ACCESS_KEY_ID'):
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_access_KEY', os.getenv('AWS_SECRET_ACCESS_KEY'))
        )
        cache_table = dynamodb.Table("RailConnectCache")
except Exception as e:
    print("AWS DynamoDB init failed:", e)

def offset_cached_dates(route_obj, target_date_str):
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    base_date = datetime(2024, 1, 1)
    diff_days = (target_date - base_date).days
    
    def traverse_and_add(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and len(v) == 19:
                    try:
                        dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                        obj[k] = (dt + timedelta(days=diff_days)).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                else:
                    traverse_and_add(v)
        elif isinstance(obj, list):
            for item in obj:
                traverse_and_add(item)

    traverse_and_add(route_obj)
    return route_obj

def time_to_mins(t_str: str) -> int:
    if t_str == "None" or not t_str: return 0
    parts = t_str.split(':')
    h, m = int(parts[0]), int(parts[1])
    return h * 60 + m

def get_journey_time(dep_time: str, dep_day: int, arr_time: str, arr_day: int) -> int:
    dep_m = time_to_mins(dep_time)
    arr_m = time_to_mins(arr_time)
    return (arr_day - dep_day) * 24 * 60 + (arr_m - dep_m)

def add_mins_to_datetime_str(dt_str: str, mins: int) -> str:
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    dt += timedelta(minutes=mins)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def make_datetime_str(base_date_str: str, time_str: str) -> str:
    parts = time_str.split(':')
    h, m = parts[0], parts[1]
    s = parts[2] if len(parts) > 2 else "00"
    return f"{base_date_str} {h}:{m}:{s}"

def find_routes(db: Session, source: str, destination: str, date_str: str = "2026-03-01", criteria: str = "fastest", switches: str = "0,1"):
    source_code = crud.resolve_station_code(db, source)
    dest_code = crud.resolve_station_code(db, destination)

    if not source_code or not dest_code:
        return []

    source = source_code
    destination = dest_code
    
    # --- 0. Try AWS Cache First ---
    if cache_table:
        try:
            path_id = f"{source}-{destination}"
            response = cache_table.get_item(Key={'PathID': path_id})
            if 'Item' in response:
                print(f"CACHE HIT on AWS for {path_id}!")
                cached_json = json.loads(response['Item']['Routes'])
                return offset_cached_dates(cached_json, date_str)
        except Exception as e:
            print(f"AWS Cache Read Failed: {e}")
    
    switches_list = []
    if switches == "all":
        switches_list = [0, 1, 2]
    else:
        switches_list = [int(x) for x in switches.split(",")]

    direct_routes = []
    connecting_routes = []
    
    # --- 1. Direct Routes ---
    query_direct = text("""
        SELECT 
            t1.train_number, 
            tr.train_name, 
            t1.departure_time, 
            t2.arrival_time,
            t1.day_count AS dep_day,
            t2.day_count AS arr_day
        FROM schedules t1
        JOIN schedules t2 ON t1.train_number = t2.train_number
        JOIN trains tr ON t1.train_number = tr.train_number
        WHERE t1.station_code = :source 
          AND t2.station_code = :destination
          AND t2.stop_number > t1.stop_number
          AND t1.departure_time != 'None'
          AND t2.arrival_time != 'None'
    """)
    
    result_direct = db.execute(query_direct, {"source": source, "destination": destination}).fetchall()
    
    min_direct_duration = float('inf')
    
    for row in result_direct:
        duration = get_journey_time(row[2], row[4], row[3], row[5])
        if duration < min_direct_duration:
            min_direct_duration = duration
            
        dep_dt = make_datetime_str(date_str, row[2])
        arr_dt = add_mins_to_datetime_str(dep_dt, duration)
        
        direct_routes.append({
            "type": "direct",
            "train_number": row[0],
            "train_name": row[1],
            "departure": dep_dt,
            "arrival": arr_dt,
            "duration_mins": duration,
            "switches": 0
        })

    # --- 2. Connecting Routes ---
    
    # Pre-calculate direct train numbers to avoid suggesting a connection on a train that already goes all the way
    direct_train_numbers = {r["train_number"] for r in direct_routes}
    
    if 1 in switches_list and min_direct_duration != float('inf'):
        query_conn = text("""
        SELECT 
            s1.train_number AS t1_num, tr1.train_name AS t1_name,
            s1.departure_time AS t1_dep, s2.arrival_time AS t1_arr,
            s1.day_count AS t1_dep_day, s2.day_count AS t1_arr_day,
            
            s2.station_code AS transfer_stn, stn.name AS transfer_name,
            
            s3.train_number AS t2_num, tr2.train_name AS t2_name,
            s3.departure_time AS t2_dep, s4.arrival_time AS t2_arr,
            s3.day_count AS t2_dep_day, s4.day_count AS t2_arr_day
            
        FROM schedules s1
        JOIN schedules s2 ON s1.train_number = s2.train_number AND s2.stop_number > s1.stop_number
        JOIN trains tr1 ON s1.train_number = tr1.train_number
        
        JOIN schedules s3 ON s2.station_code = s3.station_code AND s1.train_number != s3.train_number
        JOIN schedules s4 ON s3.train_number = s4.train_number AND s4.stop_number > s3.stop_number
        JOIN trains tr2 ON s3.train_number = tr2.train_number
        JOIN stations stn ON s2.station_code = stn.code
        
        WHERE s1.station_code = :source 
          AND s4.station_code = :destination
          AND s1.departure_time != 'None'
          AND s2.arrival_time != 'None'
          AND s3.departure_time != 'None'
          AND s4.arrival_time != 'None'
        """)
        
        result_conn = db.execute(query_conn, {"source": source, "destination": destination}).fetchall()
    else:
        result_conn = []
    
    max_allowed_duration = min_direct_duration * 1.25 if min_direct_duration != float('inf') else float('inf')
    
    best_connections = {}
    
    for row in result_conn:
        t1_num, t1_name, t1_dep, t1_arr, t1_dep_day, t1_arr_day, transfer_stn, transfer_name, t2_num, t2_name, t2_dep, t2_arr, t2_dep_day, t2_arr_day = row
        
        # Skip if either leg is a direct train itself 
        if t1_num in direct_train_numbers or t2_num in direct_train_numbers:
            continue
            
        duration1 = get_journey_time(t1_dep, t1_dep_day, t1_arr, t1_arr_day)
        duration2 = get_journey_time(t2_dep, t2_dep_day, t2_arr, t2_arr_day)
        
        arr_m = time_to_mins(t1_arr)
        dep_m = time_to_mins(t2_dep)
        layover = dep_m - arr_m
        if layover < 0: layover += 24*60
        
        # Require 15 minutes minimum layover, 12 hours maximum
        if layover >= 15 and layover <= 12 * 60:
            total_duration = duration1 + layover + duration2
            
            if total_duration <= max_allowed_duration:
                pair_key = (t1_num, t2_num)
                # If we've seen this pair of trains before, only keep the connection with the shorter total duration
                if pair_key not in best_connections or total_duration < best_connections[pair_key]["total_duration_mins"]:
                    leg1_dep_dt = make_datetime_str(date_str, t1_dep)
                    leg1_arr_dt = add_mins_to_datetime_str(leg1_dep_dt, duration1)
                    leg2_dep_dt = add_mins_to_datetime_str(leg1_arr_dt, layover)
                    leg2_arr_dt = add_mins_to_datetime_str(leg2_dep_dt, duration2)
                    
                    best_connections[pair_key] = {
                        "type": "connecting",
                        "leg1": {
                            "train_number": t1_num, "train_name": t1_name,
                            "from": source, "to": transfer_stn,
                            "departure": leg1_dep_dt, "arrival": leg1_arr_dt
                        },
                        "layover_mins": layover,
                        "transfer_station": transfer_stn,
                        "transfer_station_name": transfer_name,
                        "leg2": {
                            "train_number": t2_num, "train_name": t2_name,
                            "from": transfer_stn, "to": destination,
                            "departure": leg2_dep_dt, "arrival": leg2_arr_dt
                        },
                        "total_duration_mins": total_duration,
                        "switches": 1
                    }

        connecting_routes.extend(best_connections.values())
        
    all_routes = []
    if 0 in switches_list:
        all_routes.extend(direct_routes)
    if 1 in switches_list:
        # Extra safety measure: Ensure no duplicate train pairs slipped through
        seen_pairs = set()
        unique_conn = []
        for r in connecting_routes:
            pid = (r["leg1"]["train_number"], r["leg2"]["train_number"])
            if pid not in seen_pairs:
                seen_pairs.add(pid)
                unique_conn.append(r)
        all_routes.extend(unique_conn)
        
    # --- 3. 2-Switch Connecting Routes ---
    connecting_routes_2 = []
    if 2 in switches_list and min_direct_duration != float('inf'):
        query_conn2 = text("""
            SELECT 
                s1.train_number as t1_num, tr1.train_name as t1_name,
                s1.departure_time as t1_dep, s2.arrival_time as t1_arr,
                s1.day_count as t1_dep_day, s2.day_count as t1_arr_day,
                
                s2.station_code as trans1_stn, stn1.name as trans1_name,
                
                s3.train_number as t2_num, tr2.train_name as t2_name,
                s3.departure_time as t2_dep, s4.arrival_time as t2_arr,
                s3.day_count as t2_dep_day, s4.day_count as t2_arr_day,
                
                s4.station_code as trans2_stn, stn2.name as trans2_name,
                
                s5.train_number as t3_num, tr3.train_name as t3_name,
                s5.departure_time as t3_dep, s6.arrival_time as t3_arr,
                s5.day_count as t3_dep_day, s6.day_count as t3_arr_day
            FROM schedules s1
            JOIN schedules s2 ON s1.train_number = s2.train_number AND s2.stop_number > s1.stop_number
            JOIN trains tr1 ON s1.train_number = tr1.train_number
            
            JOIN schedules s3 ON s2.station_code = s3.station_code AND s1.train_number != s3.train_number
            JOIN schedules s4 ON s3.train_number = s4.train_number AND s4.stop_number > s3.stop_number
            JOIN trains tr2 ON s3.train_number = tr2.train_number
            JOIN stations stn1 ON s2.station_code = stn1.code
            
            JOIN schedules s5 ON s4.station_code = s5.station_code AND s3.train_number != s5.train_number
            JOIN schedules s6 ON s5.train_number = s6.train_number AND s6.stop_number > s5.stop_number
            JOIN trains tr3 ON s5.train_number = tr3.train_number
            JOIN stations stn2 ON s4.station_code = stn2.code
            
            WHERE s1.station_code = :source 
              AND s6.station_code = :destination
              AND s1.departure_time != 'None' AND s2.arrival_time != 'None'
              AND s3.departure_time != 'None' AND s4.arrival_time != 'None'
              AND s5.departure_time != 'None' AND s6.arrival_time != 'None'
            LIMIT 5000
        """)
        
        result_conn2 = db.execute(query_conn2, {"source": source, "destination": destination}).fetchall()
        max_allowed_duration2 = min_direct_duration * 1.5 
        best_connections2 = {}

        for row2 in result_conn2:
            t1_num, t1_name, t1_dep, t1_arr, t1_dep_day, t1_arr_day, trans1_stn, trans1_name, t2_num, t2_name, t2_dep, t2_arr, t2_dep_day, t2_arr_day, trans2_stn, trans2_name, t3_num, t3_name, t3_dep, t3_arr, t3_dep_day, t3_arr_day = row2
            
            if t1_num in direct_train_numbers or t2_num in direct_train_numbers or t3_num in direct_train_numbers:
                continue
                
            duration1 = get_journey_time(t1_dep, t1_dep_day, t1_arr, t1_arr_day)
            duration2 = get_journey_time(t2_dep, t2_dep_day, t2_arr, t2_arr_day)
            duration3 = get_journey_time(t3_dep, t3_dep_day, t3_arr, t3_arr_day)
            
            arr_m1 = time_to_mins(t1_arr)
            dep_m2 = time_to_mins(t2_dep)
            layover1 = dep_m2 - arr_m1
            if layover1 < 0: layover1 += 24*60
            
            arr_m2 = time_to_mins(t2_arr)
            dep_m3 = time_to_mins(t3_dep)
            layover2 = dep_m3 - arr_m2
            if layover2 < 0: layover2 += 24*60
            
            if layover1 >= 15 and layover1 <= 12 * 60 and layover2 >= 15 and layover2 <= 12 * 60:
                total_duration = duration1 + duration2 + duration3 + layover1 + layover2
                if total_duration <= max_allowed_duration2:
                    pair_key = (t1_num, t2_num, t3_num)
                    if pair_key not in best_connections2 or total_duration < best_connections2[pair_key]["total_duration_mins"]:
                        leg1_dep_dt = make_datetime_str(date_str, t1_dep)
                        leg1_arr_dt = add_mins_to_datetime_str(leg1_dep_dt, duration1)
                        leg2_dep_dt = add_mins_to_datetime_str(leg1_arr_dt, layover1)
                        leg2_arr_dt = add_mins_to_datetime_str(leg2_dep_dt, duration2)
                        leg3_dep_dt = add_mins_to_datetime_str(leg2_arr_dt, layover2)
                        leg3_arr_dt = add_mins_to_datetime_str(leg3_dep_dt, duration3)
                        
                        best_connections2[pair_key] = {
                            "type": "connecting2",
                            "leg1": {
                                "train_number": t1_num, "train_name": t1_name,
                                "from": source, "to": trans1_stn,
                                "departure": leg1_dep_dt, "arrival": leg1_arr_dt
                            },
                            "layover_mins": layover1,
                            "transfer_station": trans1_stn,
                            "transfer_station_name": trans1_name,
                            "leg2": {
                                "train_number": t2_num, "train_name": t2_name,
                                "from": trans1_stn, "to": trans2_stn,
                                "departure": leg2_dep_dt, "arrival": leg2_arr_dt
                            },
                            "layover_mins2": layover2,
                            "transfer_station2": trans2_stn,
                            "transfer_station_name2": trans2_name,
                            "leg3": {
                                "train_number": t3_num, "train_name": t3_name,
                                "from": trans2_stn, "to": destination,
                                "departure": leg3_dep_dt, "arrival": leg3_arr_dt
                            },
                            "total_duration_mins": total_duration,
                            "switches": 2
                        }

        connecting_routes_2.extend(best_connections2.values())
        
        seen_pairs_2 = set()
        unique_conn_2 = []
        for r in connecting_routes_2:
            pid = (r["leg1"]["train_number"], r["leg2"]["train_number"], r["leg3"]["train_number"])
            if pid not in seen_pairs_2:
                seen_pairs_2.add(pid)
                unique_conn_2.append(r)
                
        all_routes.extend(unique_conn_2)
    
    if criteria == "fastest":
        all_routes.sort(key=lambda x: x.get("duration_mins") if x["type"] == "direct" else x.get("total_duration_mins"))
    elif criteria == "fewest_switches":
        all_routes.sort(key=lambda x: x["switches"])
    
    return all_routes[:250]
