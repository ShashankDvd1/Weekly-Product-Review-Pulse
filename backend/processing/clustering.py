from fastembed import TextEmbedding
import umap
import hdbscan
import pandas as pd
import numpy as np

# Load the BGE model using fastembed (no PyTorch required)
try:
    model = TextEmbedding("BAAI/bge-small-en-v1.5")
except Exception as e:
    print("Warning: Could not load TextEmbedding locally.")
    model = None

def cluster_reviews(df: pd.DataFrame, min_cluster_size: int = 5) -> pd.DataFrame:
    """
    Generates embeddings, reduces dimensionality with UMAP, and clusters with HDBSCAN.
    Identifies centroid reviews for each cluster to minimize LLM token usage.
    """
    if df.empty or 'content' not in df.columns or model is None:
        return df

    texts = df['content'].tolist()
    
    # Generate embeddings (returns a generator, convert to list of numpy arrays)
    embeddings = list(model.embed(texts))
    
    # UMAP dimensionality reduction
    n_neighbors = min(15, len(texts) - 1) if len(texts) > 2 else 2
    if n_neighbors < 2:
        df['cluster'] = 0
        df['is_centroid'] = True
        return df
        
    reducer = umap.UMAP(n_neighbors=n_neighbors, n_components=5, metric='cosine', random_state=42)
    reduced_embeddings = reducer.fit_transform(embeddings)
    
    # HDBSCAN clustering
    # min_cluster_size handles how big a cluster needs to be
    cluster_size = min(min_cluster_size, len(texts))
    clusterer = hdbscan.HDBSCAN(min_cluster_size=cluster_size, metric='euclidean', cluster_selection_method='eom')
    cluster_labels = clusterer.fit_predict(reduced_embeddings)
    
    df['cluster'] = cluster_labels
    df['is_centroid'] = False
    
    # Find centroids
    unique_clusters = set(cluster_labels)
    for cluster_id in unique_clusters:
        if cluster_id == -1:
            continue # Skip noise points
            
        cluster_indices = np.where(cluster_labels == cluster_id)[0]
        cluster_center = np.mean(reduced_embeddings[cluster_indices], axis=0)
        
        # Point closest to the center
        distances = np.linalg.norm(reduced_embeddings[cluster_indices] - cluster_center, axis=1)
        closest_index = cluster_indices[np.argmin(distances)]
        
        # Mark as centroid using integer location
        df.iloc[closest_index, df.columns.get_loc('is_centroid')] = True

    fallback_used = False
    # Fallback: if no clusters were found (all noise), randomly sample a few reviews
    if df['is_centroid'].sum() == 0 and len(df) > 0:
        fallback_count = min(3, len(df))
        fallback_indices = np.random.choice(len(df), fallback_count, replace=False)
        df.iloc[fallback_indices, df.columns.get_loc('is_centroid')] = True
        fallback_used = True

    return df, fallback_used
