import os
import json
import requests
import sys
import re
import time

# Configuration
CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")
BASE_URL = "https://www.moltbook.com/api/v1"

WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
    'ninety': 90
}

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

def solve_challenge(challenge_text):
    # Remove noise characters but keep spaces and hyphens
    clean_text = re.sub(r"[^a-zA-Z0-9\s\-]", "", challenge_text)
    print(f"Cleaned Text: {clean_text}")
    
    words = clean_text.lower().replace('-', ' ').split()
    
    numbers_found = []
    
    skip_next = False
    for i, w in enumerate(words):
        if skip_next:
            skip_next = False
            continue
            
        val = 0
        if w in WORD_TO_NUM:
            val = WORD_TO_NUM[w]
            # Check for compound numbers like "twenty five"
            if i + 1 < len(words) and words[i+1] in WORD_TO_NUM:
                val += WORD_TO_NUM[words[i+1]]
                skip_next = True
            numbers_found.append(val)
            
    print(f"Numbers found: {numbers_found}")
    
    # Heuristic for operation
    text_lower = clean_text.lower()
    
    if any(keyword in text_lower for keyword in ["multiplies", "multiply", "times", "product"]):
        print("Detected multiplication keyword.")
        if not numbers_found: return 0
        result = numbers_found[0]
        for n in numbers_found[1:]:
            result *= n
        return result
    elif any(keyword in text_lower for keyword in ["slow", "minus", "subtract", "reduce", "decrease", "less"]):
        print("Detected subtraction keyword.")
        if not numbers_found: return 0
        result = numbers_found[0]
        for n in numbers_found[1:]:
            result -= n
        return result
    else:
        print("Defaulting to addition.")
        return sum(numbers_found)

def auto_reply(post_id, content):
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
            print(f"❌ Rate limited: {resp.text}")
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
        
        print(f"Challenge received: {challenge}")
        
        # Solve
        try:
            answer_val = solve_challenge(challenge)
            answer_str = f"{answer_val:.2f}"
            print(f"Calculated Answer: {answer_str}")
            
            # Verify
            verify_url = f"{BASE_URL}/verify"
            verify_payload = {"verification_code": code, "answer": answer_str}
            
            print(f"Sending verification...")
            v_resp = requests.post(verify_url, headers=headers, json=verify_payload)
            print(f"Verification Status: {v_resp.status_code}")
            print(f"Verification Response: {v_resp.text}")
            
        except Exception as e:
            print(f"Error solving/verifying: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 auto_reply_moltbook.py <post_id> <content>")
        sys.exit(1)
    
    auto_reply(sys.argv[1], sys.argv[2])
