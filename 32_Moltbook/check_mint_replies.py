import os
import json
import requests

CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")
BASE_URL = "https://www.moltbook.com/api/v1"

def load_credentials():
    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            return json.load(f)
    except:
        return None

def check_replies():
    creds = load_credentials()
    if not creds:
        return

    api_key = creds.get("api_key")
    headers = {"Authorization": f"Bearer {api_key}"}

    print("Fetching recent posts...")
    resp = requests.get(f"{BASE_URL}/posts?sort=new&limit=20", headers=headers)
    posts = resp.json().get("posts", [])
    
    mint_posts = [p for p in posts if "mint" in (p.get("title", "") + p.get("content", "")).lower()]
    
    print(f"Checking {len(mint_posts)} mint posts for replies...")
    
    for post in mint_posts:
        post_id = post.get("id")
        # Fetch thread/comments for this post
        # Assuming there's an endpoint or we just check if 'comments_count' > 0 if available
        # But usually we need to fetch the post details or comments specifically
        
        # Let's try fetching post details which usually includes comments
        p_resp = requests.get(f"{BASE_URL}/posts/{post_id}", headers=headers)
        if p_resp.status_code == 200:
            p_data = p_resp.json()
            comments = p_data.get("comments", [])
            if comments:
                print(f"\n[Post {post_id}] has {len(comments)} comments:")
                for c in comments:
                    print(f"  - [{c.get('author', {}).get('name')}]: {c.get('content')}")
            else:
                # print(f"[Post {post_id}] No comments.")
                pass

if __name__ == "__main__":
    check_replies()
