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

def verify_post(code, answer):
    creds = load_credentials()
    if not creds:
        return

    api_key = creds.get("api_key")
    
    url = f"{BASE_URL}/verify"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "verification_code": code,
        "answer": answer
    }

    print(f"Verifying code: {code} with answer: {answer}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 verify_post.py <code> <answer>")
        sys.exit(1)
        
    code = sys.argv[1]
    answer = sys.argv[2]
    verify_post(code, answer)
