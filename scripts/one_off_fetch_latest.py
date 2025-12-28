import feedparser
import datetime
import pytz
import os
from deep_translator import GoogleTranslator

# RSS Feed URLs (Updated list)
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

def fetch_rss_feeds():
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)
    
    # Initialize translator
    translator = GoogleTranslator(source='auto', target='ja')

    # Create content for Markdown
    content = f"# RSS Feeds (Latest 5) ({now.strftime('%Y-%m-%d %H:%M')})\n\n"
    current_date_str = now.strftime('%Y-%m-%d')
    
    for name, url in RSS_FEEDS.items():
        try:
            print(f"Fetching {name}...")
            feed = feedparser.parse(url)
            entries = feed.entries[:5] # Limit to 5
            
            if entries:
                content += f"## {name}\n"
                for entry in entries:
                    title = entry.title
                    link = entry.link
                    published = ""
                    
                    # Try to parse date for display, but don't filter by it
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                         dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                         published = dt.strftime('%Y-%m-%d %H:%M')
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                         dt = datetime.datetime(*entry.updated_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                         published = dt.strftime('%Y-%m-%d %H:%M')
                    
                    # summary acquisition
                    summary_text = ""
                    if hasattr(entry, 'summary'):
                        summary_text = clean_summary(entry.summary)
                    elif hasattr(entry, 'description'):
                        summary_text = clean_summary(entry.description)

                    # Translation logic
                    if name in ENGLISH_FEEDS:
                        try:
                            # Translate title
                            translated_title = translator.translate(title)
                            
                            content += f"- [{translated_title}]({link}) ({published})\n"
                            content += f"    - **Original**: {title}\n"
                            
                            # Translate summary if it exists
                            if summary_text and len(summary_text) > 10:
                                if len(summary_text) > 500:
                                    summary_text = summary_text[:500] + "..."
                                translated_summary = translator.translate(summary_text)
                                content += f"    - **Summary**: {translated_summary}\n"
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

                content += "\n"
                
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            content += f"## {name}\nError fetching feed: {e}\n\n"

    # Ensure output directory exists (using Japanese name)
    output_dir = "毎日のAIニュース取得"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save to file (Overwriting today's file)
    filename = os.path.join(output_dir, f"{current_date_str}_RSS_Feed.md")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully finished RSS fetch. Saved to {filename}")

if __name__ == "__main__":
    fetch_rss_feeds()
