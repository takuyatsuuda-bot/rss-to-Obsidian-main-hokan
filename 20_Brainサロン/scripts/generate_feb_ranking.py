import os
import re
from datetime import timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../もくもく会logs/2026-02")
OUTPUT_FILE = os.path.join(LOG_DIR, "00_2月ランキング.md")
TARGET_FILES = ["2026-02-01.md", "2026-02-02.md", "2026-02-03.md", "2026-02-04.md", "2026-02-05.md"]

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
    
    # Pre-cleaning similar to existing script
    cleaned_text = re.sub(r'(\d+位)', r'\n\1', content)
    cleaned_text = re.sub(r'([🥇🥈🥉])', r'\n\1', cleaned_text)
    
    for line in cleaned_text.splitlines():
        # Clean rank/medals
        line_clean = re.sub(r'^\s*(?:\d+位|[🥇🥈🥉])\s*', '', line)
        
        # Match time and user: "09:08:10 @User..."
        m = re.match(r'(\d{1,3}:\d{2}:\d{2})\s+(.+)', line_clean)
        if m:
            time_str = m.group(1)
            user_name = m.group(2).strip()
            data[user_name] = parse_duration(time_str)
            
    return data

def extract_id(text):
    """ Extract stable ID from name string """
    # 1. Try (@id)
    m1 = re.search(r'\(@([a-zA-Z0-9_]+)\)$', text)
    if m1: return m1.group(1)
        
    # 2. Try @Name@id or @id
    parts = [p for p in text.split('@') if p]
    
    def is_id_like(s):
        return re.match(r'^[a-zA-Z0-9_]+$', s) is not None

    if parts:
        possible_id = parts[-1]
        if len(parts) > 1:
            return possible_id
        if is_id_like(possible_id):
            return possible_id
            
    # Fallback
    clean = text.strip()
    if clean.startswith('@'): clean = clean[1:]
    clean = re.sub(r'\s*\(@[a-zA-Z0-9_]+\)$', '', clean)
    return clean.strip()

def main():
    aggregated_data = {} # {uid: {'total_time': td, 'name': original_name}}
    previous_data = {}   # {uid: {'total_time': td}}
    today_data = {}      # {uid: td}
    
    # 1. Aggregate Data
    for i, filename in enumerate(TARGET_FILES):
        path = os.path.join(LOG_DIR, filename)
        if not os.path.exists(path):
            print(f"Warning: {filename} not found")
            continue
            
        daily_map = parse_daily_log(path)
        is_today = (i == len(TARGET_FILES) - 1)
        
        for name, duration in daily_map.items():
            uid = extract_id(name)
            
            # Global Total
            if uid not in aggregated_data:
                aggregated_data[uid] = {'total_time': timedelta(0), 'name': name}
            aggregated_data[uid]['total_time'] += duration
            
            # Previous Total (All days except the last one)
            if not is_today:
                if uid not in previous_data:
                    previous_data[uid] = {'total_time': timedelta(0)}
                previous_data[uid]['total_time'] += duration
            
            # Today's Data (Only the last file)
            else:
                today_data[uid] = duration
            
            # Keep newest name (optional, but good for display)
            aggregated_data[uid]['name'] = name

    # 2. Calculate Previous Ranks
    # Sort previous data to determine ranks before today
    sorted_prev = sorted(previous_data.items(), key=lambda x: x[1]['total_time'], reverse=True)
    prev_ranks = {} # uid -> rank (1-based)
    for i, (uid, _) in enumerate(sorted_prev):
        prev_ranks[uid] = i + 1

    # 3. Calculate Current Ranks and Generate MD
    sorted_users = sorted(aggregated_data.values(), key=lambda x: x['total_time'], reverse=True)
    
    lines = []
    lines.append("# 🏆 2026年2月 もくもく会 月間累計ランキング")
    lines.append("")
    # Calculate day range dynamically for display if needed, or keep hardcoded/adjusted
    start_date = TARGET_FILES[0].replace(".md", "")
    end_date = TARGET_FILES[-1].replace(".md", "")
    day_count = len(TARGET_FILES)
    lines.append(f"**集計期間**: {start_date} 〜 {end_date} (全{day_count}日間)")
    lines.append("")
    
    # Updated Table Header
    lines.append("| 順位 | 変動 | 名前 | 累計時間 | 前日差 |")
    lines.append("| :--- | :---: | :--- | :--- | :--- |")
    
    for i, user_data in enumerate(sorted_users):
        current_rank = i + 1
        name = user_data['name']
        uid = extract_id(name)
        total_time_str = format_timedelta(user_data['total_time'])
        
        # Rank Change Logic
        prev_rank = prev_ranks.get(uid)
        if prev_rank is None:
            # New entry (didn't exist in previous days)
            change_str = "🆕"
        else:
            diff = prev_rank - current_rank
            if diff > 0:
                change_str = f"⬆️ {diff}" # Rank improved (e.g. 5 -> 3, diff=2)
            elif diff < 0:
                change_str = f"⬇️ {abs(diff)}" # Rank dropped (e.g. 3 -> 5, diff=-2)
            else:
                change_str = "➡️"
        
        # Daily Increment Logic
        daily_increment = today_data.get(uid, timedelta(0))
        daily_str = format_timedelta(daily_increment)
        daily_display = f"+{daily_str}"
        
        # Rank formatting
        if current_rank == 1: r_str = "🥇"
        elif current_rank == 2: r_str = "🥈"
        elif current_rank == 3: r_str = "🥉"
        else: r_str = f"{current_rank}位"
        
        lines.append(f"| {r_str} | {change_str} | {name} | {total_time_str} | {daily_display} |")
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
        
    print(f"Successfully wrote to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
