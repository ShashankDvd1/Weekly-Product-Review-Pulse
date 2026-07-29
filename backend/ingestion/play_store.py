from google_play_scraper import Sort, reviews
import pandas as pd
from datetime import datetime

def fetch_play_store_reviews(package_name: str, from_date: str, to_date: str, lang: str = 'en', country: str = 'in', max_reviews: int = 500) -> pd.DataFrame:
    """
    Fetches reviews from the Google Play Store for a given package name.
    Dates should be in 'YYYY-MM-DD' format.
    """
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    # Google Play Scraper does not paginate reliably via token for Sort.NEWEST,
    # so we scale the count dynamically in a loop until we reach reviews older than from_dt.
    current_count = max_reviews
    all_results = []
    
    while True:
        results, _ = reviews(
            package_name,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=current_count
        )
        if not results:
            break
            
        all_results = results
        # If the last review we got is older than from_dt, or we reached the end of the catalog,
        # or we hit a reasonable safety limit (e.g. 2500 reviews), we stop.
        if results[-1]['at'] < from_dt or len(results) < current_count or current_count >= 2500:
            break
            
        current_count += 500


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
