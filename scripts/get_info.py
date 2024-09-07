import requests
import json
import os

# Replace with your server details and credentials
GITHUB_API_URL = "https://<your-ghes-server>/api/v3/enterprises/<enterprise>/audit-log"
TOKEN = "your_github_token"
HEADERS = {"Authorization": f"token {TOKEN}"}

# Directory to save logs
SAVE_DIR = "/mnt/nfs01/audit_logs/"
os.makedirs(SAVE_DIR, exist_ok=True)

# Function to save logs to a file
def save_logs_to_file(logs, page_num):
    file_path = os.path.join(SAVE_DIR, f"audit_logs_page_{page_num}.json")
    with open(file_path, "w") as f:
        json.dump(logs, f)

def get_audit_logs():
    page_num = 1
    while True:
        params = {
            "per_page": 100,  # Adjust as needed
            "page": page_num
        }
        response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching page {page_num}: {response.status_code}")
            break

        logs = response.json()
        if not logs:
            print(f"Finished fetching all logs. Total pages: {page_num}")
            break

        # Save logs to file
        save_logs_to_file(logs, page_num)

        print(f"Fetched and saved page {page_num}")
        page_num += 1

if __name__ == "__main__":
    get_audit_logs()
