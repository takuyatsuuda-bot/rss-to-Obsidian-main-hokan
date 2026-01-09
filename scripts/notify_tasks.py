import os
import datetime
import requests
import glob

def get_line_notify_token():
    """Get LINE Notify Token from environment variable."""
    token = os.environ.get("LINE_NOTIFY_TOKEN")
    if not token:
        print("Error: LINE_NOTIFY_TOKEN not found.")
        return None
    return token

def send_line_notify(token, message):
    """Send message to LINE Notify."""
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        print("Notification sent successfully.")
    except Exception as e:
        print(f"Failed to send notification: {e}")

def find_today_file():
    """Find today's daily note file."""
    # Logic to find the file.
    # Structure seems to be: 00_Daily Note/YYYY-MM/YYYY-MM-DD.md
    # OR Daily Note/YYYY-MM/YYYY-MM-DD.md (User has mixed structures, need to handle both or search)
    
    today = datetime.datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    year_month = today.strftime("%Y-%m")
    
    # Potential paths
    paths = [
        f"00_Daily Note/{year_month}/{date_str}.md",
        f"Daily Note/{year_month}/{date_str}.md",
        f"Daily Note/{date_str}.md",
        f"{date_str}.md"
    ]
    
    for relative_path in paths:
        if os.path.exists(relative_path):
            return relative_path
            
    # Fallback: search recursively if not found in expected locations
    files = glob.glob(f"**/{date_str}.md", recursive=True)
    if files:
        return files[0]
        
    return None

def extract_tasks(file_path):
    """Extract incomplete tasks from the file."""
    tasks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                # Check for incomplete tasks "- [ ]"
                if stripped.startswith("- [ ]"):
                    # Remove the checkbox marker
                    task_content = stripped.replace("- [ ]", "").strip()
                    tasks.append(task_content)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    return tasks

def main():
    token = get_line_notify_token()
    if not token:
        return

    file_path = find_today_file()
    if not file_path:
        print("Today's daily note not found.")
        # Optional: Send a notification saying note not found?
        # send_line_notify(token, "今日のデイリーノートが見つかりませんでした。")
        return

    print(f"Found daily note: {file_path}")
    tasks = extract_tasks(file_path)
    
    if not tasks:
        print("No incomplete tasks found.")
        send_line_notify(token, f"\n{datetime.date.today()}のタスクはありません。")
        return

    # Format the message
    message = f"\n【今日のタスク】 ({datetime.date.today()})\n"
    for i, task in enumerate(tasks, 1):
        message += f"{i}. {task}\n"
    
    send_line_notify(token, message)

if __name__ == "__main__":
    main()
