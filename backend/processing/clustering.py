from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
import pandas as pd
import numpy as np

def cluster_reviews(df: pd.DataFrame, min_cluster_size: int = 5) -> tuple:
    """
    Clusters reviews using TF-IDF vectorization + MiniBatchKMeans.
    Identifies centroid reviews for each cluster to minimize LLM token usage.
    
    Uses a lightweight sklearn pipeline (TF-IDF + KMeans) for fast, reliable
    clustering that works well inside synchronous web server contexts.
    """
    if df.empty or 'content' not in df.columns:
        df['cluster'] = 0
        df['is_centroid'] = True
        return df, True

    texts = df['content'].astype(str).tolist()
    n_reviews = len(texts)
    
    # If there are very few reviews, skip clustering and just use all of them
    if n_reviews <= 15:
        df['cluster'] = 0
        df['is_centroid'] = True
        return df, False

    # Step 1: TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        min_df=2,
        max_df=0.95,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Step 2: MiniBatchKMeans clustering (~10-15 clusters depending on volume)
    n_clusters = min(max(5, n_reviews // 50), 15)
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        random_state=42,
        batch_size=512,
        n_init=1
    )
    cluster_labels = kmeans.fit_predict(tfidf_matrix)

    df['cluster'] = cluster_labels
    df['is_centroid'] = False

    # Step 3: Find centroids (review closest to each cluster center)
    for cluster_id in range(n_clusters):
        cluster_mask = cluster_labels == cluster_id
        cluster_indices = np.where(cluster_mask)[0]
        
        if len(cluster_indices) == 0:
            continue
        
        # Get cluster center from KMeans
        center = kmeans.cluster_centers_[cluster_id]
        
        # Find the review closest to the center via dot-product similarity
        cluster_vectors = tfidf_matrix[cluster_indices]
        similarities = cluster_vectors.dot(center)
        closest_idx = cluster_indices[np.argmax(similarities)]
        
        df.iloc[closest_idx, df.columns.get_loc('is_centroid')] = True

    fallback_used = False
    # Fallback: if somehow no centroids were found, randomly sample
    if df['is_centroid'].sum() == 0 and len(df) > 0:
        fallback_count = min(5, len(df))
        fallback_indices = np.random.choice(len(df), fallback_count, replace=False)
        df.iloc[fallback_indices, df.columns.get_loc('is_centroid')] = True
        fallback_used = True

    return df, fallback_used
