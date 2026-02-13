import os
import re
from datetime import timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../もくもく会logs/2026-01")
DAILY_LOG_FILE = os.path.join(LOG_DIR, "2026-01-21.md")
RANKING_FILE = os.path.join(LOG_DIR, "00_ランキング.md")

def parse_duration(time_str):
    """ 'HH:MM:SS' to timedelta """
    try:
        h, m, s = map(int, time_str.split(':'))
        return timedelta(hours=h, minutes=m, seconds=s)
    except ValueError:
        return timedelta(0)

def format_timedelta(td):
    """ timedelta to 'HH:MM:SS' """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def parse_daily_log(filepath):
    """ Extracts {user: time} from the daily log """
    print(f"Reading daily log: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {}
    # Handles "1位 12:34:56 @User" format
    # Logic extracted/adapted from analyze_ranking.py
    cleaned_text = re.sub(r'(\d+位)', r'\n\1', content)
    cleaned_text = re.sub(r'([🥇🥈🥉])', r'\n\1', cleaned_text)
    
    for line in cleaned_text.splitlines():
        # Match time and user. 
        # Line examples: 
        # "1位 09:08:10 @なかお＠nakaokt"
        # "🥇 12:21:57 @アマノナツメ@ama72me"
        # Regex needs to be robust.
        match = re.search(r'(\d{1,3}:\d{2}:\d{2})\s+(.+)', line)
        if match:
            time_str = match.group(1)
            user_part = match.group(2).strip()
            # Remove "Rank" prefix if it got captured (though regex above expects time first, usually rank is before time)
            # Actually the format in file is "Rank Time User" -> "1位 09:08:10 @..."
            # Wait, the regex `(\d{1,3}:\d{2}:\d{2})\s+(.+)` matches "09:08:10 @..." part if I don't anchor.
            
            # Let's try to match the time and everything after it.
            # In the file: "1位 09:08:10 @なかお..."
            # Split by space is risky if name has spaces.
            
            # Let's clean the rank part first
            # Remove leading "1位 " or "🥇 " etc.
            line_clean = re.sub(r'^\s*(?:\d+位|[🥇🥈🥉])\s*', '', line)
            # Now line starts with time: "09:08:10 @..."
            
            m2 = re.match(r'(\d{1,3}:\d{2}:\d{2})\s+(.+)', line_clean)
            if m2:
                time_str = m2.group(1)
                user_name = m2.group(2).strip()
                data[user_name] = parse_duration(time_str)
    return data

def parse_ranking_file(filepath):
    """ Extracts existing stats from 00_ランキング.md """
    print(f"Reading ranking file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    users = {}
    # Improve regex to handle the markdown table format
    # | Rank | Change | User | Total Time | Prev Time | Today's + |
    # | 1 | ➡️ | Name | 174:54:58 | 157:59:37 | +16:55:21 |
    
    rows = re.findall(r'\|\s*(\d+)\s*\|\s*.*?\s*\|\s*(.+?)\s*\|\s*(\d+:\d+:\d+)\s*\|', content)
    
    for rank, user, total_time in rows:
        users[user] = {
            'old_rank': int(rank),
            'old_total': parse_duration(total_time)
        }
    return users

def generate_ranking_markdown(stats, target_date_str="1月19日"):
    """ Generates the new markdown content """
    
    # Sort by total time desc
    sorted_users = sorted(stats.items(), key=lambda x: x[1]['total_time'], reverse=True)
    
    output = []
    output.append(f"# 2026年1月 (1日-{target_date_str}) もくもく会ランキング\n")
    
    # Takuya Analysis
    takuya_entry = next((item for item in sorted_users if "Takuya (@takuya_ta98)" in item[0]), None)
    if takuya_entry:
        user_name, data = takuya_entry
        rank = sorted_users.index(takuya_entry) + 1
        output.append(f"## User Analysis: Takuya (@takuya_ta98)")
        output.append(f"- Previous Rank (Jan 1-18): {data.get('old_rank', '-')}")
        output.append(f"- Current Rank (Jan 1-{target_date_str}): {rank}\n")
    
        # Neighbors Analysis
        output.append("### Neighbors Analysis")
        output.append("| Rank | Change | User | Total Time | Prev Time | Today's + |")
        output.append("| :--: | :--------: | :----------------------------- | :--------: | :-------: | :-------: |")
        
        start_idx = max(0, rank - 6) # show surrounding 10 users? original had ~10 rows
        end_idx = min(len(sorted_users), rank + 5)
        
        # Display logic for rows... shared with Full Ranking usually
        
        def format_row(r_idx, u_name, u_data):
            curr_rank = r_idx + 1
            old_rank = u_data.get('old_rank')
            
            change_icon = "🆕"
            if old_rank:
                if curr_rank < old_rank:
                    change_icon = f"⬆️ ({old_rank}→{curr_rank})"
                elif curr_rank > old_rank:
                    change_icon = f"⬇️ ({old_rank}→{curr_rank})"
                else:
                    change_icon = "➡️"
            
            total = format_timedelta(u_data['total_time'])
            prev = format_timedelta(u_data['old_total'])
            daily = format_timedelta(u_data['daily_time'])
            
            return f"| {curr_rank} | {change_icon} | {u_name} | {total} | {prev} | +{daily} |"

        for i in range(start_idx, end_idx):
             u_name, u_data = sorted_users[i]
             output.append(format_row(i, u_name, u_data))
        
        output.append("\n")

    output.append("## Full Ranking")
    output.append("| Rank | Change | User | Total Time | Prev Time | Today's + |")
    output.append("| :--: | :--------: | :----------------------------- | :--------: | :-------: | :-------: |")
    
    for i, (u_name, u_data) in enumerate(sorted_users):
        output.append(format_row(i, u_name, u_data))
        
    return "\n".join(output)

def main():
    if not os.path.exists(DAILY_LOG_FILE):
        print(f"Error: Daily log not found: {DAILY_LOG_FILE}")
        return
    if not os.path.exists(RANKING_FILE):
        print(f"Error: Ranking file not found: {RANKING_FILE}")
        return

    daily_data = parse_daily_log(DAILY_LOG_FILE)
    old_stats = parse_ranking_file(RANKING_FILE)
    
    # Merge Data
    all_users = set(daily_data.keys()) | set(old_stats.keys())
    final_stats = {}
    
    # Map user names if they vary slightly? 
    # For now assume strict equality or try simple normalization if needed.
    # The log file has "@takuya_ta98", ranking has "Takuya (@takuya_ta98)".
    # This is a mismatch problem! 
    # Log: "@Takuya@takuya_ta98" (from line 7: 6位 08:35:02 @Takuya@takuya_ta98)
    # Ranking: "Takuya (@takuya_ta98)"
    
    # We need a strategy to match users.
    # Strategy: Normalize by extracting the ID (part starting with @).
    # Re-build simple lookup map.
    
    def extract_id(text):
        # 1. Try to find explicit ID suffix like (@ama72me) or @ama72me
        # Capture the part inside () if it starts with @, OR the part after last @ if it is alphanumeric.
        
        # Helper to check if string looks like an ID (alphanumeric/underscore)
        def is_id_like(s):
            return re.match(r'^[a-zA-Z0-9_]+$', s) is not None

        # Pattern 1: "Name (@id)" -> id
        m1 = re.search(r'\(@([a-zA-Z0-9_]+)\)$', text)
        if m1:
            return m1.group(1)
            
        # Pattern 2: "@Name@id" -> id (last part is id if alphanumeric)
        # Split by @
        parts = [p for p in text.split('@') if p]
        if parts:
            possible_id = parts[-1]
            if is_id_like(possible_id):
                # But wait, "Name" could be alphanumeric too. "Takuya"
                # If "Takuya@takuya_ta98", parts=["Takuya", "takuya_ta98"]. Last is ID.
                # If "@たろ", parts=["たろ"]. Not ID like (Japanese).
                # If "@mochio_000", parts=["mochio_000"]. ID like.
                
                # Heuristic: If there are multiple parts, and last one is ID-like, use it.
                if len(parts) > 1:
                    return possible_id
                
                # If there is only one part: "@mochio_000" -> "mochio_000"
                # "@たろ" -> "たろ" (fails is_id_like)
                if is_id_like(possible_id):
                    return possible_id
        
        # Fallback: Treat the name itself as key (strip optional leading @)
        # "たろ" -> "たろ"
        # "@たろ" -> "たろ"
        clean = text.strip()
        if clean.startswith('@'):
            clean = clean[1:]
            
        # Remove any suffix like " (@...)" just in case we missed it or it wasn't captured above
        clean = re.sub(r'\s*\(@[a-zA-Z0-9_]+\)$', '', clean)
        
        return clean.strip()
    
    # Normalize Daily Data
    normalized_daily_data = {}
    for name, time_val in daily_data.items():
        uid = extract_id(name)
        # If multiple raw names map to same UID in daily log (unlikely but possible), sum them?
        # For now just set.
        normalized_daily_data[uid] = time_val
        # keep meaningful display name if it's a new user
        
    # Normalize Old Stats
    normalized_old_stats = {}
    for name, data in old_stats.items():
        uid = extract_id(name)
        normalized_old_stats[uid] = {**data, 'original_name': name}

    # Merge Data based on UIDs
    all_uids = set(normalized_daily_data.keys()) | set(normalized_old_stats.keys())
    final_stats = {}

    for uid in all_uids:
        daily_time = normalized_daily_data.get(uid, timedelta(0))
        old_user_data = normalized_old_stats.get(uid)
        
        if old_user_data:
            # User exists
            old_total = old_user_data['old_total']
            old_rank = old_user_data['old_rank']
            display_name = old_user_data['original_name']
        else:
            # New User - Try to find the original raw name from daily log to use as display name
            # We need to look back at daily_data to find the name that produced this uid
            # A bit inefficient but fine for small list
            original_name = next((n for n in daily_data if extract_id(n) == uid), uid)
            
            old_total = timedelta(0)
            old_rank = None
            display_name = original_name 
            
        total_time = old_total + daily_time
        
        final_stats[display_name] = {
            'total_time': total_time,
            'old_total': old_total,
            'daily_time': daily_time,
            'old_rank': old_rank
        }

    markdown = generate_ranking_markdown(final_stats, "21日")
    
    # Write to file
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Updated {RANKING_FILE}")

if __name__ == "__main__":
    main()
