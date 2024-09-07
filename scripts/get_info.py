import requests
import datetime
import os
import json

# GitHub authentication and organization info
GITHUB_TOKEN = "your_token_here"
ORG = "your_org_here"
BASE_URL = f"https://api.github.com/orgs/{ORG}/audit-log"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
}

# Base directory for saving logs
BASE_DIR = "/mnt/nfs01/github-audit-logs"
os.makedirs(BASE_DIR, exist_ok=True)

# Fetch audit logs from GitHub API
def fetch_audit_logs(before_timestamp, per_page=100):
    # Construct query params with timestamp and pagination
    params = {
        "phrase": f"created:<{before_timestamp}",
        "order": "desc",
        "per_page": per_page
    }
    
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch logs: {response.status_code} - {response.text}")
        return [], None
    
    logs = response.json()
    
    if logs:
        # Get the timestamp from the last log in the batch
        last_log = logs[-1]
        last_timestamp = last_log['@timestamp']
        
        # Convert the last timestamp to a human-readable string
        readable_time = datetime.datetime.utcfromtimestamp(int(last_timestamp) / 1000).strftime('%Y-%m-%dT%H:%M:%SZ')
        return logs, readable_time
    else:
        return [], None

# Save logs to a JSON file
def save_logs(logs, file_name):
    file_path = os.path.join(BASE_DIR, file_name)
    with open(file_path, 'w') as f:
        json.dump(logs, f, indent=4)
    print(f"Saved {len(logs)} logs to {file_path}")

# Function to fetch and save all logs based on timestamp
def fetch_logs_until_end_date(start_date, end_date):
    current_timestamp = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    count = 1
    
    while True:
        print(f"Fetching logs before {current_timestamp}...")
        
        # Fetch logs before the current timestamp
        logs, last_timestamp = fetch_audit_logs(current_timestamp)
        
        if not logs:
            print("No more logs to fetch.")
            break
        
        # Save logs with a file name like '2023-09-11-1.json', '2023-09-11-2.json'
        file_name = f"{start_date.strftime('%Y-%m-%d')}-{count}.json"
        save_logs(logs, file_name)
        
        count += 1  # Increment the file counter for each batch
        
        # Update the current timestamp for the next query
        current_timestamp = last_timestamp
        
        # Stop if the last timestamp is before the end date
        last_datetime = datetime.datetime.strptime(current_timestamp, '%Y-%m-%dT%H:%M:%SZ')
        if last_datetime <= end_date:
            print(f"Reached the end date: {end_date}")
            break

# Start fetching logs from 2023-09-11 00:00 AM down to 2018-09-01 00:00 AM
start_date = datetime.datetime(2023, 9, 11, 0, 0)
end_date = datetime.datetime(2018, 9, 1, 0, 0)

# Fetch all logs in descending order and stop when the end date is reached
fetch_logs_until_end_date(start_date, end_date)
