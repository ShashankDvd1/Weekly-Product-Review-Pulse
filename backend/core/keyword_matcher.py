"""
Pulse Intelligence — Dynamic Keyword Extraction & Review Matcher
Directly extracts all search terms, phrases, categories, and stems from user input dynamically.
Zero hardcoded domain rules — fully driven by user inputs and prompt configuration.
"""

import re
from typing import List, Optional, Union, Set

def extract_keyword_terms(keywords_input: Optional[Union[str, List[str]]]) -> List[str]:
    """
    Directly extracts and parses all search terms, phrases, and word stems from user input.
    Handles structured input including:
      - Category colons (e.g. 'Fit & Sizing: fit, size, chart')
      - Numbered bullet lists (e.g. '1. Fit & sizing: "size guide", fit issue')
      - Quoted multi-word phrases (e.g. "true to size", "color mismatch")
      - Comma / newline / semicolon separated lists
    """
    if not keywords_input:
        return []
        
    raw_text = keywords_input if isinstance(keywords_input, str) else ", ".join(keywords_input)
    if not raw_text.strip():
        return []

    terms: Set[str] = set()

    # 1. Extract explicitly quoted phrases
    quoted_matches = re.findall(r'["\']([^"\']+)["\']', raw_text)
    for q in quoted_matches:
        clean_q = q.strip().lower()
        if len(clean_q) >= 2:
            terms.add(clean_q)

    # 2. Clean out quotes and split by common delimiters (commas, newlines, colons, semicolons, pipes, slashes)
    text_unquoted = re.sub(r'["\']', ' ', raw_text)
    raw_tokens = re.split(r'[,;:\n\r\|/]+', text_unquoted)

    for token in raw_tokens:
        # Strip bullet numbers (e.g. '1. ', '2) ') and punctuation
        clean_token = re.sub(r'^\s*\d+[\.\)]\s*', '', token).strip().lower()
        clean_token = clean_token.strip('.-_ !?*()[]{}&')
        if not clean_token or len(clean_token) < 2:
            continue

        # Add the full phrase token (e.g. 'true to size', 'color mismatch', 'add to cart')
        terms.add(clean_token)

        # Also extract individual words from multi-word tokens
        words = re.findall(r'[a-zA-Z0-9_-]+', clean_token)
        for w in words:
            if len(w) >= 2 and w not in {'and', 'the', 'for', 'with', 'from', 'also', 'etc'}:
                terms.add(w)
                # Generate stem for inflected words (e.g. hesitation -> hesitat, sizing -> size/siz, fitting -> fit)
                if len(w) > 5 and w.endswith(('ing', 'ion', 'ity', 'ed', 'es')):
                    stem = re.sub(r'(ing|ion|ity|ed|es)$', '', w)
                    if len(stem) >= 3:
                        terms.add(stem)

    return sorted(list(terms))


def matches_keywords(text: str, keywords: Optional[List[str]]) -> bool:
    """
    Returns True if the text contains ANY of the dynamically extracted keyword terms or stems,
    or True if no keywords are specified.
    """
    if not keywords:
        return True
    if not text:
        return False
        
    text_lower = text.lower()
    
    for kw in keywords:
        if kw in text_lower:
            return True
            
    return False


