import logging
from datetime import datetime, timedelta
from core.schemas import FullPipelineRequest
from agents.orchestrator import PipelineOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')

def test_run():
    print("Initializing PipelineOrchestrator...")
    orchestrator = PipelineOrchestrator()
    
    # Ingest past 30 days of Nykaa Fashion reviews
    today = datetime.now().strftime("%Y-%m-%d")
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    req = FullPipelineRequest(
        apps=[],
        play_store_package="com.fsn.nds",
        from_date=thirty_days_ago,
        to_date=today,
        include_reddit=False
    )
    
    print(f"Running pipeline for Nykaa Fashion (com.fsn.nds) from {thirty_days_ago} to {today}...")
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
