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

def investigate():
    creds = load_credentials()
    if not creds:
        print("No creds")
        return

    api_key = creds.get("api_key")
    headers = {"Authorization": f"Bearer {api_key}"}

    print("Fetching recent posts...")
    # Fetch more posts to get context
    resp = requests.get(f"{BASE_URL}/posts?sort=new&limit=50", headers=headers)
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code}")
        return

    posts = resp.json().get("posts", [])
    
    mint_posts = []
    claw_posts = []
    other_posts = []

    for post in posts:
        title = post.get("title", "")
        content = post.get("content", "")
        author = post.get("author", {}).get("name", "")
        
        combined = (title + content).lower()
        
        if "mint" in combined:
            mint_posts.append(post)
        elif "claw" in combined:
            claw_posts.append(post)
        else:
            other_posts.append(post)

    print(f"\nFound {len(mint_posts)} 'Mint' posts and {len(claw_posts)} 'CLAW' posts out of {len(posts)} total.")

    mint_try_posts = [p for p in mint_posts if "mint try" in p.get("title", "").lower()]
    
    if mint_try_posts:
        print(f"\n--- Found {len(mint_try_posts)} 'Mint try' posts. Sample Content: ---")
        p = mint_try_posts[0]
        print(f"Title: {p.get('title')}")
        print(f"Author: {p.get('author', {}).get('name')}")
        print(f"Content: {p.get('content')}")
        print("-" * 20)
    elif mint_posts:
        print("\n--- Sample Mint Post (Not 'Mint try') ---")
        p = mint_posts[0]
        print(f"Title: {p.get('title')}")
        print(f"Author: {p.get('author', {}).get('name')}")
        print(f"Content: {p.get('content')}")
        print("-" * 20)

    if claw_posts:
        print("\n--- Sample CLAW Post Content ---")
        p = claw_posts[0] # Just show one to see what it is
        print(f"Title: {p.get('title')}")
        print(f"Author: {p.get('author', {}).get('name')}")
        print(f"Content: {p.get('content')}")
        print("-" * 20)
        
    if other_posts:
        print("\n--- Recent Non-Mint/CLAW Activity ---")
        for p in other_posts[:3]:
            print(f"- [{p.get('author', {}).get('name')}] {p.get('title')}")

if __name__ == "__main__":
    investigate()
