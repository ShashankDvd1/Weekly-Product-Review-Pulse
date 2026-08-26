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
    Uses continuation token pagination to rapidly scan through thousands of reviews
    and collect reviews that match the target date range and user keywords.
    """
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    kw_terms = extract_keyword_terms(keywords)
    target_count = 150 if kw_terms else max_reviews
    
    all_matching_reviews = []
    token = None
    max_pages = 30  # Scans up to 6,000 reviews
    
    for _ in range(max_pages):
        try:
            results, token = reviews(
                package_name,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=200,
                continuation_token=token
            )
        except Exception:
            break
            
        if not results:
            break
            
        for r in results:
            review_at = r.get('at')
            if not review_at:
                continue
                
            # Check date range
            if from_dt <= review_at <= to_dt:
                if not kw_terms or matches_keywords(r.get('content', ''), kw_terms):
                    all_matching_reviews.append({
                        'userName': r.get('userName', 'Anonymous'),
                        'content': r.get('content', ''),
                        'score': r.get('score', 3),
                        'at': review_at
                    })
                    if len(all_matching_reviews) >= target_count:
                        break
                        
        if len(all_matching_reviews) >= target_count or not token:
            break
            
        # If the oldest review in this batch is already older than from_dt, stop
        if results and results[-1].get('at') and results[-1]['at'] < from_dt and len(all_matching_reviews) >= 30:
            break

    if not all_matching_reviews:
        return pd.DataFrame()

    return pd.DataFrame(all_matching_reviews)[['userName', 'content', 'score', 'at']]
