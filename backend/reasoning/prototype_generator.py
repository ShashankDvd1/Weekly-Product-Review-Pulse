import json
import logging
from core.llm_client import get_llm_client

logger = logging.getLogger(__name__)

def generate_prototype_markdown(strategy_deep_dive_results: dict) -> str:
    """
    Synthesizes Strategy Deep Dive results into a highly detailed, comprehensive
    PRD / Prototype Markdown document designed for direct import into Figma or Lovable.
    """
    llm = get_llm_client()
    
    # Compress deep dive results to fit prompt
    compressed_results = {}
    for step_id, step_val in strategy_deep_dive_results.get("steps", {}).items():
        compressed_results[step_id] = step_val.get("data", {})
        
    if "survey_validation" in strategy_deep_dive_results:
        compressed_results["survey_validation"] = strategy_deep_dive_results["survey_validation"]

    context_str = json.dumps(compressed_results, indent=2)[:15000]

    system_prompt = "You are a Principal Product Designer and Lead Technical PM specializing in high-fidelity prototype specifications."

    user_prompt = f"""Based on the following Strategy Deep Dive analysis, generate a comprehensive, executive-ready Prototype PRD in clean GitHub-Flavored Markdown.
This document will be directly imported into Lovable / Figma / Stitch to build an interactive high-fidelity prototype.

STRATEGY DEEP DIVE DATA:
{context_str}

REQUIREMENTS:
1. Provide extremely specific UI/UX component specs, copy text, exact color codes, micro-interactions, layout structure, and state changes (default, hover, active, empty, error).
2. Detail the exact screen-by-screen breakdown (Screen 1: Cart Drawer Entry, Screen 2: Authenticity Trust Modal, Screen 3: Category Exploration Carousel, etc.).
3. Highlight all Dynamic Trust Cues and Brand Verification Badges (e.g. Origin Seals, Return Guarantees).
4. Outline edge-case handling logic and fail-safes.
5. Do NOT wrap the entire response in markdown code blocks (` ```markdown `). Return raw Markdown directly starting with an # H1 Title.

STRUCTURE YOUR MARKDOWN AS FOLLOWS:
# 🚀 MVP Prototype Specification & Interactive Wireframe PRD

## 1. Executive Summary & Chosen Solution Rationale
- **Core Problem:** ...
- **Winning Solution:** ...
- **Target Cohort:** ...

## 2. Core User Flow & Navigation Architecture
- Step 1 -> Step 2 -> Step 3 flow diagram (text/ASCII format)
- Session trigger conditions and velocity impact

## 3. Screen-by-Screen UI/UX Specifications

### Screen 1: [Screen Name]
- **Purpose:** ...
- **Layout & Structure:** ...
- **UI Components:** ...
- **Trust Badges & Copy:** ...
- **State Behaviors:** (Default / Loading / Success / Empty)

### Screen 2: [Screen Name]
...

### Screen 3: [Screen Name]
...

## 4. Design System & Brand Asset Tokens
- Color Tokens (Primary, Secondary, Accent, Glass Surfaces)
- Typography & Spacing Hierarchy
- Iconography & Badge Assets

## 5. System Logic, Data Triggers & Edge Cases
- **Recommendation Engine Rules:** ...
- **Edge Case 1 & Mitigation:** ...
- **Edge Case 2 & Mitigation:** ...

## 6. Success Tracking & Analytics Events
- Interaction events to log for prototyping analytics
"""

    logger.info("Generating detailed Prototype Markdown...")
    try:
        raw_markdown = llm._call(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=6000
        )
        # Strip potential wrapping backticks if present
        cleaned = raw_markdown.strip()
        if cleaned.startswith("```markdown"):
            cleaned = cleaned[11:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()
    except Exception as e:
        logger.error(f"Failed to generate Prototype Markdown: {e}")
        return f"# Prototype Specification\n\nFailed to generate markdown: {e}"
