import feedparser
import datetime
import pytz
import os
from deep_translator import GoogleTranslator

# RSS Feed URLs
RSS_FEEDS = {
    "ledge": "https://ledge.ai/feed/",
    "ainow": "https://ainow.ai/feed/",
    "itmedia_ai": "https://www.itmedia.co.jp/rss/2.0/ait.xml",
    "techcrunch": "https://techcrunch.com/feed/",
    "wired_jp": "https://wired.jp/rss/",
    "gihyo": "https://gihyo.jp/feed/rss2",
    "codezine": "https://codezine.jp/rss/new/20/index.xml"
}

# Feeds that need translation (English sources)
ENGLISH_FEEDS = ["techcrunch"]

def clean_summary(summary):
    """Remove HTML tags and extra whitespace from summary."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(summary, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text

def fetch_rss_feeds():
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)
    yesterday = now - datetime.timedelta(hours=24)
    
    # Initialize translator
    translator = GoogleTranslator(source='auto', target='ja')

    # Create content for Markdown
    content = f"# RSS Feeds ({now.strftime('%Y-%m-%d %H:%M')})\n\n"
    current_date_str = now.strftime('%Y-%m-%d')
    
    has_updates = False

    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            entries = []
            
            for entry in feed.entries:
                # Parse publication date
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                     published_time = datetime.datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime.datetime(*entry.updated_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                
                if published_time and published_time > yesterday:
                    entries.append(entry)
            
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
                    if name in ENGLISH_FEEDS:
                        try:
                            # Translate title
                            translated_title = translator.translate(title)
                            
                            content += f"- [{translated_title}]({link}) ({published})\n"
                            content += f"    - **Original**: {title}\n"
                            
                            # Translate summary if it exists and is long enough
                            if summary_text and len(summary_text) > 10:
                                # Truncate summary to avoid too long requests usually 5000 chars limit, but for summary 300-500 is enough
                                if len(summary_text) > 500:
                                    summary_text = summary_text[:500] + "..."
                                translated_summary = translator.translate(summary_text)
                                content += f"    - **Summary**: {translated_summary}\n"
                        except Exception as e:
                            print(f"Translation failed for {title}: {e}")
                            # Fallback to original
                            content += f"- [{title}]({link}) ({published})\n"
                            if summary_text:
                                content += f"    - **Summary**: {summary_text}\n"

                    else:
                        # Japanese feeds
                        content += f"- [{title}]({link}) ({published})\n"
                        if summary_text and len(summary_text) > 20: # Short filter
                             # Sometimes summary is just a repeat of title or empty
                             if summary_text != title:
                                if len(summary_text) > 200:
                                    summary_text = summary_text[:200] + "..."
                                content += f"    - **Summary**: {summary_text}\n"

                content += "\n"
                
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    if not has_updates:
        content += "No new articles in the last 24 hours.\n"

    # Ensure RSS directory exists
    output_dir = "毎日のAIニュース取得"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save to file
    filename = os.path.join(output_dir, f"{current_date_str}_RSS_Feed.md")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully finished RSS fetch. Saved to {filename}")

if __name__ == "__main__":
    fetch_rss_feeds()
