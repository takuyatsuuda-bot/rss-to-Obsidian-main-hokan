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

def interactive_reply(post_id, content):
    creds = load_credentials()
    if not creds: return
    api_key = creds.get("api_key")
    
    # 1. Post Reply
    url = f"{BASE_URL}/posts/{post_id}/comments"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"content": content}
    
    print(f"Posting reply to {post_id}...")
    try:
        resp = requests.post(url, headers=headers, json=payload)
        
        if resp.status_code == 429:
            print(f"Rate limited: {resp.text}")
            return

        if resp.status_code not in [200, 201]:
            print(f"Failed to reply: {resp.status_code} {resp.text}")
            return
            
        data = resp.json()
        if not data.get("verification_required"):
            print("✅ Success! No verification needed.")
            return
            
        # 2. Handle Verification
        verification = data.get("verification", {})
        code = verification.get("code")
        challenge = verification.get("challenge")
        
        print(f"CHALLENGE: {challenge}")
        print("Please enter the answer (e.g. 42.00) immediately:")
        sys.stdout.flush()
        
        # Determine strict answer from input
        answer_str = input().strip() # Reads from stdin
        print(f"Start verifying with answer: {answer_str}")
        
        # Verify
        verify_url = f"{BASE_URL}/verify"
        verify_payload = {"verification_code": code, "answer": answer_str}
        
        v_resp = requests.post(verify_url, headers=headers, json=verify_payload)
        print(f"Verification Response: {v_resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 interactive_reply.py <post_id> <content>")
        sys.exit(1)
    
    interactive_reply(sys.argv[1], sys.argv[2])
