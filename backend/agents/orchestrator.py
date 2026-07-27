"""
Pulse Intelligence — Pipeline Orchestrator

Coordinates the full data collection → analysis → reporting pipeline.
This is the "manager agent" that decides what to run, in what order,
and handles errors across the pipeline.
"""

import logging
import os
import json
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from core.config import QUICK_COMMERCE_APPS
from core.llm_client import get_llm_client
from core.schemas import (
    DataSource, UnifiedSignal, CollectionResult,
    Theme, CategoryBarrier, Persona, JTBD, GrowthOpportunity,
    Hypothesis, OptimizedInterviewQuestion, InterviewScriptOutput, ExecutiveSummary,
    FullPipelineRequest, QualityCategory
)
from ingestion.play_store import fetch_play_store_reviews
from ingestion.app_store import fetch_app_store_reviews
from ingestion.reddit import collect_reddit_data
from ingestion.normalizer import (
    normalize_play_store_reviews,
    normalize_app_store_reviews,
    normalize_reddit_data,
    merge_and_deduplicate,
)
from processing.pii_scrubber import scrub_pii_from_text
from reasoning.behavior_analyzer import detect_themes, detect_category_barriers, analyze_sentiment_batch
from reasoning.persona_generator import generate_personas
from reasoning.jtbd_analyzer import analyze_jtbd
from reasoning.opportunity_miner import identify_opportunities
from reasoning.research_copilot import generate_hypotheses, generate_interview_questions
from output.report_generator import generate_executive_summary, generate_category_discovery_report
from output.evidence_builder import (
    compute_source_distribution, compute_sentiment_summary,
    compute_category_mention_counts, compute_behavioral_signal_counts,
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Orchestrates the full intelligence pipeline:
    1. Collect data from all sources
    2. Normalize and deduplicate
    3. Run AI analysis (themes, barriers, personas, JTBD)
    4. Generate reports and recommendations
    """

    def __init__(self):
        self.signals: list[UnifiedSignal] = []
        self.themes: list[Theme] = []
        self.barriers: list[CategoryBarrier] = []
        self.personas: list[Persona] = []
        self.jobs: list[JTBD] = []
        self.opportunities: list[GrowthOpportunity] = []
        self.hypotheses: list[Hypothesis] = []
        self.interview_script = None
        self.executive_summary: Optional[ExecutiveSummary] = None
        self.collection_results: list[CollectionResult] = []
        self.board_evaluation = None
        self.viva_questions = []
        self.viva_session = {
            "active": False,
            "current_question_index": 0,
            "questions": [],
            "answers": [],
            "evaluations": []
        }
        self.mvp_case_study = None
        self.strategy_deep_dive = None
        self.board_presentation = None
        self.active_problem_statement = None
        self.strategy_status = "idle"  # idle, running, completed, failed
        self.strategy_logs = []
        self.strategy_completed_steps = 0
        self.strategy_total_steps = 17
        self._status = "idle"
        self._progress = []

        # Load cached strategy deep dive if available
        try:
            import os
            import json
            cache_path = os.path.join("data", "strategy_cache.json")
            if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.strategy_deep_dive = data.get("strategy_deep_dive")
                    self.board_presentation = data.get("board_presentation")
                    self.mvp_workspace_prd = data.get("mvp_workspace_prd")
                    self.active_problem_statement = data.get("active_problem_statement")
                    
                    # Check status
                    if self.strategy_deep_dive and self.board_presentation:
                        self.strategy_status = "completed"
                        self.strategy_completed_steps = 17
                    elif self.strategy_deep_dive and self.strategy_deep_dive.get("steps") and len(self.strategy_deep_dive["steps"]) < 16:
                        self.strategy_status = "awaiting_survey"
                        self.strategy_completed_steps = len(self.strategy_deep_dive["steps"])
                    elif self.strategy_deep_dive:
                        self.strategy_status = "completed" # fallback
                        self.strategy_completed_steps = 17
                    
                    if self.strategy_deep_dive:
                        if not self.board_presentation and self.strategy_status == "completed":
                            logger.info("Cache has deep dive but lacks board presentation. Synthesizing in background...")
                            def run_bg_synthesis():
                                try:
                                    from reasoning.board_presenter import synthesize_board_presentation
                                    self.board_presentation = synthesize_board_presentation(self.strategy_deep_dive)
                                    # Save back to cache
                                    try:
                                        with open(cache_path, "w", encoding="utf-8") as f_out:
                                            json.dump({
                                                "strategy_deep_dive": self.strategy_deep_dive,
                                                "board_presentation": self.board_presentation,
                                                "active_problem_statement": self.active_problem_statement
                                            }, f_out, indent=2)
                                    except Exception as write_err:
                                        logger.error(f"Failed to write updated cache: {write_err}")
                                except Exception as synth_err:
                                    logger.error(f"Failed to synthesize board presentation in background: {synth_err}")
                            
                            import threading
                            threading.Thread(target=run_bg_synthesis, daemon=True).start()
                        
                        self.strategy_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Loaded strategy deep dive and presentation from local cache file."]
                        logger.info("Loaded strategy deep dive and presentation from local cache file.")
        except Exception as ce:
            logger.error(f"Failed to load strategy cache: {ce}")

        # Load cached pipeline results if available
        try:
            pipeline_cache_path = os.path.join("data", "pipeline_cache.json")
            if os.path.exists(pipeline_cache_path):
                with open(pipeline_cache_path, "r", encoding="utf-8") as f:
                    pc = json.load(f)
                    from core.schemas import UnifiedSignal, Theme, CategoryBarrier, Persona, JTBD, GrowthOpportunity, Hypothesis, ExecutiveSummary
                    self.signals = [UnifiedSignal.model_validate(s) for s in pc.get("signals", [])]
                    self.themes = [Theme.model_validate(t) for t in pc.get("themes", [])]
                    self.barriers = [CategoryBarrier.model_validate(b) for b in pc.get("barriers", [])]
                    self.personas = [Persona.model_validate(p) for p in pc.get("personas", [])]
                    self.jobs = [JTBD.model_validate(j) for j in pc.get("jobs", [])]
                    self.opportunities = [GrowthOpportunity.model_validate(o) for o in pc.get("opportunities", [])]
                    self.hypotheses = [Hypothesis.model_validate(h) for h in pc.get("hypotheses", [])]
                    
                    from core.schemas import InterviewScriptOutput
                    script_data = pc.get("interview_script")
                    self.interview_script = InterviewScriptOutput.model_validate(script_data) if script_data else None
                    
                    summary_data = pc.get("executive_summary")
                    self.executive_summary = ExecutiveSummary.model_validate(summary_data) if summary_data else None
                    
                    from core.schemas import CollectionResult
                    self.collection_results = [CollectionResult.model_validate(c) for c in pc.get("collection_results", [])]
                    
                    self._status = pc.get("status", "complete")
                    self._progress = pc.get("progress", [])
                    logger.info("Successfully loaded ingestion pipeline cache.")
        except Exception as pce:
            logger.error(f"Failed to load pipeline cache: {pce}")

    def run_strategy_deep_dive_async(self, target_phase=1):
        """Runs the Strategy Deep Dive in a background thread with progress logging. Defaults to Phase 1."""
        if self.strategy_status == "running" and target_phase != 2:
            return
        
        self.strategy_status = "running"
        if target_phase == 1 or not hasattr(self, "strategy_logs") or not self.strategy_logs:
            self.strategy_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Strategy Deep Dive analysis pipeline initialized."]
        else:
            self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resuming Strategy Deep Dive (Phase 2)...")
        
        # Extract existing steps from the deep dive state
        existing_steps = self.strategy_deep_dive.get("steps", {}) if self.strategy_deep_dive else {}
        
        # Track completed steps by ID to prevent double-counting
        self.strategy_completed_steps_set = {
            s_id for s_id, s in existing_steps.items() if s.get("status") == "complete"
        }
        if self.board_presentation:
            self.strategy_completed_steps_set.add("step_17")
        self.strategy_completed_steps = len(self.strategy_completed_steps_set)
        
        def progress_cb(step_id, step_title, status, detail=""):
            timestamp = datetime.now().strftime('%H:%M:%S')
            if status == "start":
                msg = f"[{timestamp}] Running {step_id.upper()}: {step_title}..."
            elif status == "complete":
                self.strategy_completed_steps_set.add(step_id)
                self.strategy_completed_steps = len(self.strategy_completed_steps_set)
                msg = f"[{timestamp}] Step {step_id.upper()} completed successfully ({self.strategy_completed_steps}/{self.strategy_total_steps})."
            elif status == "failed":
                msg = f"[{timestamp}] ERROR: Step {step_id.upper()} failed. Details: {detail}"
            self.strategy_logs.append(msg)
            logger.info(msg)

        def on_step_complete(step_id, step_res):
            if not self.strategy_deep_dive:
                self.strategy_deep_dive = {"steps": {}}
            if "steps" not in self.strategy_deep_dive:
                self.strategy_deep_dive["steps"] = {}
            self.strategy_deep_dive["steps"][step_id] = step_res
            # Save strategy deep dive data to file cache incrementally
            try:
                os.makedirs("data", exist_ok=True)
                with open(os.path.join("data", "strategy_cache.json"), "w", encoding="utf-8") as f:
                    json.dump({
                        "strategy_deep_dive": self.strategy_deep_dive,
                        "board_presentation": self.board_presentation,
                        "active_problem_statement": self.active_problem_statement
                    }, f, indent=2)
            except Exception as ce:
                logger.error(f"Failed to auto-save strategy cache step: {ce}")

        try:
            from reasoning.strategy_deep_dive import run_strategy_deep_dive
            problem_stmt = getattr(self, "active_problem_statement", None)
            result = run_strategy_deep_dive(
                self.signals,
                self.themes,
                self.barriers,
                self.personas,
                self.opportunities,
                problem_statement=problem_stmt,
                progress_callback=progress_cb,
                existing_steps=existing_steps,
                on_step_complete=on_step_complete,
                target_phase=target_phase,
                survey_context=self.strategy_deep_dive.get("survey_validation") if self.strategy_deep_dive else None
            )
            self.strategy_deep_dive = result
            
            if target_phase == 1:
                self.strategy_status = "awaiting_survey"
                self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Phase 1 (Discovery) completed successfully. Awaiting Survey Data.")
            else:
                # We are running phase 2 or all, do the presentation synthesis
                progress_cb("step_17", "Board-Level Executive Presentation Synthesis", "start")
                from reasoning.board_presenter import synthesize_board_presentation
                board_deck = synthesize_board_presentation(result)
                self.board_presentation = board_deck
                progress_cb("step_17", "Board-Level Executive Presentation Synthesis", "complete")
                
                self.strategy_status = "completed"
                self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Phase 2 & Executive Presentation completed successfully.")
            
            # Save strategy deep dive data to file cache
            try:
                os.makedirs("data", exist_ok=True)
                with open(os.path.join("data", "strategy_cache.json"), "w", encoding="utf-8") as f:
                    json.dump({
                        "strategy_deep_dive": self.strategy_deep_dive,
                        "board_presentation": self.board_presentation,
                        "active_problem_statement": self.active_problem_statement
                    }, f, indent=2)
                self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Strategy Deep Dive data successfully saved to local file cache.")
            except Exception as ce:
                logger.error(f"Failed to save strategy cache: {ce}")
        except Exception as e:
            self.strategy_status = "failed"
            self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Critical failure in Strategy Deep Dive pipeline: {e}")
            logger.exception("Strategy Deep Dive failed")


    @property
    def status(self) -> str:
        return self._status

    @property
    def progress(self) -> list[str]:
        return self._progress

    def _log_progress(self, message: str):
        """Log and track pipeline progress."""
        self._progress.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        logger.info(message)

    # ── Collection Phase ─────────────────────────
    def collect_all(
        self,
        apps: list[str] = None,
        play_store_package: str = None,
        app_store_id: str = None,
        from_date: str = None,
        to_date: str = None,
        include_reddit: bool = True,
        reddit_subreddits: list[str] = None,
        reddit_search_terms: list[str] = None,
    ) -> list[UnifiedSignal]:
        """
        Collect data, deduplicate, and run the Intelligent Review Quality Filter.
        If valid genuine reviews < target, dynamically expand the date range and retry.
        """
        if apps is None:
            apps = ["zepto", "blinkit", "swiggy_instamart"]

        if (play_store_package or app_store_id) and apps == ["zepto", "blinkit", "swiggy_instamart"]:
            apps = []

        if not from_date or not to_date:
            from datetime import datetime
            from_date = "2024-01-01"
            to_date = datetime.now().strftime("%Y-%m-%d")

        TARGET_GENUINE_REVIEWS = 250
        MAX_RETRIES = 2
        
        current_from_date = from_date
        current_to_date = to_date
        
        self.collection_results = []
        self._progress = []
        all_signals = []
        
        from core.schemas import QualityCategory
        
        for attempt in range(MAX_RETRIES + 1):
            self._log_progress(f"\n🚀 Collection Attempt {attempt + 1}/{MAX_RETRIES + 1} (From: {current_from_date} To: {current_to_date})")
            batch_signals = []
            
            # 1. Custom app targets
            if play_store_package or app_store_id:
                app_name = "Custom Target"
                if play_store_package:
                    try:
                        self._log_progress(f"📱 Collecting Play Store reviews for custom package: {play_store_package}...")
                        df_play = fetch_play_store_reviews(play_store_package, current_from_date, current_to_date, max_reviews=5000)
                        if not df_play.empty:
                            df_play["content"] = df_play["content"].apply(scrub_pii_from_text)
                            normalized = normalize_play_store_reviews(df_play, app_name, play_store_package)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} custom Play Store reviews")
                    except Exception as e:
                        self._log_progress(f"  ❌ Play Store error for {play_store_package}: {str(e)[:100]}")

                if app_store_id:
                    try:
                        self._log_progress(f"🍎 Collecting App Store reviews for custom ID: {app_store_id}...")
                        df_app = fetch_app_store_reviews(app_store_id, current_from_date, current_to_date, max_pages=100)
                        if not df_app.empty:
                            df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                            normalized = normalize_app_store_reviews(df_app, app_name, app_store_id)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} custom App Store reviews")
                        else:
                            self._log_progress(f"  ⚠️ 0 App Store reviews found in selected date range for custom ID: {app_store_id}")
                    except Exception as e:
                        self._log_progress(f"  ❌ App Store error for {app_store_id}: {str(e)[:100]}")

            # 2. Registered catalog apps
            if apps:
                for app_key in apps:
                    app_config = QUICK_COMMERCE_APPS.get(app_key)
                    if not app_config:
                        continue
                    app_name = app_config["name"]
                    package = app_config["play_store_package"]
                    app_store_id_reg = app_config["app_store_id"]

                    try:
                        self._log_progress(f"📱 Collecting Play Store reviews for {app_name}...")
                        df_play = fetch_play_store_reviews(package, current_from_date, current_to_date, max_reviews=5000)
                        if not df_play.empty:
                            df_play["content"] = df_play["content"].apply(scrub_pii_from_text)
                            normalized = normalize_play_store_reviews(df_play, app_name, package)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} Play Store reviews for {app_name}")
                    except Exception as e:
                        self._log_progress(f"  ❌ Play Store error for {app_name}: {str(e)[:100]}")

                    try:
                        self._log_progress(f"🍎 Collecting App Store reviews for {app_name}...")
                        df_app = fetch_app_store_reviews(app_store_id_reg, current_from_date, current_to_date, max_pages=100)
                        if not df_app.empty:
                            df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                            normalized = normalize_app_store_reviews(df_app, app_name, app_store_id_reg)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} App Store reviews for {app_name}")
                        else:
                            self._log_progress(f"  ⚠️ 0 App Store reviews found in selected date range for {app_name}")
                    except Exception as e:
                        self._log_progress(f"  ❌ App Store error for {app_name}: {str(e)[:100]}")

            # 3. Reddit Ingestion
            if include_reddit:
                try:
                    self._log_progress(f"🔴 Collecting Reddit discussions...")
                    reddit_signals = collect_reddit_data(
                        subreddits=reddit_subreddits,
                        search_terms=reddit_search_terms,
                    )
                    if reddit_signals:
                        for sig in reddit_signals:
                            sig["content"] = scrub_pii_from_text(sig["content"])
                        normalized = normalize_reddit_data(reddit_signals)
                        batch_signals.extend(normalized)
                        self._log_progress(f"  ✅ {len(normalized)} Reddit signals collected")
                except Exception as e:
                    self._log_progress(f"  ❌ Reddit error: {str(e)[:100]}")
            
            all_signals.extend(batch_signals)
            
            self._log_progress(f"🧠 Running Intelligent Quality Filter on {len(all_signals)} cumulative signals...")
            from reasoning.quality_filter import assess_review_quality_batch
            assessed_signals = assess_review_quality_batch(all_signals)
            
            accepted_signals_pre = [
                s for s in assessed_signals 
                if getattr(s, 'quality_category', QualityCategory.DISCARD) in [
                    QualityCategory.MEDIUM_SIGNAL, 
                    QualityCategory.HIGH_SIGNAL, 
                    QualityCategory.GOLD_INSIGHT
                ]
            ]
            self._log_progress(f"🏆 Accepted high-signal genuine reviews: {len(accepted_signals_pre)}")
            
            self._log_progress(f"🔄 Deduplicating {len(accepted_signals_pre)} high-signal reviews...")
            from processing.deduplication import semantic_deduplicate
            unique_signals = semantic_deduplicate(accepted_signals_pre)
            self._log_progress(f"✅ Current unique dataset: {len(unique_signals)} signals")
            
            if len(unique_signals) >= TARGET_GENUINE_REVIEWS:
                self.signals = unique_signals
                self._log_progress(f"✅ Reached target of {TARGET_GENUINE_REVIEWS} genuine reviews. Proceeding to analysis.")
                break
            elif attempt < MAX_RETRIES:
                self._log_progress(f"⚠️ Only {len(accepted_signals)} valid reviews found (Target: {TARGET_GENUINE_REVIEWS}). Expanding date range backward...")
                try:
                    from datetime import datetime
                    import datetime as dt
                    from_dt = datetime.strptime(current_from_date, "%Y-%m-%d")
                    new_to_dt = from_dt
                    new_from_dt = from_dt - dt.timedelta(days=90)
                    current_to_date = new_to_dt.strftime("%Y-%m-%d")
                    current_from_date = new_from_dt.strftime("%Y-%m-%d")
                except Exception as e:
                    self._log_progress("❌ Could not expand dates. Aborting retries.")
                    self.signals = accepted_signals
                    break
            else:
                self._log_progress(f"⚠️ Reached max retries. Proceeding with {len(accepted_signals)} valid reviews.")
                self.signals = accepted_signals
                
        return self.signals

    # ── Analysis Phase ─────────────────────────
    def analyze_all(self, problem_statement: Optional[str] = None) -> dict:
        """
        Run the complete AI analysis pipeline on collected signals.
        """
        if not self.signals:
            return {"error": "No signals to analyze. Run collect_all() first."}

        self.active_problem_statement = problem_statement
        self._status = "analyzing"

        from concurrent.futures import ThreadPoolExecutor
        import threading

        lock = threading.Lock()

        def safe_log(msg):
            with lock:
                self._log_progress(msg)

        # Phase 1: Concurrently run independent analyses
        safe_log("🎭 Running parallel ingestion analysis stages...")

        def run_sentiment():
            safe_log("🎭 Running sentiment analysis...")
            try:
                self.signals = analyze_sentiment_batch(self.signals)
                safe_log("  ✅ Sentiment analysis complete")
            except Exception as e:
                logger.error(f"Sentiment analysis failed: {e}")
                safe_log(f"  ❌ Sentiment analysis failed: {e}")

        def run_themes():
            safe_log("🔍 Detecting themes...")
            try:
                self.themes = detect_themes(self.signals, context=problem_statement if problem_statement else "quick commerce category exploration behavior")
                safe_log(f"  ✅ {len(self.themes)} themes detected")
            except Exception as e:
                logger.error(f"Theme detection failed: {e}")
                safe_log(f"  ❌ Theme detection failed: {e}")

        def run_barriers():
            safe_log("🚧 Detecting category exploration barriers...")
            try:
                self.barriers = detect_category_barriers(self.signals, problem_statement=problem_statement)
                safe_log(f"  ✅ {len(self.barriers)} category barriers detected")
            except Exception as e:
                logger.error(f"Category barrier detection failed: {e}")
                safe_log(f"  ❌ Category barrier detection failed: {e}")

        def run_personas():
            safe_log("👤 Generating user personas...")
            try:
                self.personas = generate_personas(self.signals, problem_statement=problem_statement)
                safe_log(f"  ✅ {len(self.personas)} personas generated")
            except Exception as e:
                logger.error(f"Persona generation failed: {e}")
                safe_log(f"  ❌ Persona generation failed: {e}")

        def run_jtbd():
            safe_log("🎯 Extracting Jobs-To-Be-Done...")
            try:
                self.jobs = analyze_jtbd(self.signals, problem_statement=problem_statement)
                safe_log(f"  ✅ {len(self.jobs)} jobs extracted")
            except Exception as e:
                logger.error(f"JTBD analysis failed: {e}")
                safe_log(f"  ❌ JTBD analysis failed: {e}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(run_sentiment),
                executor.submit(run_themes),
                executor.submit(run_barriers),
                executor.submit(run_personas),
                executor.submit(run_jtbd)
            ]
            for f in futures:
                f.result()

        # Phase 2: Opportunity Mining (depends on themes, barriers, personas, jobs)
        safe_log("💡 Identifying growth opportunities...")
        try:
            self.opportunities = identify_opportunities(
                self.themes, self.barriers, self.personas, self.jobs, self.signals, problem_statement=problem_statement
            )
            safe_log(f"  ✅ {len(self.opportunities)} opportunities identified")
        except Exception as e:
            logger.error(f"Opportunity mining failed: {e}")
            safe_log(f"  ❌ Opportunity mining failed: {e}")
            self.opportunities = []

        # Phase 3: Parallel reporting and hypotheses creation
        def run_hypotheses_and_interview():
            safe_log("🔬 Generating research hypotheses...")
            try:
                self.hypotheses = generate_hypotheses(self.barriers, self.opportunities, self.themes)
                safe_log(f"  ✅ {len(self.hypotheses)} hypotheses generated")
            except Exception as e:
                logger.error(f"Hypotheses generation failed: {e}")
                safe_log(f"  ❌ Hypotheses generation failed: {e}")
                self.hypotheses = []

            safe_log("📋 Generating interview questions...")
            try:
                self.interview_script = generate_interview_questions(
                    self.personas, self.barriers, self.hypotheses
                )
                safe_log(f"  ✅ {len(self.interview_script.optimized_script) if self.interview_script else 0} optimized questions generated")
            except Exception as e:
                logger.error(f"Interview script generation failed: {e}")
                safe_log(f"  ❌ Interview script generation failed: {e}")

        def run_summary():
            safe_log("📊 Generating executive summary...")
            try:
                self.executive_summary = generate_executive_summary(
                    self.signals, self.themes, self.barriers,
                    self.personas, self.jobs, self.opportunities,
                )
                safe_log("  ✅ Executive summary generated")
            except Exception as e:
                logger.error(f"Executive summary generation failed: {e}")
                safe_log(f"  ❌ Executive summary generation failed: {e}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(run_hypotheses_and_interview),
                executor.submit(run_summary)
            ]
            for f in futures:
                f.result()

        self._status = "complete"
        safe_log("🎉 Analysis pipeline complete!")
        
        # Save pipeline results to local file cache
        try:
            cache_data = {
                "status": self._status,
                "progress": self._progress,
                "signals": [s.model_dump(mode='json') for s in self.signals],
                "themes": [t.model_dump(mode='json') for t in self.themes],
                "barriers": [b.model_dump(mode='json') for b in self.barriers],
                "personas": [p.model_dump(mode='json') for p in self.personas],
                "jobs": [j.model_dump(mode='json') for j in self.jobs],
                "opportunities": [o.model_dump(mode='json') for o in self.opportunities],
                "hypotheses": [h.model_dump(mode='json') for h in self.hypotheses],
                "interview_script": self.interview_script.model_dump(mode='json') if self.interview_script else None,
                "executive_summary": self.executive_summary.model_dump(mode='json') if self.executive_summary else None,
                "collection_results": [c.model_dump(mode='json') for c in self.collection_results],
            }
            os.makedirs("data", exist_ok=True)
            with open(os.path.join("data", "pipeline_cache.json"), "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
            safe_log("💾 Ingestion pipeline cache successfully saved to local file.")
        except Exception as e:
            logger.error(f"Failed to save pipeline cache: {e}")

        return self.get_full_results()

    # ── Full Pipeline ──────────────────────────
    def run_full_pipeline(self, request: Optional[FullPipelineRequest] = None) -> dict:
        """
        Run the complete pipeline: collect → analyze → report.
        """
        if request is None:
            request = FullPipelineRequest()

        # Reset LLM client fallback state for a fresh execution
        try:
            get_llm_client()._force_fast_model = False
        except Exception:
            pass

        self._status = "collecting"
        try:
            # Collect
            self.collect_all(
                apps=request.apps,
                from_date=request.from_date,
                to_date=request.to_date,
                include_reddit=request.include_reddit,
                play_store_package=request.play_store_package,
                app_store_id=request.app_store_id,
                reddit_subreddits=request.reddit_subreddits,
                reddit_search_terms=request.reddit_search_terms,
            )

            if not self.signals:
                self._status = "idle"
                return {"status": "error", "message": "No data collected from any source"}

            # Analyze
            results = self.analyze_all(problem_statement=request.problem_statement)
            self._status = "complete"

            return results
        except Exception as e:
            logger.exception("Pipeline crashed")
            self._log_progress(f"❌ CRITICAL ERROR: {str(e)}")
            self._status = "error"
            return {"status": "error", "message": str(e)}

    # ── Results ──────────────────────────────
    def get_full_results(self) -> dict:
        """Get all analysis results as a serializable dict."""
        return {
            "status": self._status,
            "progress": self._progress,
            "data_coverage": {
                "total_signals": len(self.signals),
                "source_distribution": compute_source_distribution(self.signals),
                "sentiment_summary": compute_sentiment_summary(self.signals),
                "category_mentions": compute_category_mention_counts(self.signals),
                "behavioral_signals": compute_behavioral_signal_counts(self.signals),
            },
            "themes": [t.model_dump() for t in self.themes],
            "barriers": [b.model_dump() for b in self.barriers],
            "personas": [p.model_dump() for p in self.personas],
            "jobs": [j.model_dump() for j in self.jobs],
            "opportunities": [o.model_dump() for o in self.opportunities],
            "hypotheses": [h.model_dump() for h in self.hypotheses],
            "interview_script": self.interview_script.model_dump() if self.interview_script else None,
            "executive_summary": self.executive_summary.model_dump() if self.executive_summary else None,
            "collection_results": [c.model_dump() for c in self.collection_results],
        }

    def get_dashboard_overview(self) -> dict:
        """Get data for the dashboard overview page."""
        dates = []
        for s in self.signals:
            if s.date:
                if isinstance(s.date, datetime):
                    dates.append(s.date)
                elif isinstance(s.date, str):
                    try:
                        # strip Z or timezone details if necessary
                        clean_date = s.date.split("T")[0]
                        dates.append(datetime.strptime(clean_date, "%Y-%m-%d"))
                    except Exception:
                        pass
        
        min_date = min(dates).strftime("%Y-%m-%d") if dates else None
        max_date = max(dates).strftime("%Y-%m-%d") if dates else None

        return {
            "total_signals": len(self.signals),
            "signals_by_source": compute_source_distribution(self.signals),
            "signals_by_app": {
                app: sum(1 for s in self.signals if s.app_name == app)
                for app in set(s.app_name for s in self.signals)
            },
            "sentiment_summary": compute_sentiment_summary(self.signals),
            "top_themes": [
                {"title": t.title, "sentiment": t.sentiment.value, "confidence": t.confidence, "mentions": t.mention_count}
                for t in self.themes[:5]
            ],
            "top_barriers": [
                {"category": b.category, "type": b.barrier_type.value, "confidence": b.confidence}
                for b in self.barriers[:5]
            ],
            "personas_count": len(self.personas),
            "opportunities_count": len(self.opportunities),
            "date_range": {"from_date": min_date, "to_date": max_date},
            "status": self._status,
            "last_updated": datetime.now().isoformat(),
        }


# Module-level singleton
_orchestrator_instance = None


def get_orchestrator() -> PipelineOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = PipelineOrchestrator()
    return _orchestrator_instance


def reset_orchestrator():
    """Reset the orchestrator (for fresh runs)."""
    global _orchestrator_instance
    _orchestrator_instance = PipelineOrchestrator()
