#!/bin/bash

# Ensure correct path (add user python bin and standard paths)
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/ttdesign/Library/Python/3.9/bin:$PATH

# Directory where the script lives
SCRIPT_DIR="/Users/ttdesign/Library/Mobile Documents/iCloud~md~obsidian/Documents/Main保管庫/11_Instagram運用代行_Tobu/04_フォロワー数推移"

cd "$SCRIPT_DIR"

# Run the python script
# Using python3 (assuming it's in the path or using system python)
python3 monitor_followers.py >> monitor_run.log 2>&1
