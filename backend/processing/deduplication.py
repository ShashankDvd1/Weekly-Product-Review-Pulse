"""
Pulse Intelligence — Semantic Deduplication

Uses embeddings and ChromaDB to find and remove semantically similar
signals (e.g., users expressing the exact same thought in slightly different words).
"""

import logging
from typing import Optional

from core.schemas import UnifiedSignal
from core.vector_store import (
    store_signals,
    find_similar,
    clear_collection,
)
from core.config import DEDUP_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


def semantic_deduplicate(
    signals: list[UnifiedSignal],
    similarity_threshold: float = DEDUP_SIMILARITY_THRESHOLD,
) -> list[UnifiedSignal]:
    """
    Remove semantically duplicate signals using vector embeddings.

    This is more aggressive than the exact deduplication in the normalizer.
    If two users say "The milk was expired", we keep both if they are distinct
    events, but if a single user spams the same review across platforms,
    this catches it.
    """
    if not signals:
        return []

    # Ensure a clean slate for this run
    clear_collection("signals")

    unique_signals = []
    texts_to_store = []
    metadatas_to_store = []
    ids_to_store = []
    seen_ids = set()

    for signal in signals:
        # Prevent exact duplicates from entering the batch storage arrays
        if signal.unified_id in seen_ids:
            continue
        seen_ids.add(signal.unified_id)

        # Check if we already have something very similar
        similar = find_similar(signal.content, top_k=1, threshold=similarity_threshold)

        if similar:
            logger.debug(f"Dropped duplicate signal: {signal.unified_id}")
            continue

        unique_signals.append(signal)

        # We must store it so subsequent checks can find it
        # But doing this 1 by 1 is slow, so we batch it every 50
        texts_to_store.append(signal.content)
        metadatas_to_store.append({"app": signal.app_name, "source": signal.source.value})
        ids_to_store.append(signal.unified_id)

        if len(texts_to_store) >= 50:
            store_signals(texts_to_store, metadatas_to_store, ids_to_store)
            texts_to_store.clear()
            metadatas_to_store.clear()
            ids_to_store.clear()

    # Store any remaining
    if texts_to_store:
        store_signals(texts_to_store, metadatas_to_store, ids_to_store)

    logger.info(f"Semantic dedup: {len(signals)} -> {len(unique_signals)} signals (threshold {similarity_threshold})")
    return unique_signals
