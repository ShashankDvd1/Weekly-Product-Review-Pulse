"""
Pulse Intelligence — Relative Keyword Extraction & Semantic Matcher
Extracts search terms from user input and expands them with relative semantic families
(synonyms, related workflows, and stems) so that reviews discussing related concepts are preserved.
"""

import re
from typing import List, Optional, Union, Set

# Semantic family expansions: If a keyword belongs to a family, all related terms are included
SEMANTIC_FAMILIES = {
    "fit_and_sizing": {
        "fit", "size", "sizing", "chart", "guide", "measurement", "tight", "loose", 
        "small", "large", "medium", "xl", "xxl", "length", "waist", "shoulder", 
        "fitting", "true to size", "model", "height", "trial", "alter", "cut"
    },
    "wishlist_and_cart": {
        "wishlist", "wish", "save", "saved", "bag", "cart", "favourite", "favorite", 
        "heart", "later", "item", "list", "stock", "sold out", "notify", "forgot", 
        "stale", "add to cart", "move to bag", "saved items"
    },
    "quality_and_fabric": {
        "fabric", "cloth", "material", "quality", "cotton", "silk", "polyester", 
        "color", "colour", "mismatch", "photo", "picture", "finish", "cheap", 
        "original", "fake", "counterfeit", "texture", "feel", "wash", "shrink", 
        "bleed", "stitch", "transparent", "see through"
    },
    "intent_and_decision": {
        "hesitat", "confus", "decid", "decision", "doubt", "paralys", "paralysis", 
        "choice", "delay", "defer", "buy", "purchas", "order", "worth", "abandon", 
        "checkout", "drop off", "think twice", "second thought", "cancel", "unsure"
    },
    "ux_and_navigation": {
        "filter", "sort", "search", "find", "browse", "ui", "ux", "scroll", 
        "category", "categor", "clutter", "section", "drawer", "tab", "organize", 
        "lost", "slow", "bug", "crash", "stuck", "interface", "navigation"
    },
    "pricing_and_offers": {
        "price", "cost", "discount", "coupon", "offer", "deal", "charge", 
        "expensive", "cheap", "worth", "cashback", "sale", "overpriced", "fee"
    },
    "delivery_and_returns": {
        "return", "exchange", "refund", "pickup", "replace", "policy", "courier"
    }
}

def extract_keyword_terms(keywords_input: Optional[Union[str, List[str]]]) -> List[str]:
    """
    Extracts individual words and quoted phrases from structured user input,
    and automatically enriches the term list with relative semantic synonyms.
    """
    if not keywords_input:
        return []
        
    raw = keywords_input if isinstance(keywords_input, str) else ", ".join(keywords_input)
    
    # Step 1: Extract quoted phrases (e.g. "size guide", "fit issue")
    quoted_phrases = re.findall(r'"([^"]+)"', raw)
    
    # Step 2: Clean remaining text
    remaining = re.sub(r'"[^"]*"', ' ', raw)
    remaining = re.sub(r'\d+\.\s*', ' ', remaining)
    remaining = re.sub(r'[&|/\\()\[\]{}]', ' ', remaining)
    
    raw_tokens = re.split(r'[,\n;]+', remaining)
    
    extracted_terms: Set[str] = set()
    for phrase in quoted_phrases:
        clean = phrase.strip().lower()
        if len(clean) >= 2:
            extracted_terms.add(clean)
            
    for token in raw_tokens:
        clean = token.strip().lower()
        if len(clean) >= 3 and clean not in {
            'uncertainty', 'friction', 'management', 'decay', 'non-monetary', 'roadblocks'
        }:
            if len(clean.split()) > 4:
                words = [w for w in clean.split() if len(w) >= 3]
                extracted_terms.update(words)
            else:
                extracted_terms.add(clean)

    # Step 3: Expand with relative semantic families
    expanded_terms: Set[str] = set(extracted_terms)
    for term in list(extracted_terms):
        for family_name, family_words in SEMANTIC_FAMILIES.items():
            # If the extracted term intersects or is a substring of any family word
            if any(term in fw or fw in term for fw in family_words):
                expanded_terms.update(family_words)

    return list(expanded_terms)

def matches_keywords(text: str, keywords: Optional[List[str]]) -> bool:
    """
    Returns True if the text contains ANY of the relative keyword terms or stems,
    or True if no keywords are specified.
    """
    if not keywords:
        return True
    if not text:
        return False
        
    text_lower = text.lower()
    
    # Fast check: direct substring or stem match
    for kw in keywords:
        if kw in text_lower:
            return True
            
    return False

