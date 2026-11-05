import json
import boto3

# Initialize a boto3 Session using your 'new-account' profile
session = boto3.Session(profile_name='new-account')
dynamodb = session.client('dynamodb', region_name='us-east-1')

table_name = "HrLeavePortalBackend-HrTable0964620C-18P2CTYIJ0WWN"

# Load the local backup file
with open('hr_leave_portal_backup.json', 'r') as f:
    data = json.load(f)

items = data.get('Items', [])
print(f"Importing {len(items)} items into {table_name}...")

# DynamoDB batch_write_item handles up to 25 items at a time
for i in range(0, len(items), 25):
    batch = items[i:i+25]
    request_items = {
        table_name: [{'PutRequest': {'Item': item}} for item in batch]
    }
    dynamodb.batch_write_item(RequestItems=request_items)

print("Data import completed successfully!")