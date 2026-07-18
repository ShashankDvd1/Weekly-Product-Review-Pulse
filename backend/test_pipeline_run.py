import logging
from datetime import datetime, timedelta
from core.schemas import FullPipelineRequest
from agents.orchestrator import PipelineOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')

def test_run():
    print("Initializing PipelineOrchestrator...")
    orchestrator = PipelineOrchestrator()
    
    # Run from 2025 to today to capture the most recent reviews fetched by the scraper
    yesterday = "2025-01-01"
    today = "2026-07-15"
    
    req = FullPipelineRequest(
        apps=["blinkit"],
        from_date=yesterday,
        to_date=today,
        include_reddit=False
    )
    
    print(f"Running pipeline from {yesterday} to {today}...")
    try:
        results = orchestrator.run_full_pipeline(req)
        print("\n=== PIPELINE RUN SUCCESS ===")
        print(f"Total Signals: {results.get('total_signals')}")
        print(f"Detected Themes: {len(results.get('themes', []))}")
        print(f"Detected Barriers: {len(results.get('barriers', []))}")
        print("============================\n")
    except Exception as e:
        print("\n=== PIPELINE RUN FAILED ===")
        logging.exception("Error during execution")
        print("===========================\n")

if __name__ == "__main__":
    test_run()
