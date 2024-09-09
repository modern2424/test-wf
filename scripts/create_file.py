import json
import os

# File path for org.json
json_file_path = "provisioner/gha_onboarding/org.json"
org_name = "github_organization_name"
org_value = True

# Ensure the provisioner/gha_onboarding directory exists
os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

# Load the existing JSON data if the file exists, otherwise start with an empty dictionary
if os.path.exists(json_file_path):
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
else:
    data = {}

# Update or add the github_organization_name entry
data[org_name] = org_value

# Save the updated data back to the JSON file
with open(json_file_path, "w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Updated {json_file_path} with {org_name}: {org_value}")
