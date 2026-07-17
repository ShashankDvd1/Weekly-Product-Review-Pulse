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
    Hypothesis, InterviewQuestion, ExecutiveSummary,
    FullPipelineRequest,
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
        self.interview_questions: list[InterviewQuestion] = []
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
        self._progress.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {message}")
        logger.info(message)

    # ── Collection Phase ─────────────────────────
    def collect_all(
        self,
        apps: Optional[list[str]] = None,
        from_date: str = "",
        to_date: str = "",
        include_reddit: bool = True,
        play_store_package: Optional[str] = None,
        app_store_id: Optional[str] = None,
        reddit_subreddits: Optional[list[str]] = None,
        reddit_search_terms: Optional[list[str]] = None,
    ) -> list[UnifiedSignal]:
        """
        Collect data from all configured or custom sources.
        """
        self._status = "collecting"
        self._progress = []

        all_signals = []

        # If a custom app target is provided, ignore the default catalog apps list
        # to ensure the pipeline runs only for the user's specific request.
        if (play_store_package or app_store_id) and apps == ["zepto", "blinkit", "swiggy_instamart"]:
            apps = []

        # Set default dates if not provided
        if not from_date or not to_date:
            from_date = "2024-01-01"
            to_date = datetime.now().strftime("%Y-%m-%d")

        # 1. Custom app targets
        if play_store_package or app_store_id:
            app_name = "Custom Target"
            
            if play_store_package:
                try:
                    self._log_progress(f"📱 Collecting Play Store reviews for custom package: {play_store_package}...")
                    df_play = fetch_play_store_reviews(play_store_package, from_date, to_date, max_reviews=30)
                    if not df_play.empty:
                        df_play["content"] = df_play["content"].apply(scrub_pii_from_text)
                        normalized = normalize_play_store_reviews(df_play, app_name, play_store_package)
                        all_signals.extend(normalized)
                        self._log_progress(f"  ✅ {len(normalized)} custom Play Store reviews")
                        self.collection_results.append(CollectionResult(
                            source=DataSource.PLAY_STORE,
                            app_name=app_name,
                            signals_collected=len(df_play),
                            signals_after_filtering=len(normalized),
                        ))
                except Exception as e:
                    self._log_progress(f"  ❌ Play Store error for {play_store_package}: {str(e)[:100]}")

            if app_store_id:
                try:
                    self._log_progress(f"🍎 Collecting App Store reviews for custom ID: {app_store_id}...")
                    df_app = fetch_app_store_reviews(app_store_id, from_date, to_date, max_pages=1)
                    if not df_app.empty:
                        df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                        normalized = normalize_app_store_reviews(df_app, app_name, app_store_id)
                        all_signals.extend(normalized)
                        self._log_progress(f"  ✅ {len(normalized)} custom App Store reviews")
                        self.collection_results.append(CollectionResult(
                            source=DataSource.APP_STORE,
                            app_name=app_name,
                            signals_collected=len(df_app),
                            signals_after_filtering=len(normalized),
                        ))
                except Exception as e:
                    self._log_progress(f"  ❌ App Store error for {app_store_id}: {str(e)[:100]}")

        # 2. Registered catalog apps (if specified)
        if apps:
            for app_key in apps:
                app_config = QUICK_COMMERCE_APPS.get(app_key)
                if not app_config:
                    continue

                app_name = app_config["name"]
                package = app_config["play_store_package"]
                app_store_id_reg = app_config["app_store_id"]

                # Play Store
                try:
                    self._log_progress(f"📱 Collecting Play Store reviews for {app_name}...")
                    df_play = fetch_play_store_reviews(package, from_date, to_date, max_reviews=30)
                    if not df_play.empty:
                        df_play["content"] = df_play["content"].apply(scrub_pii_from_text)
                        normalized = normalize_play_store_reviews(df_play, app_name, package)
                        all_signals.extend(normalized)
                        self._log_progress(f"  ✅ {len(normalized)} Play Store reviews for {app_name}")
                        self.collection_results.append(CollectionResult(
                            source=DataSource.PLAY_STORE,
                            app_name=app_name,
                            signals_collected=len(df_play),
                            signals_after_filtering=len(normalized),
                        ))
                except Exception as e:
                    self._log_progress(f"  ❌ Play Store error for {app_name}: {str(e)[:100]}")

                # App Store
                try:
                    self._log_progress(f"🍎 Collecting App Store reviews for {app_name}...")
                    df_app = fetch_app_store_reviews(app_store_id_reg, from_date, to_date, max_pages=1)
                    if not df_app.empty:
                        df_app["content"] = df_app["content"].apply(scrub_pii_from_text)
                        normalized = normalize_app_store_reviews(df_app, app_name, app_store_id_reg)
                        all_signals.extend(normalized)
                        self._log_progress(f"  ✅ {len(normalized)} App Store reviews for {app_name}")
                        self.collection_results.append(CollectionResult(
                            source=DataSource.APP_STORE,
                            app_name=app_name,
                            signals_collected=len(df_app),
                            signals_after_filtering=len(normalized),
                        ))
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
                    all_signals.extend(normalized)
                    self._log_progress(f"  ✅ {len(normalized)} Reddit signals collected")
                    self.collection_results.append(CollectionResult(
                        source=DataSource.REDDIT,
                        app_name="all",
                        signals_collected=len(reddit_signals),
                        signals_after_filtering=len(normalized),
                    ))
                else:
                    self._log_progress(f"  ⚠️ No Reddit signals found")
            except Exception as e:
                self._log_progress(f"  ❌ Reddit error: {str(e)[:100]}")

        # Deduplicate
        self._log_progress(f"🔄 Deduplicating {len(all_signals)} signals...")
        from processing.deduplication import semantic_deduplicate
        self.signals = semantic_deduplicate(all_signals)
        self._log_progress(f"✅ Final dataset: {len(self.signals)} unique signals")

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
        self.interview_questions = generate_interview_questions(
            self.personas, self.barriers, self.hypotheses
        )
        self._log_progress(f"  ✅ {len(self.interview_questions)} interview questions generated")

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
            return {"status": "error", "message": "No data collected from any source"}

        # Analyze
        results = self.analyze_all()

        return results

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
            "interview_questions": [q.model_dump() for q in self.interview_questions],
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
            "last_updated": datetime.utcnow().isoformat(),
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
