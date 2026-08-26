from google_play_scraper import Sort, reviews
import pandas as pd
from datetime import datetime
from typing import Optional, Union, List
from core.keyword_matcher import extract_keyword_terms, matches_keywords

def fetch_play_store_reviews(
    package_name: str, 
    from_date: str, 
    to_date: str, 
    lang: str = 'en', 
    country: str = 'in', 
    max_reviews: int = 500,
    keywords: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Fetches reviews from the Google Play Store for a given package name.
    If keywords are provided, filters reviews during scraping and continues
    fetching until enough keyword-matching reviews are collected.
    """
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    kw_terms = extract_keyword_terms(keywords)
    target_matching_count = 150 if kw_terms else max_reviews

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
        
        # Check how many matching reviews we have in the current date range
        matching_count = 0
        for r in results:
            if r['at'] >= from_dt and r['at'] <= to_dt:
                if not kw_terms or matches_keywords(r.get('content', ''), kw_terms):
                    matching_count += 1
                    
        # Stop if we found enough matching reviews, or if we passed from_dt,
        # or if we hit the maximum catalog / safety limit
        if matching_count >= target_matching_count or results[-1]['at'] < from_dt or len(results) < current_count or current_count >= 3000:
            break
            
        current_count += 500

    if not all_results:
        return pd.DataFrame()

    df = pd.DataFrame(all_results)
    
    # Filter by date range
    df['at'] = pd.to_datetime(df['at'])
    mask = (df['at'] >= from_dt) & (df['at'] <= to_dt)
    filtered_df = df.loc[mask]
    
    # Fallback to recent data if filtered_df is empty due to date boundary
    if filtered_df.empty and len(all_results) >= max_reviews and all_results[-1]['at'] > to_dt:
        filtered_df = df

    # Filter by keywords directly in scraper
    if kw_terms and not filtered_df.empty:
        kw_mask = filtered_df['content'].apply(lambda x: matches_keywords(str(x), kw_terms))
        filtered_df = filtered_df.loc[kw_mask]

    return filtered_df[['userName', 'content', 'score', 'at']]
