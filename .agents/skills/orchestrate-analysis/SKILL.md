---
name: orchestrate-analysis
description: Guide on how to run, configure, and monitor the consumer review analysis pipeline, scrapers, deduplication, and persona generators in this workspace.
---

# IDE Skill: Orchestrate Analysis Pipeline

This skill instructs agents on how the main product review intelligence pipeline is structured, configured, and run.

## 1. Core Architecture

The analysis is managed by a Python singleton orchestrator located in:
* **[orchestrator.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/agents/orchestrator.py)**

The orchestrator coordinates the following sequential steps:
1. **Scraping**: Fetches reviews from Play Store and App Store via [play_store.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/ingestion/play_store.py) and [app_store.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/ingestion/app_store.py).
2. **Deduplication**: Runs semantic similarity deduplication via Sentence Transformers in [deduplication.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/processing/deduplication.py).
3. **Behavioral Analysis**: Detects themes and category barriers using LLMs in [behavior_analyzer.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/behavior_analyzer.py).
4. **JTBD Mining**: Extracts Jobs-To-Be-Done in [jtbd_analyzer.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/jtbd_analyzer.py).
5. **Persona Generation**: Creates user profiles in [persona_generator.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/persona_generator.py).
6. **Review Board Evaluation**: Generates scorecards and visual schemas in [review_board.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/review_board.py).

---

## 2. Configuration & Limits

### Scraper Fetch Limits
* **Play Store**: Configured using the `max_reviews` parameter (currently set to `300`).
* **App Store**: Configured using the `max_pages` parameter (currently set to `4` / `200` reviews).
* Setting limits is done inside the `start_analysis_pipeline` method of `orchestrator.py`.

### LLM Token Downsampling
To prevent hitting API rate limits on Groq free tiers (6,000 TPM limit for Llama 3.3 70B), the pipeline automatically downsamples the unique deduplicated signal dataset down to a maximum of **150 reviews** before sending them to the LLM. 
* Configured by changing `MAX_SIGNALS` in [behavior_analyzer.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/behavior_analyzer.py) and `sample_size` in [jtbd_analyzer.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/jtbd_analyzer.py) and [persona_generator.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/persona_generator.py).

---

## 3. Running & Testing

To test the pipeline via scripts, use:
```powershell
python test_pipeline_run.py
```
This tests the full sequence from scraping to report compilation synchronously.
