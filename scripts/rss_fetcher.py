import feedparser
import datetime
import pytz
import os

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

def fetch_rss_feeds():
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)
    yesterday = now - datetime.timedelta(hours=24)
    
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
                if hasattr(entry, 'published_parsed'):
                     published_time = datetime.datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                elif hasattr(entry, 'updated_parsed'):
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
                    if hasattr(entry, 'published_parsed'):
                         dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                         published = dt.strftime('%H:%M')
                    
                    content += f"- [{title}]({link}) ({published})\n"
                content += "\n"
                
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    if not has_updates:
        content += "No new articles in the last 24 hours.\n"

    # Ensure RSS directory exists
    output_dir = "RSS"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save to file
    filename = os.path.join(output_dir, f"{current_date_str}_RSS_Feed.md")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully finished RSS fetch. Saved to {filename}")

if __name__ == "__main__":
    fetch_rss_feeds()
