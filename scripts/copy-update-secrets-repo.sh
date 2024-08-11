#!/bin/bash

# Variables (replace with your actual values)
#AUTH_TOKEN=""
#ORG_NAME=""
#SECRET_NAME=""
#SECRET_VALUE=""
#REPO_NAME=""

# Step 1: Get the public key for the organization
echo "Fetching the public key for the organization..."
response=$(curl -s -H "Authorization: Bearer $AUTH_TOKEN" \
                -H "Accept: application/vnd.github+json" \
                https://api.github.com/$ORG_NAME/$REPO_NAME/actions/secrets/public-key)

key_id=$(echo "$response" | jq -r .key_id)
public_key=$(echo "$response" | jq -r .key)

if [ -z "$key_id" ] || [ -z "$public_key" ]; then
  echo "Failed to retrieve public key. Exiting..."
  exit 1
fi

echo "Public key retrieved. Key ID: $key_id"

# Step 2: Encrypt the secret using Python and the public key
echo "Encrypting the secret..."
encrypted_value=$(python3 -c "
import base64
from nacl import encoding, public

def encrypt(public_key: str, secret: str) -> str:
    public_key = public.PublicKey(public_key.encode('utf-8'), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

print(encrypt('$public_key', '$SECRET_VALUE'))
")

if [ -z "$encrypted_value" ]; then
  echo "Encryption failed. Exiting..."
  exit 1
fi

echo "Secret encrypted."
# Step 3: Create or update the organization secret
echo "Creating or updating the repository secret..."
update_response=$(curl -s -X PUT -H "Authorization: Bearer $AUTH_TOKEN" \
                     -H "Accept: application/vnd.github+json" \
                     -d "{\"encrypted_value\":\"$encrypted_value\", \"key_id\":\"$key_id\", \"visibility\":\"private\"}" \
                     https://api.github.com/$ORG_NAME/$REPO_NAME/actions/secrets/$SECRET_NAME)

#if echo "$update_response" | grep -q '"created_at"'; then
if [[ "$update_response" == "201" || "$update_response" == "204" ]]; then
  echo "Secret '$SECRET_NAME' successfully created or updated."
else
  echo "Failed to create or update the secret. Response: $update_response"
  exit 1
fi
