"""
Pulse Intelligence — Vector Store (ChromaDB)

Manages ChromaDB collections for semantic search, similarity matching,
and embedding-based deduplication.
"""

import os
import hashlib
import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from core.config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_SIGNALS,
    CHROMA_COLLECTION_INSIGHTS,
    EMBEDDING_MODEL,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Embedding Model (loaded once)
# ─────────────────────────────────────────────
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Load the sentence-transformers model (lazy singleton)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}...")
        
        # Configure torch to use 1 thread and disable gradients BEFORE loading model to save memory
        try:
            import torch
            torch.set_num_threads(1)
            torch.set_grad_enabled(False)
            logger.info("Configured PyTorch for single-threaded CPU execution (saves memory).")
        except Exception as e:
            logger.warning(f"Failed to configure PyTorch threads: {e}")

        try:
            # Try offline loading first to avoid hanging on update checks in sandboxed environments
            _embedding_model = SentenceTransformer(EMBEDDING_MODEL, local_files_only=True)
            logger.info("Embedding model loaded successfully from local cache.")
        except Exception as e:
            logger.info(f"Local model load failed ({e}), attempting online load...")
            _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            logger.info("Embedding model loaded from HuggingFace Hub.")
    return _embedding_model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    model = get_embedding_model()
    import gc
    try:
        import torch
        with torch.no_grad():
            embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    except Exception:
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        
    gc.collect()
    return embeddings.tolist()


def generate_embedding(text: str) -> list[float]:
    """Generate embedding for a single text."""
    return generate_embeddings([text])[0]


# ─────────────────────────────────────────────
# ChromaDB Client
# ─────────────────────────────────────────────
_chroma_client: Optional[chromadb.ClientAPI] = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create a persistent ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        logger.info(f"ChromaDB initialized at: {CHROMA_PERSIST_DIR}")
    return _chroma_client


# ─────────────────────────────────────────────
# Collection Management
# ─────────────────────────────────────────────
def get_signals_collection():
    """Get (or create) the consumer signals collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_SIGNALS,
        metadata={"description": "All consumer signals (reviews + reddit)"},
    )


def get_insights_collection():
    """Get (or create) the AI-generated insights collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_INSIGHTS,
        metadata={"description": "AI-generated themes, personas, barriers"},
    )


# ─────────────────────────────────────────────
# Core Operations
# ─────────────────────────────────────────────
def store_signals(
    texts: list[str],
    metadatas: list[dict],
    ids: Optional[list[str]] = None,
):
    """
    Store consumer signals in ChromaDB with their embeddings.

    Args:
        texts: The text content of each signal
        metadatas: Metadata dicts for each signal
        ids: Optional custom IDs; auto-generated from text hash if not provided
    """
    if not texts:
        return

    collection = get_signals_collection()
    embeddings = generate_embeddings(texts)

    if ids is None:
        ids = [hashlib.md5(t.encode()).hexdigest() for t in texts]

    # ChromaDB upsert handles duplicates gracefully
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    logger.info(f"Stored {len(texts)} signals in ChromaDB")


def semantic_search(
    query: str,
    top_k: int = 10,
    where: Optional[dict] = None,
    collection_name: str = "signals",
) -> dict:
    """
    Perform semantic search across stored signals.

    Args:
        query: Search query text
        top_k: Number of results to return
        where: Optional metadata filter (e.g., {"source": "reddit"})
        collection_name: Which collection to search

    Returns:
        ChromaDB query results dict with ids, documents, distances, metadatas
    """
    collection = get_signals_collection() if collection_name == "signals" else get_insights_collection()
    query_embedding = generate_embedding(query)

    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, collection.count() or 1),
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)
    return results


def find_similar(
    text: str,
    top_k: int = 5,
    threshold: float = 0.0,
) -> list[dict]:
    """
    Find signals similar to the given text.

    Returns:
        List of dicts with keys: id, text, distance, metadata
    """
    results = semantic_search(text, top_k=top_k)

    similar = []
    if results and results.get("ids") and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results.get("distances") else 0
            # ChromaDB uses L2 distance by default; lower = more similar
            similarity = 1 - (distance / 2)  # Approximate cosine similarity
            if similarity >= threshold:
                similar.append({
                    "id": doc_id,
                    "text": results["documents"][0][i] if results.get("documents") else "",
                    "distance": distance,
                    "similarity": similarity,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                })
    return similar


def get_collection_stats() -> dict:
    """Get statistics about stored data."""
    signals = get_signals_collection()
    insights = get_insights_collection()
    return {
        "signals_count": signals.count(),
        "insights_count": insights.count(),
    }


def clear_collection(collection_name: str = "signals"):
    """Clear all data from a collection (for testing/reset)."""
    client = get_chroma_client()
    if collection_name == "signals":
        client.delete_collection(CHROMA_COLLECTION_SIGNALS)
        logger.info("Cleared signals collection")
    elif collection_name == "insights":
        client.delete_collection(CHROMA_COLLECTION_INSIGHTS)
        logger.info("Cleared insights collection")
