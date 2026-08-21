import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.schemas import FullPipelineRequest
from agents.orchestrator import PipelineOrchestrator

prompt = """You are an expert NLP Data Analyst specializing in E-commerce Growth and Consumer Psychology. Your sole mission is to process raw scraped reviews and extract precise human motivations behind two behaviors:
1. WISHLIST INTENT (Why users add items to a wishlist instead of buying)
2. NON-MONETARY DROP-OFF (Why users leave items in a wishlist without purchasing, excluding discounts/price issues)

---
### INSTRUCTIONS:
Process each review strictly through the following classification framework. Ignore all generic feedback, post-purchase shipping complaints, app crashes, or payment failure bugs. Focus ONLY on pre-purchase hesitation and saving psychology.

1. CLASSIFY INTENT (Select one if present):
   - [MOODBOARD]: Saving for style inspiration, aesthetic matching, or social media outfit ideas (Reels/TikTok/Instagram).
   - [DEFERRED_PURCHASE]: Intending to buy later (salary delay, occasion planning, waiting to buy multiple items together).
   - [COMPARISON]: Saving to compare against alternative fits, brands, or platforms later.

2. CLASSIFY DROP-OFF FRICTION (Select one if present - NON-MONETARY ONLY):
   - [FIT_UNCERTAINTY]: Lack of confidence in sizing, real-life fabric quality, or how it looks on real body types.
   - [TREND_DECAY]: Loss of interest over time, trend expired, or realization that it was an impulse save.
   - [WISHLIST_CLUTTER]: The saved list became too large, disorganized, or overwhelming to review.
   - [STOCK_SENSITIVITY]: Size went out of stock before decision was made, leading to abandonment.

3. NOISE FILTERING RULE:
   - If a review mentions "refund", "delivery boy", "damaged package", "app crash", "OTP", or contains fewer than 4 meaningful words, MARK AS: [FILTERED_OUT]."""

def main():
    print("Initializing pipeline orchestrator...")
    orchestrator = PipelineOrchestrator()
    
    req = FullPipelineRequest(
        apps=[],
        play_store_package="com.myntra.android",
        from_date="2026-07-21",
        to_date="2026-08-20",
        include_reddit=False, # disabled to speed up test slightly
        problem_statement=prompt
    )
    
    print("Running run_full_pipeline to verify full cycle...")
    results = orchestrator.run_full_pipeline(req)
    
    print(f"\nSUCCESS! Pipeline completed.")
    print(f"Total accepted signals: {len(orchestrator.signals)}")
    print(f"Total themes generated: {len(orchestrator.themes)}")
    print(f"Total personas generated: {len(orchestrator.personas)}")
    print(f"Total hypotheses generated: {len(orchestrator.hypotheses)}")
    
    # Clean finish without printing raw strings to avoid Windows console unicode encoding crashes
    pass
        
if __name__ == "__main__":
    main()
