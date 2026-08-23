import logging
import sys
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
        if isinstance(results, dict) and results.get("status") == "error":
            raise RuntimeError(results.get("message", "Unknown error in pipeline"))
            
        print("\n=== PIPELINE RUN SUCCESS ===")
        coverage = results.get('data_coverage', {})
        print(f"Total Signals: {coverage.get('total_signals')}")
        print(f"Source Distribution: {coverage.get('source_distribution')}")
        print(f"Sentiment Summary: {coverage.get('sentiment_summary')}")
        print(f"Detected Themes: {len(results.get('themes', []))}")
        print(f"Detected Barriers: {len(results.get('barriers', []))}")
        print(f"Token Usage Summary: {results.get('token_usage')}")
        print("============================\n")
    except Exception as e:
        print("\n=== PIPELINE RUN FAILED ===")
        logging.exception("Error during execution")
        print("\nPipeline Progress Logs:")
        for log_line in orchestrator.progress:
            print(log_line)
        print("===========================\n")
        sys.exit(1)

if __name__ == "__main__":
    test_run()
