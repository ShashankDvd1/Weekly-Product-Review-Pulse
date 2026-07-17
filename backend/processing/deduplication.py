"""
Pulse Intelligence — Semantic Deduplication

Uses embeddings and ChromaDB to find and remove semantically similar
signals (e.g., users expressing the exact same thought in slightly different words).
"""

import logging
import numpy as np
from core.schemas import UnifiedSignal
from core.vector_store import (
    get_embedding_model,
    store_signals,
    clear_collection,
)
from core.config import DEDUP_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


def semantic_deduplicate(
    signals: list[UnifiedSignal],
    similarity_threshold: float = DEDUP_SIMILARITY_THRESHOLD,
) -> list[UnifiedSignal]:
    """
    Remove semantically duplicate signals using vector embeddings in batch.
    """
    if not signals:
        return []

    logger.info(f"Starting batch semantic deduplication of {len(signals)} signals...")

    # 1. Deduplicate exact IDs first to minimize embeddings workload
    seen_ids = set()
    unique_candidates = []
    for s in signals:
        if s.unified_id not in seen_ids:
            seen_ids.add(s.unified_id)
            unique_candidates.append(s)

    if not unique_candidates:
        return []

    # 2. Batch generate embeddings for all unique candidates
    try:
        model = get_embedding_model()
        contents = [s.content for s in unique_candidates]
        logger.info(f"Generating embeddings for {len(contents)} signals...")
        embeddings = model.encode(contents, show_progress_bar=False, normalize_embeddings=True)
    except Exception as e:
        logger.exception("Failed to generate embeddings in batch, falling back to original signals")
        return unique_candidates

    # 3. Perform cosine similarity checks in a fast NumPy matrix loop
    unique_signals = []
    unique_indices = []

    for i, signal in enumerate(unique_candidates):
        is_dup = False
        for u_idx in unique_indices:
            sim = float(np.dot(embeddings[i], embeddings[u_idx]))
            if sim >= similarity_threshold:
                is_dup = True
                break
        
        if not is_dup:
            unique_signals.append(signal)
            unique_indices.append(i)

    # 4. Batch store the final unique signals in ChromaDB for search compatibility
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
            logger.info(f"Stored {len(unique_signals)} unique signals in ChromaDB")
    except Exception as e:
        logger.error(f"Failed to save unique signals to ChromaDB: {e}")

    logger.info(f"Semantic dedup complete: {len(signals)} -> {len(unique_signals)} signals (threshold {similarity_threshold})")
    return unique_signals
