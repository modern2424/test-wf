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

# Buffer time in seconds
BUFFER_SECONDS = 2

# Fetch audit logs from GitHub API
def fetch_audit_logs(before_timestamp, per_page=100):
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
        last_log = logs[-1]
        last_timestamp = last_log['@timestamp']
        return logs, last_timestamp
    else:
        return [], None

# Append logs to a JSON file
def append_logs(logs, file_name):
    file_path = os.path.join(BASE_DIR, file_name)
    
    # Ensure file exists and create if not
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("[\n")  # Start a new JSON array
    
    # Open the file to append logs
    with open(file_path, 'a') as f:
        if os.path.getsize(file_path) > 2:  # Check if file has more than just '[\n'
            f.write(",\n")  # Add a comma before new logs
        
        json.dump(logs, f, indent=4)
    
    print(f"Appended {len(logs)} logs to {file_path}")

# Consolidate logs from multiple files into a single file
def consolidate_logs(file_range_start, file_range_end):
    consolidated_file = f"logs-{file_range_start}-{file_range_end}.json"
    consolidated_path = os.path.join(BASE_DIR, consolidated_file)
    
    logs = []
    
    # Read logs from each file in the range
    for i in range(file_range_start, file_range_end + 1):
        file_name = f"log-{i}.json"
        file_path = os.path.join(BASE_DIR, file_name)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                file_logs = json.load(f)
                logs.extend(file_logs)
            
            os.remove(file_path)  # Remove the old log file after reading
    
    # Write consolidated logs to the new file
    with open(consolidated_path, 'w') as f:
        json.dump(logs, f, indent=4)
    
    print(f"Consolidated logs into {consolidated_path}")

# Function to fetch and save all logs based on timestamp
def fetch_logs_until_end_date(start_date, end_date):
    current_timestamp = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    previous_timestamp = None
    count = 1
    file_count = 1
    logs_per_file = 1000
    logs_buffer = []
    
    while True:
        print(f"Fetching logs before {current_timestamp}...")
        
        logs, last_timestamp = fetch_audit_logs(current_timestamp)
        
        if logs:
            logs_buffer.extend(logs)
            
            # If we have collected enough logs for a file
            if len(logs_buffer) >= logs_per_file:
                # Save the logs to a file
                file_name = f"log-{file_count}.json"
                append_logs(logs_buffer[:logs_per_file], file_name)
                
                # Move to next file
                file_count += 1
                logs_buffer = logs_buffer[logs_per_file:]  # Remaining logs for next file
                
            count += 1
            
            if last_timestamp:
                last_datetime = datetime.datetime.strptime(last_timestamp, '%Y-%m-%dT%H:%M:%SZ')
                new_timestamp = (last_datetime - datetime.timedelta(seconds=BUFFER_SECONDS)).strftime('%Y-%m-%dT%H:%M:%SZ')
                
                if previous_timestamp and (new_timestamp >= previous_timestamp):
                    print(f"Timestamp issue: current_timestamp ({current_timestamp}) is not decreasing properly.")
                    print(f"Last timestamp: {last_timestamp}")
                    break
                
                previous_timestamp = current_timestamp
                current_timestamp = new_timestamp
            else:
                current_datetime = datetime.datetime.strptime(current_timestamp, '%Y-%m-%dT%H:%M:%SZ')
                current_timestamp = (current_datetime - datetime.timedelta(seconds=BUFFER_SECONDS)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        else:
            if logs_buffer:
                # Save remaining logs if any
                file_name = f"log-{file_count}.json"
                append_logs(logs_buffer, file_name)
            
            print("No more logs to fetch.")
            break
        
        last_datetime = datetime.datetime.strptime(current_timestamp, '%Y-%m-%dT%H:%M:%SZ')
        if last_datetime <= end_date:
            print(f"Reached the end date: {end_date}")
            break
    
    # Consolidate files in range
    for start in range(1, count, logs_per_file):
        end = min(start + logs_per_file - 1, count - 1)
        if end > start:
            consolidate_logs(start, end)

# Start fetching logs from 2023-09-11 00:00 AM down to 2018-09-01 00:00 AM
start_date = datetime.datetime(2023, 9, 11, 0, 0)
end_date = datetime.datetime(2018, 9, 1, 0, 0)

# Fetch all logs in descending order and stop when the end date is reached
fetch_logs_until_end_date(start_date, end_date)
