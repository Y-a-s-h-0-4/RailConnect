import os
import boto3
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_access_KEY')
)

table = dynamodb.Table("RailConnectCache")

def check_aws():
    print("Pinging AWS DynamoDB...")
    try:
        response = table.scan(Limit=1)
        items = response.get('Items', [])
        if not items:
            print("Table is currently empty. Run python precompute_graph.py to fill it!")
        else:
            print(f"SUCCESS! Found `{items[0]['PathID']}` with {len(items[0]['Routes'])} bytes of cached JSON data!")
            print("AWS is successfully holding your Pre-computed Graph!")
    except Exception as e:
        print(f"AWS Error: {e}")

if __name__ == "__main__":
    check_aws()
