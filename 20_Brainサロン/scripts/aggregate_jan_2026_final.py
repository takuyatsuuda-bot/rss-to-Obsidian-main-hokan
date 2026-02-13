import os
import re
import glob
from datetime import timedelta

# ==========================================
# Configuration
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Logs are in ../もくもく会logs/2026-01
LOG_DIR = os.path.join(BASE_DIR, "../もくもく会logs/2026-01")
OUTPUT_FILE = os.path.join(LOG_DIR, "00_ランキング.md")

def parse_duration(time_str):
    """ 'HH:MM:SS' -> timedelta """
    try:
        h, m, s = map(int, time_str.split(':'))
        return timedelta(hours=h, minutes=m, seconds=s)
    except ValueError:
        return timedelta(0)

def format_timedelta(td):
    """ timedelta -> 'HH:MM:SS' """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def clean_username_key(raw_name):
    """
    Normalize user name to a unique key (UID).
    """
    # 0. Pre-clean the raw name to remove artifacts that confuse ID extraction
    # Remove trailing markdown characters or common noise
    clean = raw_name.strip()
    clean = re.sub(r'\s*!\[.*$', '', clean) # Remove image links starts
    clean = re.sub(r'\s*\*\*.*$', '', clean) # Remove bold suffixes
    clean = re.sub(r'\s*\(.*\)$', '', clean) # Remove trailing parenthesis
    
    # 1. "Name (@id)" -> id
    m1 = re.search(r'\(@([a-zA-Z0-9_]+)\)$', clean)
    if m1:
        return m1.group(1)
        
    # 2. "@Name@id" -> id
    parts = [p for p in clean.split('@') if p]
    if parts:
        possible_id = parts[-1]
        if re.match(r'^[a-zA-Z0-9_]+$', possible_id):
            if len(parts) > 1:
                return possible_id
            # If only one part and looks like ID, use it
            return possible_id
            
    # Fallback: use cleaned name
    if clean.startswith('@'):
        clean = clean[1:]
    clean = re.sub(r'\s*\(@[a-zA-Z0-9_]+\)$', '', clean)
    
    return clean.strip()

def parse_daily_log(filepath):
    """ 
    Extracts time for each user from a single daily log file.
    Returns: list of (raw_name, timedelta)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strategy: Insert a newline before every timestamp pattern.
    # This separates "Time User..." segments effectively.
    # Pattern: HH:MM:SS or H:MM:SS
    # Use capturing group to keep the time.
    # Note: Regex text replacement.
    
    # 1. Normalize timestamps to have newlines before them
    # We look for something that looks like a time: \d{1,2}:\d{2}:\d{2}
    # We replace it with \n\1
    cleaned_content = re.sub(r'(\d{1,2}:\d{2}:\d{2})', r'\n\1', content)

    entries = []
    
    for line in cleaned_content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        # Match "HH:MM:SS User..."
        # We expect the line to START with the time now (or close to it if there was garbage, but we put \n before time)
        # Actually \n\1 makes the line start with time.
        
        match = re.search(r'^(\d{1,3}:\d{2}:\d{2})\s+(.+)', line)
        if match:
            time_str = match.group(1)
            user_part = match.group(2).strip()
            entries.append((user_part, parse_duration(time_str)))
            
    return entries

def main():
    print(f"Log Directory: {LOG_DIR}")
    
    # 1. Collect all monthly log files
    log_files = glob.glob(os.path.join(LOG_DIR, "2026-01-*.md"))
    log_files.sort()
    
    if not log_files:
        print("No log files found!")
        return

    print(f"Found {len(log_files)} log files. Processing...")

    # 2. Aggregation
    # keys: uid, values: { 'total_time': timedelta, 'display_name': str }
    user_stats = {}

    for filepath in log_files:
        filename = os.path.basename(filepath)
        # Skip the output file itself if it matches the pattern (it shouldn't due to date check, but safety first)
        if filename == "00_ランキング.md":
            continue
            
        daily_entries = parse_daily_log(filepath)
        
        # DEBUG
        if filename == "2026-01-01.md":
            print(f"DEBUG: Entries found in {filename}: {len(daily_entries)}")
            for d_name, d_time in daily_entries:
                if 'ama' in d_name:
                    print(f"  -> Found ama: {d_name} {d_time}")
            
        for raw_name, duration in daily_entries:
            uid = clean_username_key(raw_name)
            
            # Clean raw_name for display purposes too (remove ** and similar but keep @)
            clean_disp = raw_name.strip()
            clean_disp = re.sub(r'\s*!\[.*$', '', clean_disp)
            clean_disp = re.sub(r'\s*\*\*.*$', '', clean_disp)
            clean_disp = re.sub(r'\s*\(.*\)$', '', clean_disp)
             # Remove suffix like " (@...)" just in case if we want shorter names? 
             # No, keep " (@id)" for display if present, but remove extra junk.
            
            if uid not in user_stats:
                user_stats[uid] = {
                    'total_time': timedelta(0),
                    'display_name': clean_disp 
                }
            
            # Update time
            user_stats[uid]['total_time'] += duration
            
            # Update display name if current one is 'cleaner' or 'longer' (contains ID)?
            curr_disp = user_stats[uid]['display_name']
            
            # Prefer name with ID (@...) over without
            if '(@' in clean_disp and '(@' not in curr_disp:
                user_stats[uid]['display_name'] = clean_disp
            # If currently using a name with " **" (if logic failed) ... but we cleaned it above.
            
            # If current display name is just ID (e.g. 'ama72me') and we found a 'nicer' one '@アマノナツメ@ama72me', use it.
            # If current display name is just ID (e.g. 'ama72me') and we found a 'nicer' one '@アマノナツメ@ama72me', use it.
            # Heuristic: if new length > old length + 2 ...
            if len(clean_disp) > len(curr_disp) + 2 and '@' in clean_disp:
                 user_stats[uid]['display_name'] = clean_disp

    # 3. Sort
    # Convert to list
    ranking_list = []
    for uid, data in user_stats.items():
        ranking_list.append((data['display_name'], data['total_time']))
    
    # Sort by time desc
    ranking_list.sort(key=lambda x: x[1], reverse=True)

    # 4. Generate Markdown
    md_output = []
    md_output.append("# 🏆 2026年1月 もくもく会 月間累計ランキング")
    md_output.append("")
    md_output.append(f"**集計期間**: 2026-01-01 〜 2026-01-31 (全31日間)")
    md_output.append("")
    md_output.append("| 順位 | 名前 | 累計時間 |")
    md_output.append("| :--- | :--- | :--- |")

    for i, (name, total_time) in enumerate(ranking_list, 1):
        time_str = format_timedelta(total_time)
        
        # Medals
        rank_str = f"{i}位"
        if i == 1: rank_str = "🥇"
        elif i == 2: rank_str = "🥈"
        elif i == 3: rank_str = "🥉"
        
        md_output.append(f"| {rank_str} | {name} | {time_str} |")
    
    md_output.append("")
    
    # 5. Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_output))
        
    print(f"✅ Successfully wrote monthly ranking to: {OUTPUT_FILE}")
    print(f"Total users ranked: {len(ranking_list)}")
    print("Top 3:")
    for i in range(min(3, len(ranking_list))):
        name, t = ranking_list[i]
        print(f" {i+1}. {name}: {format_timedelta(t)}")

if __name__ == "__main__":
    main()
