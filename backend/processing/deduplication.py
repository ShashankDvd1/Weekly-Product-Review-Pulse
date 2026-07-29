"""
Pulse Intelligence — Semantic Deduplication

Uses embeddings and ChromaDB to find and remove semantically similar
signals, falling back to scikit-learn TF-IDF similarity when offline/on low resources.
"""

import logging
import numpy as np
from core.schemas import UnifiedSignal
from core.vector_store import (
    get_embedding_model,
    store_signals,
    clear_collection,
    HAS_SENTENCE_TRANSFORMERS,
)
from core.config import DEDUP_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


def tfidf_deduplicate(
    signals: list[UnifiedSignal],
    similarity_threshold: float,
) -> list[UnifiedSignal]:
    """
    Deduplicate signals using TF-IDF + Cosine Similarity.
    Highly optimized CPU approach with zero deep learning overhead.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    if not signals:
        return []

    logger.info(f"Running TF-IDF deduplication on {len(signals)} signals...")
    contents = [s.content for s in signals]

    try:
        # Simple character/word level vectorizer to detect lexical similarity
        vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
        tfidf_matrix = vectorizer.fit_transform(contents)
        similarities = cosine_similarity(tfidf_matrix)

        unique_signals = []
        kept_indices = []

        for i, signal in enumerate(signals):
            is_dup = False
            for u_idx in kept_indices:
                # Cosine similarity matrix indices
                if similarities[i, u_idx] >= similarity_threshold:
                    is_dup = True
                    break
            
            if not is_dup:
                unique_signals.append(signal)
                kept_indices.append(i)

        return unique_signals
    except Exception as e:
        logger.error(f"TF-IDF deduplication failed: {e}. Returning all signals.")
        return signals


def semantic_deduplicate(
    signals: list[UnifiedSignal],
    similarity_threshold: float = DEDUP_SIMILARITY_THRESHOLD,
) -> list[UnifiedSignal]:
    """
    Remove duplicate signals using vector embeddings in batch or TF-IDF fallback.
    """
    if not signals:
        return []

    logger.info(f"Starting batch deduplication of {len(signals)} signals...")

    # 1. Deduplicate exact IDs first to minimize workload
    seen_ids = set()
    unique_candidates = []
    for s in signals:
        if s.unified_id not in seen_ids:
            seen_ids.add(s.unified_id)
            unique_candidates.append(s)

    if not unique_candidates:
        return []

    unique_signals = []

    # 2. Check if deep learning models are available
    if not HAS_SENTENCE_TRANSFORMERS:
        logger.info("SentenceTransformer not installed. Falling back to TF-IDF deduplication...")
        unique_signals = tfidf_deduplicate(unique_candidates, similarity_threshold)
    else:
        # Batch generate embeddings for all unique candidates
        try:
            model = get_embedding_model()
            if model is None:
                raise ValueError("Embedding model loading failed/disabled")
            contents = [s.content for s in unique_candidates]
            logger.info(f"Generating embeddings for {len(contents)} signals...")
            embeddings = model.encode(contents, show_progress_bar=False, normalize_embeddings=True)
            
            # Perform cosine similarity checks using a precalculated similarity matrix
            kept_indices = []
            embeddings = np.array(embeddings)
            # Compute all-to-all similarity in one fast matrix multiplication
            similarities = np.dot(embeddings, embeddings.T)
            
            for i, signal in enumerate(unique_candidates):
                is_dup = False
                for u_idx in kept_indices:
                    if similarities[i, u_idx] >= similarity_threshold:
                        is_dup = True
                        break
                
                if not is_dup:
                    unique_signals.append(signal)
                    kept_indices.append(i)
        except Exception as e:
            logger.error(f"Embedding deduplication failed ({e}). Falling back to TF-IDF method...")
            unique_signals = tfidf_deduplicate(unique_candidates, similarity_threshold)

    # 3. Batch store the final unique signals for search compatibility
    try:
        clear_collection("signals")
        if unique_signals:
            texts = [s.content for s in unique_signals]
            metadatas = [{"app": s.app_name, "source": s.source.value} for s in unique_signals]
            ids = [s.unified_id for s in unique_signals]
            
            chunk_size = 100
            for offset in range(0, len(unique_signals), chunk_size):
                store_signals(
                    texts[offset:offset+chunk_size],
                    metadatas[offset:offset+chunk_size],
                    ids[offset:offset+chunk_size],
                )
            logger.info(f"Stored {len(unique_signals)} unique signals in collection")
    except Exception as e:
        logger.error(f"Failed to save unique signals: {e}")

    logger.info(f"Deduplication complete: {len(signals)} -> {len(unique_signals)} signals (threshold {similarity_threshold})")
    return unique_signals
