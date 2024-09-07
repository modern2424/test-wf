import os
import json
import requests
from datetime import datetime, timedelta
import time

# GitHub API Token and Org details
TOKEN = "YOUR_TOKEN"
ORG = "YOUR_ORG"
BASE_URL = f"https://api.github.com/orgs/{ORG}/audit-log"
HEADERS = {"Authorization": f"token {TOKEN}"}

# Starting and ending dates
START_DATE = "2018-09-01"
END_DATE = "2023-09-10"

# Folder to save logs
BASE_SAVE_PATH = "/mnt/nfs01/audit_logs"  # Modify this path as needed

# Function to create directory structure
def create_directories_for_date(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    month_folder = os.path.join(BASE_SAVE_PATH, date.strftime("%Y-%m"))
    day_folder = os.path.join(month_folder, date.strftime("%Y-%m-%d"))
    
    if not os.path.exists(day_folder):
        os.makedirs(day_folder)
    return day_folder

# Function to fetch logs for a specific date and page
def fetch_logs(date_str, page_num):
    params = {
        "per_page": 100,
        "page": page_num,
        "phrase": f"created:{date_str}",
        "order": "asc"
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

# Function to save logs to file
def save_logs_to_file(logs, folder, page_num):
    file_path = os.path.join(folder, f"logs_page_{page_num}.json")
    with open(file_path, 'w') as f:
        json.dump(logs, f, indent=4)

# Function to log dates with high page count
def log_high_page_count_date(date_str):
    log_file = os.path.join(BASE_SAVE_PATH, "high_page_dates.txt")
    with open(log_file, 'a') as f:
        f.write(f"{date_str}\n")

# Main function to iterate over the date range and fetch logs
def fetch_audit_logs(start_date, end_date):
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        day_folder = create_directories_for_date(date_str)
        page_num = 1
        logs_fetched = False

        while True:
            logs = fetch_logs(date_str, page_num)
            if not logs:
                break
            
            logs_fetched = True
            save_logs_to_file(logs, day_folder, page_num)
            
            # Increment page number for pagination
            page_num += 1

            # If page number reaches 100, log the date
            if page_num >= 100:
                log_high_page_count_date(date_str)

            # Rate limiting delay (adjust as needed)
            time.sleep(1)

        # Move to the next date
        current_date += timedelta(days=1)

        # If no logs were fetched for the entire day, break early
        if not logs_fetched:
            print(f"No logs for {date_str}")
            break

if __name__ == "__main__":
    fetch_audit_logs(START_DATE, END_DATE)
