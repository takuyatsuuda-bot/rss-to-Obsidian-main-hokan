import feedparser
import datetime
import pytz
import os
from deep_translator import GoogleTranslator
import google.generativeai as genai

# RSS Feed URLs
RSS_FEEDS = {
    "ledge": "https://ledge.ai/feed/",
    "ainow": "https://ainow.ai/feed/",
    "itmedia_ai": "https://www.itmedia.co.jp/rss/2.0/ait.xml",
    "techcrunch": "https://techcrunch.com/feed/",
    "wired_jp": "https://wired.jp/rss/",
    "gihyo": "https://gihyo.jp/feed/rss2",
    "codezine": "https://codezine.jp/rss/new/20/index.xml",
    "shift_ai": "https://shift-ai.co.jp/blog/feed/",
    "ai_sokuho": "https://aisokuho.com/feed/"
}

# Feeds that need translation (English sources)
ENGLISH_FEEDS = ["techcrunch"]

def clean_summary(summary):
    """Remove HTML tags and extra whitespace from summary."""
    from bs4 import BeautifulSoup
    try:
        soup = BeautifulSoup(summary, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text
    except:
        return summary

def generate_curated_news(articles, date_str):
    """Generate curated news using Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment variables. Curation skipped.")
        return

    print("GEMINI_API_KEY found. Configuring GenAI...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        print("Model configured.")
        
        # Prepare article list for prompt
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"{i}. Title: {article['title']}\n   Link: {article['link']}\n   Summary: {article['summary'][:200]}...\n\n"
            
        prompt = f"""
        あなたは経験豊富なAIエンジニア兼テックジャーナリストです。
        以下の今日のAI関連ニュース記事リストから、特にエンジニアや研究者にとって重要で注目すべき記事を「5つだけ」選んでください。
        
        それぞれの記事について、以下のフォーマットでMarkdown形式で出力してください。
        
        ## [記事タイトル](URL)
        - **要約**: (記事の要約を日本語で簡潔に。3行程度)
        - **おすすめ理由**: (なぜこの記事が重要なのか、技術的観点や業界への影響を踏まえた解説を日本語で。3行程度)
        - **媒体**: (記事の配信元サイト名)
        
        条件:
        - 必ず5つ選んでください。
        - 専門的な視点を含めてください。
        - 出力は見やすく整形してください。
        
        ニュースリスト:
        {articles_text}
        """
        
        response = model.generate_content(prompt)
        curated_content = f"# 今日の注目ニュース ({date_str})\n\n" + response.text
        
        # Ensure directory exists
        output_dir = "01_今日の注目ニュース"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = os.path.join(output_dir, f"{date_str}_Featured.md")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(curated_content)
        print(f"Successfully generated curated news: {filename}")
        
    except Exception as e:
        print(f"Error generating curated news: {e}")
        error_log = f"# Error Log ({datetime.datetime.now()})\n\nError generating curated news:\n{str(e)}"
        
        # Ensure directory exists (even if generation failed)
        output_dir = "01_今日の注目ニュース"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        error_filename = os.path.join(output_dir, "Error_Log.md")
        with open(error_filename, 'w', encoding='utf-8') as f:
            f.write(error_log)

def fetch_rss_feeds(target_date=None):
    jst = pytz.timezone('Asia/Tokyo')
    if target_date:
        now = target_date
    else:
        now = datetime.datetime.now(jst)
    
    yesterday = now - datetime.timedelta(hours=24)
    
    # Initialize translator
    translator = GoogleTranslator(source='auto', target='ja')

    # Create content for Markdown
    content = f"# RSS Feeds ({now.strftime('%Y-%m-%d %H:%M')})\n\n"
    current_date_str = now.strftime('%Y-%m-%d')
    
    has_updates = False
    all_articles = [] # Store all fetched articles for curation

    # Load previous day's URLs to prevent duplicates
    seen_urls = set()
    prev_filename = os.path.join("00_毎日のAIニュース取得", f"{yesterday.strftime('%Y-%m-%d')}_RSS_Feed.md")
    if os.path.exists(prev_filename):
        try:
            with open(prev_filename, 'r', encoding='utf-8') as f:
                prev_content = f.read()
                # Simple extraction of markdown links: ](url)
                import re
                links = re.findall(r'\]\((https?://[^)]+)\)', prev_content)
                seen_urls.update(links)
            print(f"Loaded {len(seen_urls)} URLs from yesterday's file for deduplication.")
        except Exception as e:
            print(f"vWarning: Could not read previous file for deduplication: {e}")

    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            entries = []
            
            # Check more entries to find eligible ones after filtering
            for entry in feed.entries[:20]: 
                # Parse publication date for display
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                     published_time = datetime.datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime.datetime(*entry.updated_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                
                # Filter by date (within last 24 hours)
                if published_time:
                    if published_time < yesterday:
                        continue
                    if published_time > now: # Skip future posts if any
                        continue
                
                # Deduplicate against yesterday's file
                if entry.link in seen_urls:
                    continue

                entries.append(entry)
                if len(entries) >= 5:
                    break
            
            if entries:
                has_updates = True
                content += f"## {name}\n"
                for entry in entries:
                    title = entry.title
                    link = entry.link
                    published = ""
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                         dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                         published = dt.strftime('%H:%M')
                    
                    # summary acquisition
                    summary_text = ""
                    if hasattr(entry, 'summary'):
                        summary_text = clean_summary(entry.summary)
                    elif hasattr(entry, 'description'):
                        summary_text = clean_summary(entry.description)

                    # Translation logic
                    translated_title = title
                    translated_summary = summary_text

                    if name in ENGLISH_FEEDS:
                        try:
                            # Translate title
                            translated_title = translator.translate(title)
                            
                            content += f"- [{translated_title}]({link}) ({published})\n"
                            content += f"    - **Original**: {title}\n"
                            
                            # Translate summary if it exists and is long enough
                            if summary_text and len(summary_text) > 10:
                                if len(summary_text) > 500:
                                    summary_text = summary_text[:500] + "..."
                                translated_summary = translator.translate(summary_text)
                                content += f"    - **Summary**: {translated_summary}\n"
                            else:
                                translated_summary = ""
                        except Exception as e:
                            print(f"Translation failed for {title}: {e}")
                            content += f"- [{title}]({link}) ({published})\n"
                            if summary_text:
                                content += f"    - **Summary**: {summary_text}\n"
                    else:
                        # Japanese feeds
                        content += f"- [{title}]({link}) ({published})\n"
                        if summary_text and len(summary_text) > 20: 
                             if summary_text != title:
                                if len(summary_text) > 200:
                                    summary_text = summary_text[:200] + "..."
                                content += f"    - **Summary**: {summary_text}\n"

                    # Store article info for curation
                    article_data = {
                        "title": translated_title,
                        "link": link,
                        "summary": translated_summary if translated_summary else summary_text,
                        "source": name
                    }
                    all_articles.append(article_data)

                content += "\n"
                
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    if not has_updates:
        content += "No new articles in the last 24 hours.\n"

    # Ensure RSS directory exists
    output_dir = "00_毎日のAIニュース取得"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save to file
    filename = os.path.join(output_dir, f"{current_date_str}_RSS_Feed.md")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully finished RSS fetch. Saved to {filename}")

    print(f"Total articles found for curation: {len(all_articles)}")

    # Generate curated news
    if all_articles:
        print(f"Starting curation with Gemini at {datetime.datetime.now()}...")
        generate_curated_news(all_articles, current_date_str)
    else:
        print("No articles found to curate.")

    print("No articles found to curate.")

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Fetch RSS feeds.')
    parser.add_argument('--date', type=str, help='Target date in YYYY-MM-DD format')
    args = parser.parse_args()

    target_date = None
    if args.date:
        try:
            # Set target time to 08:00 JST on the specified date to match cron schedule
            date_obj = datetime.datetime.strptime(args.date, '%Y-%m-%d')
            jst = pytz.timezone('Asia/Tokyo')
            target_date = jst.localize(date_obj.replace(hour=8, minute=0, second=0, microsecond=0))
            print(f"Running for target date: {target_date}")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    fetch_rss_feeds(target_date)
