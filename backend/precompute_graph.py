import os
import boto3
import json
from dotenv import load_dotenv
from database import engine, SessionLocal
import models
from graph import find_routes, get_journey_time, time_to_mins, make_datetime_str, add_mins_to_datetime_str
from sqlalchemy import text

load_dotenv()

# Initialize AWS DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_access_KEY')
)

TABLE_NAME = "RailConnectCache"

def create_table_if_not_exists():
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'PathID', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PathID', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Waiting for logical DynamoDB table creation...")
        table.wait_until_exists()
        print("AWS DynamoDB Table Ready!")
    except Exception as e:
        if "Table already exists" in str(e):
            print("Table already exists on AWS.")
        else:
            print(f"Error creating table: {e}")

def get_busiest_stations(db, limit=100):
    """
    To prevent looping 16 Million times instantly, we will first extract 
    the absolute busiest N stations in India by counting schedules.
    """
    query = text("""
        SELECT station_code FROM schedules 
        GROUP BY station_code 
        ORDER BY COUNT(id) DESC 
        LIMIT :limit
    """)
    result = db.execute(query, {'limit': limit}).fetchall()
    return [r[0] for r in result]

def run_precomputation():
    create_table_if_not_exists()
    
    db = SessionLocal()
    table = dynamodb.Table(TABLE_NAME)
    
    # Let's start safely with the top 50 busiest stations (2500 pairs) 
    # to avoid locking up your PC for days while it crunches.
    print("Fetching Top Hubs...")
    top_stations = get_busiest_stations(db, 50)
    
    total_pairs = len(top_stations) * len(top_stations)
    print(f"Boto3 Initiated. Computing {total_pairs} Combinations to AWS...")
    
    pair_count = 0
    for source in top_stations:
        for destination in top_stations:
            if source == destination:
                continue
                
            pair_count += 1
            print(f"[{pair_count}/{total_pairs}] Computing {source} -> {destination}")
            
            # Use a dummy abstract date for math calculations.
            # Real dates will be injected by the frontend when parsing the JSON array.
            routes = find_routes(db, source, destination, date_str="2024-01-01", criteria="fastest", switches="0,1")
            
            if not routes:
                continue
                
            # Only keep the Top 5 to respect the AWS 14GB Budget logic
            top_5_routes = routes[:5]
            
            # Construct a Primary Key string like: "NDLS-BCT"
            path_id = f"{source}-{destination}"
            
            # Serialize
            route_json = json.dumps(top_5_routes)
            
            try:
                table.put_item(
                    Item={
                        'PathID': path_id,
                        'Routes': route_json
                    }
                )
            except Exception as e:
                print(f"AWS Upload failed for {path_id}: {e}")

    print("AWS DynamoDB Pre-computation Complete!")

if __name__ == "__main__":
    run_precomputation()
