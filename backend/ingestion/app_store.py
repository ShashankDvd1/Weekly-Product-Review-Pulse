import requests
import pandas as pd
from datetime import datetime
import feedparser

def fetch_app_store_reviews(app_id: str, from_date: str, to_date: str, country: str = 'in', max_pages: int = 10) -> pd.DataFrame:
    """
    Fetches reviews from the Apple App Store using the iTunes XML RSS feed.
    max_pages: iTunes RSS only allows up to 10 pages (500 reviews total).
    """
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    all_reviews = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    for page in range(1, max_pages + 1):
        if page > 1:
            import time
            time.sleep(1.0)  # Sleep between pages to avoid Apple RSS rate limiting
            
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/sortBy=mostRecent/id={app_id}/xml"
            
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                break
                
            feed = feedparser.parse(response.content)
            entries = feed.entries
            if not entries:
                # Apple RSS often returns 200 but empty feed when throttled. Retry once after 2 seconds.
                import time
                time.sleep(2.0)
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    entries = feed.entries
                    
            if not entries:
                break
                
            for entry in entries:
                rating_str = entry.get('im_rating')
                if not rating_str:
                    continue
                    
                review_text = entry.get('summary', '')
                author = entry.get('author', 'Unknown')
                rating = int(rating_str)
                
                date_str = entry.get('updated', '')
                if not date_str:
                    continue
                
                try:
                    # Parse ISO-8601 (e.g. 2023-10-18T12:00:00-07:00) truncating timezone
                    review_dt = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    continue
                
                all_reviews.append({
                    'userName': author,
                    'content': review_text,
                    'score': rating,
                    'at': review_dt
                })
        except Exception as e:
            break

    if not all_reviews:
        return pd.DataFrame()

    df = pd.DataFrame(all_reviews)
    mask = (df['at'] >= from_dt) & (df['at'] <= to_dt)
    filtered_df = df.loc[mask]

    return filtered_df

