import os
import json
import requests
import sys

# Configuration
CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")
BASE_URL = "https://www.moltbook.com/api/v1"

def load_credentials():
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Error: Credentials not found at {CREDENTIALS_PATH}")
        return None
    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading credentials: {e}")
        return None

def reply_to_post(post_id, content):
    creds = load_credentials()
    if not creds:
        return

    api_key = creds.get("api_key")
    if not api_key:
        print("Error: API Key not found.")
        return

    url = f"{BASE_URL}/posts/{post_id}/comments"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"content": content}

    print(f"Sending reply to {post_id}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 reply_moltbook.py <post_id> <content>")
        sys.exit(1)
    
    post_id = sys.argv[1]
    content = sys.argv[2]
    reply_to_post(post_id, content)
