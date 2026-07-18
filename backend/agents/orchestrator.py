"""
Pulse Intelligence — Pipeline Orchestrator

Coordinates the full data collection → analysis → reporting pipeline.
This is the "manager agent" that decides what to run, in what order,
and handles errors across the pipeline.
"""

import logging
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
        self._status = "idle"
        self._progress = []

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

        TARGET_GENUINE_REVIEWS = 150
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
                        df_play = fetch_play_store_reviews(play_store_package, current_from_date, current_to_date, max_reviews=300)
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
                        df_app = fetch_app_store_reviews(app_store_id, current_from_date, current_to_date, max_pages=4)
                        if not df_app.empty:
                            df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                            normalized = normalize_app_store_reviews(df_app, app_name, app_store_id)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} custom App Store reviews")
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
                        df_play = fetch_play_store_reviews(package, current_from_date, current_to_date, max_reviews=300)
                        if not df_play.empty:
                            df_play["content"] = df_play["content"].apply(scrub_pii_from_text)
                            normalized = normalize_play_store_reviews(df_play, app_name, package)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} Play Store reviews for {app_name}")
                    except Exception as e:
                        self._log_progress(f"  ❌ Play Store error for {app_name}: {str(e)[:100]}")

                    try:
                        self._log_progress(f"🍎 Collecting App Store reviews for {app_name}...")
                        df_app = fetch_app_store_reviews(app_store_id_reg, current_from_date, current_to_date, max_pages=4)
                        if not df_app.empty:
                            df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                            normalized = normalize_app_store_reviews(df_app, app_name, app_store_id_reg)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} App Store reviews for {app_name}")
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
            
            self._log_progress(f"🔄 Deduplicating {len(all_signals)} cumulative signals...")
            from processing.deduplication import semantic_deduplicate
            unique_signals = semantic_deduplicate(all_signals)
            self._log_progress(f"✅ Current unique dataset: {len(unique_signals)} signals")
            
            self._log_progress(f"🧠 Running Intelligent Quality Filter on {len(unique_signals)} reviews...")
            from reasoning.quality_filter import assess_review_quality_batch
            assessed_signals = assess_review_quality_batch(unique_signals)
            
            accepted_signals = [
                s for s in assessed_signals 
                if getattr(s, 'quality_category', QualityCategory.DISCARD) in [
                    QualityCategory.MEDIUM_SIGNAL, 
                    QualityCategory.HIGH_SIGNAL, 
                    QualityCategory.GOLD_INSIGHT
                ]
            ]
            
            self._log_progress(f"🏆 Accepted high-signal genuine reviews: {len(accepted_signals)}")
            
            if len(accepted_signals) >= TARGET_GENUINE_REVIEWS:
                self.signals = accepted_signals
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
    def analyze_all(self) -> dict:
        """
        Run the complete AI analysis pipeline on collected signals.
        """
        if not self.signals:
            return {"error": "No signals to analyze. Run collect_all() first."}

        self._status = "analyzing"

        # 1. Sentiment Analysis
        self._log_progress(f"🎭 Running sentiment analysis on {len(self.signals)} signals...")
        self.signals = analyze_sentiment_batch(self.signals)
        self._log_progress(f"  ✅ Sentiment analysis complete")

        # 2. Theme Detection
        self._log_progress(f"🔍 Detecting themes...")
        self.themes = detect_themes(self.signals)
        self._log_progress(f"  ✅ {len(self.themes)} themes detected")

        # 3. Category Barrier Detection
        self._log_progress(f"🚧 Detecting category exploration barriers...")
        self.barriers = detect_category_barriers(self.signals)
        self._log_progress(f"  ✅ {len(self.barriers)} category barriers detected")

        # 4. Persona Generation
        self._log_progress(f"👤 Generating user personas...")
        self.personas = generate_personas(self.signals)
        self._log_progress(f"  ✅ {len(self.personas)} personas generated")

        # 5. JTBD Analysis
        self._log_progress(f"🎯 Extracting Jobs-To-Be-Done...")
        self.jobs = analyze_jtbd(self.signals)
        self._log_progress(f"  ✅ {len(self.jobs)} jobs extracted")

        # 6. Opportunity Mining
        self._log_progress(f"💡 Identifying growth opportunities...")
        self.opportunities = identify_opportunities(
            self.themes, self.barriers, self.personas, self.jobs, self.signals
        )
        self._log_progress(f"  ✅ {len(self.opportunities)} opportunities identified")

        # 7. Research Copilot
        self._log_progress(f"🔬 Generating research hypotheses...")
        self.hypotheses = generate_hypotheses(self.barriers, self.opportunities, self.themes)
        self._log_progress(f"  ✅ {len(self.hypotheses)} hypotheses generated")

        self._log_progress(f"📋 Generating interview questions...")
        self.interview_script = generate_interview_questions(
            self.personas, self.barriers, self.hypotheses
        )
        self._log_progress(f"  ✅ {len(self.interview_script.optimized_script) if self.interview_script else 0} optimized questions generated")

        # 8. Executive Summary
        self._log_progress(f"📊 Generating executive summary...")
        self.executive_summary = generate_executive_summary(
            self.signals, self.themes, self.barriers,
            self.personas, self.jobs, self.opportunities,
        )
        self._log_progress(f"  ✅ Executive summary generated")

        self._status = "complete"
        self._log_progress(f"🎉 Analysis pipeline complete!")

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
            results = self.analyze_all()
            self._status = "complete"

            return results
        except Exception as e:
            logger.exception("Pipeline crashed")
            self._log_progress(f"❌ CRITICAL ERROR: {str(e)}")
            self._status = "idle" # Return to idle so frontend stops polling
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
