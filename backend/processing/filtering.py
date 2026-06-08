import pandas as pd
import emoji

def filter_reviews(df: pd.DataFrame, min_word_count: int, include_emojis: bool) -> pd.DataFrame:
    """
    Filters a DataFrame of reviews based on word count and emoji presence.
    """
    if df.empty or 'content' not in df.columns:
        return df

    # Drop empty contents
    df = df.dropna(subset=['content'])
    df['content'] = df['content'].astype(str)

    # Filter by min word count
    if min_word_count > 0:
        word_counts = df['content'].apply(lambda x: len(str(x).split()))
        df = df[word_counts >= min_word_count]

    # Filter by emojis
    if not include_emojis:
        def has_emoji(text):
            return emoji.emoji_count(text) > 0
        
        # Keep only reviews that do NOT have emojis
        df = df[~df['content'].apply(has_emoji)]
        
    return df
