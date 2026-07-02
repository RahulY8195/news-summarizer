import re
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import feedparser

GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search"


def fetch_articles(query: str = "technology", page_size: int = 10) -> list[dict]:
    encoded_query = quote(query)
    feed = feedparser.parse(
        f"{GOOGLE_NEWS_RSS_URL}?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    )

    results = []
    for entry in feed.entries[:page_size]:
        if not entry.get("link"):
            continue

        summary = re.sub(r"<[^>]+>", "", entry.get("summary", "")).strip()
        content = summary or entry.get("title", "")

        published_at = None
        if entry.get("published"):
            published_at = parsedate_to_datetime(entry["published"])

        source = entry.get("source", {}).get("title", "Google News")

        results.append({
            "title": entry.get("title", "Untitled"),
            "source": source,
            "url": entry["link"],
            "published_at": published_at,
            "content": content,
        })
    return results
