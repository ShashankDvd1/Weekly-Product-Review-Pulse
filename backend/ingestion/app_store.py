import requests
import pandas as pd
from datetime import datetime

def fetch_app_store_reviews(app_id: str, from_date: str, to_date: str, country: str = 'in', max_pages: int = 10) -> pd.DataFrame:
    """
    Fetches reviews from the Apple App Store using the iTunes RSS feed.
    max_pages: iTunes RSS only allows up to 10 pages (500 reviews total).
    """
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    all_reviews = []

    for page in range(1, max_pages + 1):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/sortBy=mostRecent/id={app_id}/json"
        response = requests.get(url)
        if response.status_code != 200:
            break
            
        data = response.json()
        if 'feed' not in data or 'entry' not in data['feed']:
            break
            
        entries = data['feed']['entry']
        if not isinstance(entries, list):
            entries = [entries]
            
        for entry in entries:
            # Skip the first entry if it's the app metadata itself
            if 'im:name' in entry and 'author' not in entry:
                continue
                
            review_text = entry.get('content', {}).get('label', '')
            author = entry.get('author', {}).get('name', {}).get('label', 'Unknown')
            rating = int(entry.get('im:rating', {}).get('label', '0'))
            
            date_str = entry.get('updated', {}).get('label', '')
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

    if not all_reviews:
        return pd.DataFrame()

    df = pd.DataFrame(all_reviews)
    mask = (df['at'] >= from_dt) & (df['at'] <= to_dt)
    filtered_df = df.loc[mask]

    return filtered_df
