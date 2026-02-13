import os
import re
from datetime import timedelta
import glob

# ==========================================
# 設定：あなたのフォルダ構成に合わせました
# ==========================================
# スクリプト(scriptsフォルダ)から見て、一つ上の階層にある 'もくもく会logs' を見に行く
LOG_DIR = "../もくもく会logs"
# 集計結果を書き出すファイル（20_Brainサロンフォルダ直下に作ります）
OUTPUT_FILE = "../summary.md"

def parse_duration(time_str):
    """ 'HH:MM:SS' 文字列を timedelta オブジェクトに変換 """
    h, m, s = map(int, time_str.split(':'))
    return timedelta(hours=h, minutes=m, seconds=s)

def format_timedelta(td):
    """ timedelta を 'HH時間 MM分 SS秒' 形式の文字列に変換 """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def clean_and_extract_data(text):
    """ 
    テキストの表記揺れ（改行なし問題）を整形してデータを抽出する
    """
    data = []
    
    # "4位" や "10位" などのパターンの前に強制的に改行を入れる
    cleaned_text = re.sub(r'(\d+位)', r'\n\1', text)
    
    # 行ごとに解析
    for line in cleaned_text.splitlines():
        # 正規表現: 時間(HH:MM:SS) + スペース + ユーザー名
        match = re.search(r'(\d{1,2}:\d{2}:\d{2})\s+(.+)', line)
        if match:
            time_str = match.group(1)
            # ユーザー名から余計な順位表記などを除去
            user_name = match.group(2).strip()
            user_name = re.sub(r'\s*\d+位.*', '', user_name)
            
            data.append((user_name, time_str))
            
    return data

def main():
    # パスの確認（デバッグ用）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, LOG_DIR)
    
    print(f"現在の場所: {current_dir}")
    print(f"ログを探す場所: {target_dir}")

    user_stats = {} 

    # 1. ログファイルの読み込み
    log_files = glob.glob(os.path.join(target_dir, "*.md"))
    
    if not log_files:
        print("⚠️ 注意: .mdファイルが見つかりませんでした。")
        print(f"'{target_dir}' にランキングをコピペしたmdファイルがあるか確認してください。")
        return

    print(f"集計対象ファイル数: {len(log_files)}")

    for filepath in log_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            extracted = clean_and_extract_data(content)
            
            for user, time_str in extracted:
                td = parse_duration(time_str)
                if user in user_stats:
                    user_stats[user] += td
                else:
                    user_stats[user] = td

    # 2. 集計とソート
    sorted_stats = sorted(user_stats.items(), key=lambda x: x[1], reverse=True)

    # 3. Markdown生成
    md_output = "# 🏆 もくもく会 月間累計ランキング\n\n"
    md_output += f"データ更新日: {os.path.basename(log_files[-1])} 時点\n\n"
    md_output += "| 順位 | 名前 | 累計時間 |\n"
    md_output += "| :--- | :--- | :--- |\n"

    for rank, (user, total_time) in enumerate(sorted_stats, 1):
        formatted_time = format_timedelta(total_time)
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}位"
        md_output += f"| {medal} | {user} | {formatted_time} |\n"

    # 4. ファイル書き出し
    output_path = os.path.join(current_dir, OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_output)
    
    print(f"✅ 集計完了！ '{output_path}' に結果を書き出しました。")

if __name__ == "__main__":
    main()
    