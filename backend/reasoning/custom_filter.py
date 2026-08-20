"""
Pulse Intelligence — Custom NLP Prompt Filter

Intercepts the ingestion pipeline to apply a highly targeted user-provided NLP extraction prompt.
Filters out noise and extracts specific human motivations behind behaviors (like wishlist drop-off).
"""

import logging
import json
import numpy as np
from typing import List

from core.llm_client import get_llm_client
from core.schemas import UnifiedSignal, QualityCategory
from core.config import LLM_MODEL_FAST

logger = logging.getLogger(__name__)

def semantic_prefilter(signals: List[UnifiedSignal], problem_statement: str, max_results: int = 300) -> List[UnifiedSignal]:
    """
    Blazing fast pre-filter using local vector embeddings. 
    Drops completely irrelevant reviews before they hit the LLM.
    """
    if not signals or not problem_statement:
        return signals
        
    logger.info(f"Running Fast Semantic Pre-filter on {len(signals)} raw signals against the Problem Statement...")
    
    from core.vector_store import generate_embedding, generate_embeddings
    
    try:
        prob_emb = np.array(generate_embedding(problem_statement))
    except Exception as e:
        logger.error(f"Failed to generate embedding for problem statement: {e}")
        return signals # fallback to all
        
    texts = [sig.content for sig in signals]
    try:
        sig_embs = np.array(generate_embeddings(texts))
    except Exception as e:
        logger.error(f"Failed to generate embeddings for signals: {e}")
        return signals
        
    # Since generate_embeddings uses normalize_embeddings=True, dot product is cosine similarity
    similarities = np.dot(sig_embs, prob_emb)
    
    scored_signals = list(zip(signals, similarities))
    scored_signals.sort(key=lambda x: x[1], reverse=True)
    
    # Keep top results with decent similarity
    filtered = [s for s, sim in scored_signals if sim > 0.05][:max_results]
    
    logger.info(f"Semantic Pre-filter reduced {len(signals)} -> {len(filtered)} signals.")
    return filtered

def assess_reviews_with_custom_prompt(signals: List[UnifiedSignal], custom_prompt: str) -> List[UnifiedSignal]:
    """
    Passes reviews through the custom NLP extraction prompt provided by the user.
    """
    if not signals or not custom_prompt:
        return signals

    logger.info(f"Applying Custom NLP Filter to {len(signals)} signals...")
    llm = get_llm_client()
    
    # Process in batches to avoid token limits (e.g. 50 reviews per batch)
    BATCH_SIZE = 30
    accepted_signals = []
    
    for i in range(0, len(signals), BATCH_SIZE):
        batch = signals[i:i + BATCH_SIZE]
        
        # Prepare the reviews block
        reviews_block = ""
        for idx, sig in enumerate(batch):
            reviews_block += f"[{idx}] {sig.content}\n"
            
        system_prompt = custom_prompt
        
        user_message = f"Here are the reviews to process:\n\n{reviews_block}\n\n"
        user_message += "Return a valid JSON array of objects following the exact requested output format. For example: [{\"review_id\": \"0\", ...}, {\"review_id\": \"1\", ...}]. The review_id should be the index [X] provided above."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = llm._call(
                messages=messages,
                model=LLM_MODEL_FAST,
                temperature=0.1,
                is_json=True
            )
            
            try:
                data = json.loads(response)
                if isinstance(data, dict):
                    key = list(data.keys())[0]
                    results = data[key]
                    if not isinstance(results, list):
                        results = [data] # Fallback
                else:
                    results = data
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Custom Filter LLM response.")
                results = []

            for res in results:
                try:
                    raw_id = str(res.get("review_id", ""))
                    idx_str = ''.join(filter(str.isdigit, raw_id))
                    
                    if not idx_str:
                        continue
                        
                    idx = int(idx_str)
                    
                    if 0 <= idx < len(batch):
                        sig = batch[idx]
                        
                        intent = res.get("wishlist_intent", "")
                        drop_off = res.get("drop_off_reason", "")
                        
                        is_filtered = (
                            intent == "[FILTERED_OUT]" or 
                            drop_off == "[FILTERED_OUT]" or
                            (intent in ["NONE", ""] and drop_off in ["NONE", ""])
                        )
                        
                        if is_filtered:
                            sig.quality_category = QualityCategory.DISCARD
                        else:
                            sig.quality_category = QualityCategory.GOLD_INSIGHT
                            sig.extracted_insights = {
                                "wishlist_intent": intent,
                                "drop_off_reason": drop_off,
                                "verbatim_quote": res.get("verbatim_quote", ""),
                                "actionable_insight": res.get("actionable_insight", "")
                            }
                            accepted_signals.append(sig)
                except Exception as map_err:
                    logger.warning(f"Error mapping custom filter result: {map_err}")

        except Exception as e:
            logger.error(f"Error calling LLM for custom filter batch: {e}")
            
    logger.info(f"Custom filter accepted {len(accepted_signals)} out of {len(signals)} signals.")
    return accepted_signals
