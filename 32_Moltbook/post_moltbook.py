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

def create_post(title, content, submolt="aiagents"):
    creds = load_credentials()
    if not creds:
        return

    api_key = creds.get("api_key")
    if not api_key:
        print("Error: API Key not found.")
        return

    url = f"{BASE_URL}/posts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": title,
        "content": content,
        "submolt": submolt
    }

    print(f"Creating post: {title} in {submolt}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print("✅ Post created successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to create post (Status: {response.status_code})")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 post_moltbook.py <title> <content> [submolt]")
        sys.exit(1)
    
    title = sys.argv[1]
    content = sys.argv[2]
    submolt = sys.argv[3] if len(sys.argv) > 3 else "aiagents"
    create_post(title, content, submolt)
