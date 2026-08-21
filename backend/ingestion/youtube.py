import requests
import re
import logging
from datetime import datetime, timezone
from youtube_comment_downloader import YoutubeCommentDownloader

logger = logging.getLogger(__name__)

def collect_youtube_data(search_query: str, max_comments: int = 200) -> list[dict]:
    """
    Searches YouTube for app reviews/feedback, extracts top video IDs,
    and downloads comments without needing an official API key.
    """
    logger.info(f"Searching YouTube for: '{search_query} app review'...")
    video_ids = []
    try:
        url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}+app+review"
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}).text
        found_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
        # Deduplicate while preserving order
        seen = set()
        for v_id in found_ids:
            if v_id not in seen:
                seen.add(v_id)
                video_ids.append(v_id)
        
        # Take top 4 videos
        video_ids = video_ids[:4]
        logger.info(f"Found top YouTube videos: {video_ids}")
    except Exception as e:
        logger.error(f"Failed to search YouTube videos: {e}")
        return []

    downloader = YoutubeCommentDownloader()
    all_comments = []
    comments_per_video = max_comments // max(len(video_ids), 1)

    for video_id in video_ids:
        logger.info(f"Downloading comments for YouTube video ID: {video_id}...")
        try:
            count = 0
            # Get comments (using sort_by=1 which is Sort By Recent to avoid 429 sort setting crashes)
            for comment in downloader.get_comments(video_id, sort_by=1):
                text = comment.get("text", "").strip()
                if not text:
                    continue
                
                # Parse timestamp if exists, otherwise default to now
                time_parsed = comment.get("time_parsed")
                date_val = datetime.fromtimestamp(time_parsed, tz=timezone.utc) if time_parsed else datetime.now(timezone.utc)
                
                all_comments.append({
                    "comment_id": comment.get("cid"),
                    "content": text,
                    "author": comment.get("author", "Anonymous"),
                    "date": date_val,
                    "video_id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}&lc={comment.get('cid')}"
                })
                
                count += 1
                if count >= comments_per_video:
                    break
        except Exception as e:
            logger.error(f"Error downloading comments for video {video_id}: {e}")

    logger.info(f"Successfully collected {len(all_comments)} YouTube comments.")
    return all_comments
