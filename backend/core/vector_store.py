"""
Pulse Intelligence — Vector Store (ChromaDB & Lightweight Fallback)

Manages ChromaDB collections for semantic search, similarity matching,
and embedding-based deduplication. Falls back to a lightweight in-memory
keyword-matching store if ChromaDB is not installed.
"""

import os
import hashlib
import logging
from typing import Optional, Any

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except ImportError:
    chromadb = None
    ChromaSettings = None
    HAS_CHROMADB = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = None
    HAS_SENTENCE_TRANSFORMERS = False

from core.config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_SIGNALS,
    CHROMA_COLLECTION_INSIGHTS,
    EMBEDDING_MODEL,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# In-Memory Mock Store Fallback
# ─────────────────────────────────────────────
_mock_collection: dict[str, dict] = {}

# ─────────────────────────────────────────────
# Embedding Model (loaded once if available)
# ─────────────────────────────────────────────
_embedding_model: Optional[Any] = None


def get_embedding_model() -> Optional[Any]:
    """Load the sentence-transformers model (lazy singleton)."""
    global _embedding_model
    if not HAS_SENTENCE_TRANSFORMERS:
        return None
        
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
    if model is None:
        # Return mock 384-dimensional zero vectors if embedding is disabled
        return [[0.0] * 384 for _ in texts]
        
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
_chroma_client: Optional[Any] = None


def get_chroma_client() -> Optional[Any]:
    """Get or create a persistent ChromaDB client."""
    global _chroma_client
    if not HAS_CHROMADB:
        return None
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
    if client is None:
        return None
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_SIGNALS,
        metadata={"description": "All consumer signals (reviews + reddit)"},
    )


def get_insights_collection():
    """Get (or create) the AI-generated insights collection."""
    client = get_chroma_client()
    if client is None:
        return None
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
    Store consumer signals in ChromaDB (or mock fallback) with their embeddings.
    """
    if not texts:
        return

    if not HAS_CHROMADB:
        logger.info(f"Storing {len(texts)} signals in mock in-memory store...")
        for i, text in enumerate(texts):
            sig_id = ids[i] if ids else hashlib.md5(text.encode()).hexdigest()
            meta = metadatas[i] if i < len(metadatas) else {}
            _mock_collection[sig_id] = {"text": text, "metadata": meta}
        return

    collection = get_signals_collection()
    if collection is None:
        return
        
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
    Perform semantic search across stored signals. Falls back to keyword matching.
    """
    if not HAS_CHROMADB:
        logger.info(f"ChromaDB not available. Performing fallback keyword search for '{query}'...")
        results = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        query_words = set(query.lower().split())
        if not query_words:
            return results
            
        matched = []
        for sig_id, data in _mock_collection.items():
            text = data["text"]
            overlap = sum(1 for w in query_words if w in text.lower())
            if overlap > 0:
                matched.append((sig_id, data, overlap))
                
        matched.sort(key=lambda x: x[2], reverse=True)
        matched = matched[:top_k]
        
        results["ids"] = [[m[0] for m in matched]]
        results["documents"] = [[m[1]["text"] for m in matched]]
        results["metadatas"] = [[m[1]["metadata"] for m in matched]]
        results["distances"] = [[float(1.0 - (m[2] / len(query_words))) for m in matched]]
        return results

    collection = get_signals_collection() if collection_name == "signals" else get_insights_collection()
    if collection is None:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        
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
    """
    results = semantic_search(text, top_k=top_k)

    similar = []
    if results and results.get("ids") and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results.get("distances") and i < len(results["distances"][0]) else 0
            # ChromaDB uses L2 distance; TF-IDF fallback uses normalized word overlap distance
            similarity = 1 - (distance / 2) if HAS_CHROMADB else (1 - distance)
            if similarity >= threshold:
                similar.append({
                    "id": doc_id,
                    "text": results["documents"][0][i] if results.get("documents") and i < len(results["documents"][0]) else "",
                    "distance": distance,
                    "similarity": similarity,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") and i < len(results["metadatas"][0]) else {},
                })
    return similar


def get_collection_stats() -> dict:
    """Get statistics about stored data."""
    if not HAS_CHROMADB:
        return {
            "signals_count": len(_mock_collection),
            "insights_count": 0,
        }
    try:
        signals = get_signals_collection()
        insights = get_insights_collection()
        return {
            "signals_count": signals.count() if signals else 0,
            "insights_count": insights.count() if insights else 0,
        }
    except Exception:
        return {
            "signals_count": len(_mock_collection),
            "insights_count": 0,
        }


def clear_collection(collection_name: str = "signals"):
    """Clear all data from a collection (for testing/reset)."""
    if not HAS_CHROMADB:
        if collection_name == "signals":
            _mock_collection.clear()
            logger.info("Cleared mock signals collection")
        return
        
    client = get_chroma_client()
    if client is None:
        return
    if collection_name == "signals":
        client.delete_collection(CHROMA_COLLECTION_SIGNALS)
        logger.info("Cleared signals collection")
    elif collection_name == "insights":
        client.delete_collection(CHROMA_COLLECTION_INSIGHTS)
        logger.info("Cleared insights collection")
