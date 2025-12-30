import feedparser
url = "https://ma-ji.ai/"
feed = feedparser.parse(url)
print(f"Bozo: {feed.bozo}")
print(f"Entries: {len(feed.entries)}")
for entry in feed.entries[:5]:
    print(f"Title: {entry.title}")
    print(f"Link: {entry.link}")
    print(f"Published: {entry.get('published_parsed')}")
