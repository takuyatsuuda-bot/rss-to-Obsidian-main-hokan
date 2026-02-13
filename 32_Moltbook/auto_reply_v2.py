import os
import json
import requests
import sys
import re

# Configuration
CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")
BASE_URL = "https://www.moltbook.com/api/v1"

# Mapping for string matching
WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
    'ninety': 90, 'hundred': 100
}

OPS = {
    'multipl': '*', 'times': '*', 'product': '*',
    'subtract': '-', 'minus': '-', 'less': '-', 'slow': '-', 'reduce': '-',
    'add': '+', 'plus': '+', 'total': '+', 'adds': '+'
}

def load_credentials():
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            return json.load(f)
    except:
        return None

def solve_challenge_v2(challenge_text):
    # 1. Remove ALL non-alpha characters (preserve nothing)
    clean = re.sub(r"[^a-zA-Z]", "", challenge_text).lower()
    print(f"Cleaned: {clean}")
    
    # 2. Scan for tokens
    found = []
    
    # Numbers
    for word, val in WORD_TO_NUM.items():
        start = 0
        while True:
            idx = clean.find(word, start)
            if idx == -1: break
            found.append((idx, 'num', val, len(word)))
            start = idx + 1
            
    # Ops
    for word, op in OPS.items():
        start = 0
        while True:
            idx = clean.find(word, start)
            if idx == -1: break
            found.append((idx, 'op', op, len(word)))
            start = idx + 1
            
    # Sort by index
    found.sort(key=lambda x: x[0])
    
    # Filter overlaps: Re-sort by index ASC, then length DESC
    found.sort(key=lambda x: (x[0], -x[3]))
    
    final_tokens = []
    curr_end = -1
    
    for item in found:
        idx, type_, val, length = item
        if idx >= curr_end:
            final_tokens.append(item)
            curr_end = idx + length
            
    print(f"Tokens: {[ (t, v) for _, t, v, _ in final_tokens]}")
    
    # 3. Collapse compound numbers
    collapsed = []
    i = 0
    while i < len(final_tokens):
        curr = final_tokens[i]
        if curr[1] == 'num':
            val = curr[2]
            # Look ahead
            if i + 1 < len(final_tokens) and final_tokens[i+1][1] == 'num':
                next_val = final_tokens[i+1][2]
                # Compound condition: e.g. 20 + 3 = 23.
                if val >= 20 and val % 10 == 0 and next_val < 10:
                    val += next_val
                    i += 1 # Skip next
                elif val == 100: # hundred case
                    pass
            collapsed.append(('num', val))
        else:
            collapsed.append((curr[1], curr[2]))
        i += 1
        
    print(f"Collapsed: {collapsed}")
    
    # 4. Perform calculation
    op = '+' # Default
    nums = [x[1] for x in collapsed if x[0] == 'num']
    ops = [x[1] for x in collapsed if x[0] == 'op']
    
    if ops:
        op = ops[0] # Take first op found
    
    if not nums: return 0
    
    res = nums[0]
    for n in nums[1:]:
        if op == '+': res += n
        elif op == '-': res -= n
        elif op == '*': res *= n
        
    return res

def auto_reply_v2(post_id, content):
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
        
        print(f"Challenge: {challenge}")
        
        # Solve
        try:
            answer_val = solve_challenge_v2(challenge)
            answer_str = f"{answer_val:.2f}"
            print(f"Calculated Answer: {answer_str}")
            
            # Verify
            verify_url = f"{BASE_URL}/verify"
            verify_payload = {"verification_code": code, "answer": answer_str}
            
            v_resp = requests.post(verify_url, headers=headers, json=verify_payload)
            print(f"Verification Response: {v_resp.text}")
            
        except Exception as e:
            print(f"Error solving/verifying: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 auto_reply_v2.py <post_id> <content>")
        sys.exit(1)
    
    auto_reply_v2(sys.argv[1], sys.argv[2])
