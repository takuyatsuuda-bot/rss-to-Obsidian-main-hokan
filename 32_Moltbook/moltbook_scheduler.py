import time
import subprocess
import os
import datetime

# Check every 60 minutes
INTERVAL_SECONDS = 3600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_SCRIPT = os.path.join(BASE_DIR, "check_moltbook.py")

# Import the posting logic
import sys
sys.path.append(BASE_DIR)
import requests # Need requests for verification
import json

try:
    from post_moltbook import create_post, BASE_URL, load_credentials
except ImportError:
    create_post = None
    BASE_URL = "https://www.moltbook.com/api/v1"
    load_credentials = lambda: None
    print("⚠️  Could not import post_moltbook.py")

try:
    from solver import solve_challenge_v3
except ImportError:
    solve_challenge_v3 = lambda x: 0
    print("⚠️  Could not import solver.py")

def verify_challenge(code, challenge, api_key):
    print(f"🧩 Solving Challenge: {challenge[:30]}...")
    try:
        answer_val = solve_challenge_v3(challenge)
        answer_str = f"{answer_val:.2f}"
        print(f"💡 Calculated Answer: {answer_str}")
        
        url = f"{BASE_URL}/verify"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"verification_code": code, "answer": answer_str}
        
        resp = requests.post(url, headers=headers, json=payload)
        print(f"Verification Response: {resp.text}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")

# We need to monkey-patch or modify create_post to handle verification return
# Or just copy-paste the logic since create_post in post_moltbook doesn't return the response object cleanly for external use?
# Actually post_moltbook just prints. We should probably modify run_mint to do its own posting or modify create_post.
# Let's write a custom posting function here to handle the full flow.

def custom_post_mint():
    creds = load_credentials()
    if not creds: return
    api_key = creds.get("api_key")
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = f"Mint try {timestamp}"
    content = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}\n\nmbc20.xyz'
    
    url = f"{BASE_URL}/posts"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"title": title, "content": content, "submolt": "general"}
    
    print(f"💰 Minting CLAW ({timestamp})...")
    try:
        resp = requests.post(url, headers=headers, json=payload)
        data = resp.json()
        
        if resp.status_code in [200, 201]:
            print("✅ Post created.")
            
            if data.get("verification_required"):
                v = data.get("verification", {})
                code = v.get("code")
                chal = v.get("challenge")
                if code and chal:
                    verify_challenge(code, chal, api_key)
        else:
            print(f"❌ Post failed: {resp.status_code} {resp.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def run_check():
    print(f"\n🦞 Running Moltbook Check at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    if os.path.exists(CHECK_SCRIPT):
        try:
            subprocess.run(["python3", CHECK_SCRIPT], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running script: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    else:
        print(f"❌ Script not found: {CHECK_SCRIPT}")

def run_mint():
    # Use our custom function that handles verification
    custom_post_mint()

def main():
    print("--- 🦞 Moltbook Scheduler Started (Verified) ---")
    print(f" > Checking & Minting every {INTERVAL_SECONDS/60} minutes.")
    print(" > Press Ctrl+C to stop.")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit (for GitHub Actions)")
    args = parser.parse_args()

    try:
        # Run once immediately
        run_check()
        run_mint()
        
        if args.once:
            print("✅ --once flag detected. Exiting.")
            return

        while True:
            time.sleep(INTERVAL_SECONDS)
            run_check()
            run_mint()

    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped.")

if __name__ == "__main__":
    main()
