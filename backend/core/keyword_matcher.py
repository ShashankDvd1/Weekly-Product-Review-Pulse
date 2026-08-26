"""
Pulse Intelligence — Keyword Extraction & Matching Utility
Extracts clean search terms from structured or comma-separated user inputs
and checks if review texts match the keyword requirements.
"""

import re
from typing import List, Optional, Union

def extract_keyword_terms(keywords_input: Optional[Union[str, List[str]]]) -> List[str]:
    """
    Extracts individual words and quoted phrases from structured user input.
    Handles numbering (1., 2.), quoted blocks ("size guide"), and category headers.
    """
    if not keywords_input:
        return []
        
    raw = keywords_input if isinstance(keywords_input, str) else ", ".join(keywords_input)
    
    # Step 1: Extract quoted phrases first (e.g. "size guide", "fit issue")
    quoted_phrases = re.findall(r'"([^"]+)"', raw)
    
    # Step 2: Remove quoted phrases, numbering, and category headers from the remaining text
    remaining = re.sub(r'"[^"]*"', ' ', raw)
    remaining = re.sub(r'\d+\.\s*', ' ', remaining)
    remaining = re.sub(r'[&|/\\()\[\]{}]', ' ', remaining)
    
    # Step 3: Split remaining text by commas, newlines, and delimiters
    raw_tokens = re.split(r'[,\n;]+', remaining)
    
    all_terms = []
    for phrase in quoted_phrases:
        clean = phrase.strip().lower()
        if len(clean) >= 2:
            all_terms.append(clean)
            
    for token in raw_tokens:
        clean = token.strip().lower()
        # Skip generic stop category headers
        if len(clean) >= 3 and clean not in {
            'fit', 'sizing', 'quality', 'uncertainty', 'friction',
            'management', 'hesitation', 'intent', 'decay', 'logistics',
            'non-monetary', 'roadblocks', 'post-wishlist', 'ui', 'ux'
        }:
            if len(clean.split()) > 4:
                words = [w for w in clean.split() if len(w) >= 4]
                all_terms.extend(words)
            else:
                all_terms.append(clean)
                
    # Deduplicate while preserving order
    seen = set()
    result = []
    for t in all_terms:
        if t not in seen:
            seen.add(t)
            result.append(t)
            
    return result

def matches_keywords(text: str, keywords: Optional[List[str]]) -> bool:
    """
    Returns True if the text contains ANY of the extracted keywords,
    or True if no keywords are specified.
    """
    if not keywords:
        return True
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)
