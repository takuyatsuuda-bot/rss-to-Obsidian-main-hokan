import os
import re
import argparse
from datetime import datetime, timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_ROOT_DIR = os.path.join(BASE_DIR, "../もくもく会logs")

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
    
    # Pre-cleaning
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

def get_target_files(month_dir):
    """ Get all YYYY-MM-DD.md files in the directory, sorted by date """
    if not os.path.exists(month_dir):
        return []
        
    files = []
    for f in os.listdir(month_dir):
        if re.match(r'\d{4}-\d{2}-\d{2}\.md$', f):
            files.append(f)
            
    return sorted(files)

def main():
    parser = argparse.ArgumentParser(description='Update monthly ranking.')
    parser.add_argument('--month', type=str, help='Target month in YYYY-MM format (e.g. 2026-02)', default=None)
    args = parser.parse_args()

    # Determine Target Directory
    if args.month:
        target_month = args.month
    else:
        # Default to current month
        now = datetime.now()
        target_month = now.strftime('%Y-%m')

    # Handle directory selection logic if not explicitly passed
    # If explicit passed, verify. If default, verify.
    target_dir = os.path.join(LOGS_ROOT_DIR, target_month)
    
    if not os.path.exists(target_dir):
        # If current month doesn't exist, try previous month just in case? Or just fail.
        # Let's try to be smart, if we are at day 1 of month, maybe we want previous month?
        # For now, just error out if not found.
        print(f"Directory not found: {target_dir}")
        return

    print(f"Target Month Directory: {target_dir}")

    target_files = get_target_files(target_dir)
    if not target_files:
        print("No daily logs found.")
        return
        
    print(f"Found {len(target_files)} log files: {target_files}")

    output_file_name = f"00_{int(target_month.split('-')[1])}月ランキング.md"
    output_file_path = os.path.join(target_dir, output_file_name)

    aggregated_data = {} # {uid: {'total_time': td, 'name': original_name}}
    previous_data = {}   # {uid: {'total_time': td}}
    today_data = {}      # {uid: td}
    
    # 1. First Pass: Filter out empty files
    valid_files = []
    for filename in target_files:
        path = os.path.join(target_dir, filename)
        daily_map = parse_daily_log(path)
        if daily_map:
            valid_files.append((filename, daily_map))
        else:
            print(f"Skipping empty/no-data file: {filename}")

    if not valid_files:
        print("No valid data found in logs.")
        return

    # 1. Aggregate Data from Valid Files
    for i, (filename, daily_map) in enumerate(valid_files):
        is_today = (i == len(valid_files) - 1)
        
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
            else:
                today_data[uid] = duration
            
            # Keep newest name
            aggregated_data[uid]['name'] = name

    # 2. Calculate Previous Ranks
    sorted_prev = sorted(previous_data.items(), key=lambda x: x[1]['total_time'], reverse=True)
    prev_ranks = {} # uid -> rank (1-based)
    for i, (uid, _) in enumerate(sorted_prev):
        prev_ranks[uid] = i + 1

    # 3. Calculate Current Ranks and Generate MD
    sorted_users = sorted(aggregated_data.values(), key=lambda x: x['total_time'], reverse=True)
    
    lines = []
    lines.append(f"# 🏆 {target_month.replace('-', '年')}月 もくもく会 月間累計ランキング")
    lines.append("")
    
    start_date = valid_files[0][0].replace(".md", "")
    end_date = valid_files[-1][0].replace(".md", "")
    day_count = len(valid_files)
    lines.append(f"**集計期間**: {start_date} 〜 {end_date} (全{day_count}日間)")
    lines.append("")
    
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
            change_str = "🆕"
        else:
            diff = prev_rank - current_rank
            if diff > 0:
                change_str = f"⬆️ {diff}" 
            elif diff < 0:
                change_str = f"⬇️ {abs(diff)}"
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
        
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
        
    print(f"Successfully wrote to {output_file_path}")

if __name__ == "__main__":
    main()
