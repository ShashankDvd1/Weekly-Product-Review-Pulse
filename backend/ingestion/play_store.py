from google_play_scraper import Sort, reviews
import pandas as pd
from datetime import datetime

def fetch_play_store_reviews(package_name: str, from_date: str, to_date: str, lang: str = 'en', max_reviews: int = 500) -> pd.DataFrame:
    """
    Fetches reviews from the Google Play Store for a given package name.
    Dates should be in 'YYYY-MM-DD' format.
    """
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    all_results = []
    token = None
    
    while True:
        result, token = reviews(
            package_name,
            lang=lang,
            sort=Sort.NEWEST,
            count=199, # Max per page
            continuation_token=token
        )
        
        if not result:
            break
            
        all_results.extend(result)
        
        # Check if the oldest review in this batch is older than from_dt
        oldest_date = result[-1]['at']
        if oldest_date < from_dt:
            break
            
        if not token:
            break
            
        if len(all_results) >= max_reviews:
            break

    if not all_results:
        return pd.DataFrame()

    df = pd.DataFrame(all_results)
    
    # Filter by date range
    df['at'] = pd.to_datetime(df['at'])
    mask = (df['at'] >= from_dt) & (df['at'] <= to_dt)
    filtered_df = df.loc[mask]
    
    # If the app has extreme volume and we hit max_reviews before reaching the 'to_dt',
    # the filtered_df will be empty. The user requested to just return the recent data we did fetch!
    if filtered_df.empty and len(all_results) >= max_reviews and all_results[-1]['at'] > to_dt:
        return df[['userName', 'content', 'score', 'at']]

    return filtered_df[['userName', 'content', 'score', 'at']]
