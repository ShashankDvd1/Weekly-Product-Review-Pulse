"""
Pulse Intelligence — Reddit Data Collector

Collects posts and comments from Reddit using the public JSON API.
No API key required — just append .json to any Reddit URL.

Targets subreddits where quick commerce is discussed and searches
for relevant keywords (zepto, blinkit, swiggy instamart, etc.).
"""

import time
import logging
import requests
from datetime import datetime, timezone
from typing import Optional

from core.config import (
    REDDIT_BASE_URL,
    REDDIT_USER_AGENT,
    REDDIT_DEFAULT_SUBREDDITS,
    REDDIT_SEARCH_TERMS_QUICK_COMMERCE,
    REDDIT_MIN_SCORE,
    REDDIT_MIN_WORD_COUNT,
    REDDIT_MAX_POSTS_PER_QUERY,
    REDDIT_MAX_COMMENTS_PER_POST,
    REDDIT_REQUEST_DELAY,
)

logger = logging.getLogger(__name__)

# Shared session for connection reuse
_session = requests.Session()
_session.headers.update({"User-Agent": REDDIT_USER_AGENT})


def _reddit_get(url: str, params: Optional[dict] = None) -> Optional[dict]:
    """Make a GET request to Reddit's JSON API with rate limiting."""
    time.sleep(REDDIT_REQUEST_DELAY)
    try:
        response = _session.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            logger.warning("Reddit rate limited — waiting 30s...")
            time.sleep(30)
            return None
        else:
            logger.warning(f"Reddit API returned {response.status_code} for {url}")
            return None
    except requests.RequestException as e:
        logger.error(f"Reddit request failed: {e}")
        return None


def search_subreddit(
    subreddit: str,
    query: str,
    sort: str = "relevance",
    time_filter: str = "year",
    limit: int = REDDIT_MAX_POSTS_PER_QUERY,
) -> list[dict]:
    """
    Search a subreddit for posts matching a query.

    Args:
        subreddit: Subreddit name (without r/)
        query: Search query string
        sort: Sort order (relevance, hot, top, new, comments)
        time_filter: Time range (hour, day, week, month, year, all)
        limit: Max posts to return

    Returns:
        List of post dicts with standardized fields
    """
    url = f"{REDDIT_BASE_URL}/r/{subreddit}/search.json"
    params = {
        "q": query,
        "sort": sort,
        "t": time_filter,
        "restrict_sr": "on",
        "limit": min(limit, 100),  # Reddit caps at 100 per page
    }

    data = _reddit_get(url, params)
    if not data or "data" not in data:
        return []

    posts = []
    for child in data["data"].get("children", []):
        post_data = child.get("data", {})
        if not post_data:
            continue

        # Extract and normalize
        created_utc = post_data.get("created_utc", 0)
        post_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)

        selftext = post_data.get("selftext", "") or ""
        title = post_data.get("title", "") or ""

        # Skip removed/deleted posts
        if selftext in ("[removed]", "[deleted]"):
            selftext = ""

        posts.append({
            "post_id": post_data.get("id", ""),
            "subreddit": subreddit,
            "post_type": "post",
            "author": post_data.get("author", "Anonymous"),
            "title": title,
            "content": f"{title}\n\n{selftext}".strip() if selftext else title,
            "score": post_data.get("score", 0),
            "date": post_date,
            "url": f"https://reddit.com{post_data.get('permalink', '')}",
            "num_comments": post_data.get("num_comments", 0),
            "parent_post_id": None,
        })

    return posts


def fetch_post_comments(
    post_url: str,
    max_comments: int = REDDIT_MAX_COMMENTS_PER_POST,
) -> list[dict]:
    """
    Fetch comments from a specific Reddit post.

    Args:
        post_url: Full Reddit permalink URL
        max_comments: Maximum comments to collect

    Returns:
        List of comment dicts with standardized fields
    """
    # Normalize URL to end with .json
    json_url = post_url.rstrip("/") + ".json"
    if not json_url.startswith("http"):
        json_url = f"{REDDIT_BASE_URL}{json_url}"
    if not json_url.endswith(".json"):
        json_url += ".json"

    params = {"limit": max_comments, "sort": "top"}
    data = _reddit_get(json_url, params)
    if not data or not isinstance(data, list) or len(data) < 2:
        return []

    comments = []
    post_id = ""

    # First element is the post itself
    if data[0].get("data", {}).get("children"):
        post_data = data[0]["data"]["children"][0].get("data", {})
        post_id = post_data.get("id", "")

    # Second element contains comments
    _extract_comments(data[1], comments, post_id, max_comments)

    return comments[:max_comments]


def _extract_comments(
    listing: dict,
    comments: list[dict],
    parent_post_id: str,
    max_comments: int,
    depth: int = 0,
):
    """Recursively extract comments from a Reddit comment listing."""
    if depth > 5 or len(comments) >= max_comments:
        return

    children = listing.get("data", {}).get("children", [])
    for child in children:
        if len(comments) >= max_comments:
            break

        if child.get("kind") != "t1":  # t1 = comment
            continue

        comment_data = child.get("data", {})
        body = comment_data.get("body", "") or ""

        # Skip removed/deleted/bot comments
        if body in ("[removed]", "[deleted]", ""):
            continue
        author = comment_data.get("author", "")
        if author in ("AutoModerator", "[deleted]"):
            continue

        created_utc = comment_data.get("created_utc", 0)
        comment_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)

        comments.append({
            "post_id": comment_data.get("id", ""),
            "subreddit": comment_data.get("subreddit", ""),
            "post_type": "comment",
            "author": author,
            "title": None,
            "content": body,
            "score": comment_data.get("score", 0),
            "date": comment_date,
            "url": f"https://reddit.com{comment_data.get('permalink', '')}",
            "num_comments": 0,
            "parent_post_id": parent_post_id,
        })

        # Recurse into replies
        replies = comment_data.get("replies")
        if replies and isinstance(replies, dict):
            _extract_comments(replies, comments, parent_post_id, max_comments, depth + 1)


from typing import Optional, Union, List
from core.keyword_matcher import extract_keyword_terms, matches_keywords

def collect_reddit_data(
    subreddits: Optional[list[str]] = None,
    search_terms: Optional[list[str]] = None,
    time_filter: str = "year",
    include_comments: bool = True,
    min_score: int = REDDIT_MIN_SCORE,
    min_word_count: int = REDDIT_MIN_WORD_COUNT,
    keywords: Optional[Union[str, List[str]]] = None,
) -> list[dict]:
    """
    Collect Reddit posts and comments matching search terms or user keywords.
    """
    kw_terms = extract_keyword_terms(keywords)
    
    if subreddits is None:
        subreddits = REDDIT_DEFAULT_SUBREDDITS
        
    if search_terms is None:
        if kw_terms:
            search_terms = kw_terms[:5]  # Use top keywords directly as Reddit search terms
        else:
            search_terms = REDDIT_SEARCH_TERMS_QUICK_COMMERCE

    all_signals = []
    seen_ids = set()

    for subreddit in subreddits:
        for term in search_terms:
            logger.info(f"Searching r/{subreddit} for '{term}'...")
            posts = search_subreddit(subreddit, term, time_filter=time_filter)

            for post in posts:
                pid = post["post_id"]
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)

                # Apply keyword filter
                if kw_terms and not matches_keywords(post["content"], kw_terms):
                    continue

                # Apply filters
                word_count = len(post["content"].split())
                if post["score"] >= min_score and word_count >= min_word_count:
                    post["word_count"] = word_count
                    all_signals.append(post)

                # Fetch comments for high-engagement posts
                if include_comments and post["num_comments"] > 3:
                    comments = fetch_post_comments(post["url"])
                    for comment in comments:
                        cid = comment["post_id"]
                        if cid in seen_ids:
                            continue
                        seen_ids.add(cid)

                        if kw_terms and not matches_keywords(comment["content"], kw_terms):
                            continue

                        c_word_count = len(comment["content"].split())
                        if comment["score"] >= min_score and c_word_count >= min_word_count:
                            comment["word_count"] = c_word_count
                            all_signals.append(comment)

    logger.info(f"Reddit collection complete: {len(all_signals)} signals from {len(seen_ids)} unique items")
    return all_signals
