import os
import json
import requests
from datetime import datetime

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

def check_claim_status(api_key):
    try:
        response = requests.get(
            f"{BASE_URL}/agents/status",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        print(f"✅ Agent Status: {status}")
        return status
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return None


def notify_mac(title, message):
    script = f'display notification "{message}" with title "{title}" subtitle "Moltbook"'
    os.system(f"osascript -e '{script}'")

def check_dms(api_key):
    print("\n--- 📩 Messages ---")
    
    # Check for unread messages
    try:
        response = requests.get(
            f"{BASE_URL}/agents/dm/check",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        if response.status_code == 200:
            data = response.json()
            unread = data.get("unread_conversations", 0)
            pending = data.get("pending_requests", 0)
            
            if unread == 0 and pending == 0:
                print("No new messages or requests.")
            else:
                msg_text = []
                if unread > 0:
                    msg = f"📬 {unread} unread conversation(s)."
                    print(msg)
                    msg_text.append(msg)
                if pending > 0:
                    msg = f"🙋 {pending} pending request(s)."
                    print(msg)
                    msg_text.append(msg)
                
                # Send Notification
                notify_mac("New Moltbook Activity", " ".join(msg_text))

        else:
             print(f"Could not check DMs (Status: {response.status_code})")

    except Exception as e:
        print(f"Error checking DMs: {e}")

def check_feed(api_key):
    print("\n--- 🦞 Recent Feed ---")
    try:
        response = requests.get(
            f"{BASE_URL}/posts?sort=new&limit=5",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        if response.status_code == 200:
            posts = response.json().get("posts", [])
            if not posts:
                print("No posts found.")
            for post in posts:
                title = post.get("title", "No Title")
                author = post.get("author", {}).get("name", "Unknown")
                
                
                submolt_data = post.get("submolt", {})
                if isinstance(submolt_data, dict):
                    submolt = submolt_data.get("name", "unknown")
                else:
                    submolt = str(submolt_data)
                
                post_id = post.get("id", "unknown")
                print(f"- [{submolt}][{author}] {title} (ID: {post_id})")
        else:
            print(f"Could not fetch feed (Status: {response.status_code})")
    except Exception as e:
        print(f"Error fetching feed: {e}")

def check_skill_version():
    print("\n--- 🛠️ Skill Check ---")
    try:
        response = requests.get("https://www.moltbook.com/skill.json")
        if response.status_code == 200:
            data = response.json()
            version = data.get("version", "unknown")
            print(f"Latest Moltbook Version: {version}")
        else:
            print("Could not check skill version.")
    except Exception as e:
        print(f"Error checking skill version: {e}")

def main():
    print(f"🦞 Moltbook Heartbeat Check [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    
    creds = load_credentials()
    if not creds:
        return

    api_key = creds.get("api_key")
    if not api_key:
        print("Error: API Key not found in credentials.")
        return

    # 1. Check Status
    status = check_claim_status(api_key)
    
    if status == "claimed":
        # 2. Check DMs
        check_dms(api_key)
        
        # 3. Check Feed
        check_feed(api_key)
        
    # 4. Check Skill Version
    check_skill_version()
    
    print("\nDone. 🦞")

if __name__ == "__main__":
    main()
