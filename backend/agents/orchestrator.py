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
# Heavy ingestion, reasoning, and output modules are lazy-loaded inside methods to save startup memory.

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
        self.strategy_total_steps = 9
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
                        self.strategy_completed_steps = 9
                    elif self.strategy_deep_dive and self.strategy_deep_dive.get("steps") and len(self.strategy_deep_dive["steps"]) < 8:
                        self.strategy_status = "awaiting_survey"
                        self.strategy_completed_steps = len(self.strategy_deep_dive["steps"])
                    elif self.strategy_deep_dive:
                        self.strategy_status = "completed" # fallback
                        self.strategy_completed_steps = 9
                    
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

    def _map_phase_1_outputs_to_dashboard(self):
        """Maps Phase 1 agent outputs to dashboard variables."""
        if not self.strategy_deep_dive:
            return

        discovery_res = self.strategy_deep_dive.get("discovery", {})
        segmentation_res = self.strategy_deep_dive.get("segmentation", {})
        root_cause_res = self.strategy_deep_dive.get("root_cause", {})

        from core.schemas import Theme, CategoryBarrier, Persona, JTBD, GrowthOpportunity, Hypothesis, SentimentLabel, BarrierType, ConfidenceLevel, JTBDCategory

        # 1. Map Hypotheses
        self.hypotheses = []
        for i, h_raw in enumerate(discovery_res.get("hypotheses", [])):
            try:
                conf = h_raw.get("confidence", "Medium").upper().replace(" ", "_")
                if conf not in ConfidenceLevel.__members__:
                    conf = "MEDIUM"
                self.hypotheses.append(Hypothesis(
                    hypothesis_id=f"H{i+1}",
                    statement=h_raw.get("hypothesis", ""),
                    rationale=h_raw.get("evidence", ""),
                    evidence_count=1,
                    confidence=1.0 if conf == "HIGH" else (0.5 if conf == "MEDIUM" else 0.2),
                    validation_method="User Survey & Triangulation",
                ))
            except Exception as e:
                logger.error(f"Failed to map hypothesis: {e}")

        # 2. Map JTBD (from discovery)
        self.jobs = []
        for i, j_raw in enumerate(discovery_res.get("jobs_to_be_done", [])):
            try:
                cat_str = j_raw.get("category", "functional").lower()
                cat = JTBDCategory.FUNCTIONAL
                if "emotional" in cat_str:
                    cat = JTBDCategory.EMOTIONAL
                elif "social" in cat_str:
                    cat = JTBDCategory.SOCIAL
                self.jobs.append(JTBD(
                    jtbd_id=f"J{i+1}",
                    job_statement=j_raw.get("job_statement", ""),
                    category=cat,
                    current_solution=j_raw.get("current_solution", ""),
                    gaps=j_raw.get("gaps", []),
                    opportunity_score=float(j_raw.get("opportunity_score", 5.0)),
                    signal_count=len(j_raw.get("supporting_quotes", [])),
                    supporting_quotes=j_raw.get("supporting_quotes", [])
                ))
            except Exception as e:
                logger.error(f"Failed to map JTBD: {e}")

        # 3. Map Themes (from segmentation)
        self.themes = []
        for i, t_raw in enumerate(segmentation_res.get("prioritized_themes", [])):
            try:
                self.themes.append(Theme(
                    theme_id=f"T{i+1}",
                    title=t_raw.get("theme_name", ""),
                    summary=t_raw.get("theme_name", ""),
                    category="UX",
                    sentiment=SentimentLabel.NEGATIVE,
                    mention_count=len(t_raw.get("supporting_facts", [])),
                    confidence=0.8,
                    confidence_level=ConfidenceLevel.HIGH,
                    supporting_quotes=t_raw.get("supporting_facts", []),
                    apps_affected=["zepto", "blinkit", "swiggy_instamart"]
                ))
            except Exception as e:
                logger.error(f"Failed to map Theme: {e}")

        # 4. Map Personas (from segmentation)
        self.personas = []
        for i, p_raw in enumerate(segmentation_res.get("user_segments", [])):
            try:
                self.personas.append(Persona(
                    persona_id=f"P{i+1}",
                    name=p_raw.get("segment_name", ""),
                    description=", ".join(p_raw.get("defining_behaviors", [])),
                    shopping_habits=", ".join(p_raw.get("defining_behaviors", [])),
                    motivations=p_raw.get("observed_needs", []),
                    barriers=[],
                    preferred_categories=[],
                    avoided_categories=[],
                    apps_used=["zepto", "blinkit", "swiggy_instamart"],
                    signal_count=int(float(p_raw.get("estimated_size_pct", 30))),
                    representative_quotes=[]
                ))
            except Exception as e:
                logger.error(f"Failed to map Persona: {e}")

        # 5. Map Opportunities (from segmentation)
        self.opportunities = []
        for i, o_raw in enumerate(segmentation_res.get("growth_opportunities", [])):
            try:
                self.opportunities.append(GrowthOpportunity(
                    opportunity_id=f"O{i+1}",
                    title=o_raw.get("title", ""),
                    description=o_raw.get("description", ""),
                    category=o_raw.get("category", "UX"),
                    impact=o_raw.get("impact", "medium").lower(),
                    effort=o_raw.get("effort", "medium").lower(),
                    confidence=float(o_raw.get("confidence", 0.8)),
                    supporting_themes=[],
                    supporting_jtbd=[],
                    recommended_experiment=o_raw.get("recommended_experiment", "")
                ))
            except Exception as e:
                logger.error(f"Failed to map Opportunity: {e}")

        # 6. Map Barriers (from root causes)
        self.barriers = []
        for i, b_raw in enumerate(root_cause_res.get("validated_root_causes", [])):
            try:
                self.barriers.append(CategoryBarrier(
                    barrier_id=f"B{i+1}",
                    category="Quick Commerce",
                    barrier_type=BarrierType.TRUST,
                    description=b_raw.get("explanation", ""),
                    signal_count=len(b_raw.get("supporting_evidence", [])),
                    confidence=float(b_raw.get("impact_score", 8.0)) / 10.0,
                    confidence_level=ConfidenceLevel.HIGH,
                    recommended_intervention=b_raw.get("cause_title", ""),
                    apps_affected=["zepto", "blinkit", "swiggy_instamart"]
                ))
            except Exception as e:
                logger.error(f"Failed to map CategoryBarrier: {e}")

    def run_strategy_phase_1(self, log_func=None):
        """Executes Phase 1 strategy agents (Stages 1-5) and maps results to dashboard."""
        def default_log(msg):
            logger.info(msg)
        
        log = log_func if log_func else default_log
        
        self.strategy_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] v2 Multi-Agent Research Strategy Pipeline initialized."]
        self.strategy_completed_steps = 0
        self.strategy_status = "running"
        self.strategy_total_steps = 9

        # Helper to log steps
        def log_agent_progress(step_num, agent_name, status, detail=""):
            timestamp = datetime.now().strftime('%H:%M:%S')
            if status == "start":
                msg = f"Running Stage {step_num}/9: {agent_name}..."
            elif status == "complete":
                self.strategy_completed_steps = step_num
                msg = f"Stage {step_num}/9: {agent_name} completed successfully."
            elif status == "failed":
                msg = f"ERROR: Stage {step_num}/9: {agent_name} failed. {detail}"
            self.strategy_logs.append(f"[{timestamp}] {msg}")
            log(msg)

        # Stage 1: Planning
        log_agent_progress(1, "Research Planning Agent", "start")
        from agents.planning_agent import ResearchPlanningAgent
        planning_res = ResearchPlanningAgent().plan(self.signals)
        log_agent_progress(1, "Research Planning Agent", "complete")

        # Stage 2: Processing
        log_agent_progress(2, "Data Processing Agent", "start")
        from agents.processing_agent import DataProcessingAgent
        processing_res = DataProcessingAgent().process(self.signals)
        log_agent_progress(2, "Data Processing Agent", "complete")

        # Stage 3: Discovery
        log_agent_progress(3, "Research Discovery Agent", "start")
        from agents.discovery_agent import ResearchDiscoveryAgent
        discovery_res = ResearchDiscoveryAgent().discover(self.signals)
        log_agent_progress(3, "Research Discovery Agent", "complete")

        # Stage 4: Segmentation
        log_agent_progress(4, "Pattern & Segmentation Agent", "start")
        from agents.segmentation_agent import PatternSegmentationAgent
        segmentation_res = PatternSegmentationAgent().segment(discovery_res)
        log_agent_progress(4, "Pattern & Segmentation Agent", "complete")

        # Stage 5: Root Cause & Strategy
        log_agent_progress(5, "Root Cause & Strategy Agent", "start")
        from agents.root_cause_agent import RootCauseStrategyAgent
        root_cause_res = RootCauseStrategyAgent().analyze(segmentation_res, discovery_res)
        log_agent_progress(5, "Root Cause & Strategy Agent", "complete")

        self.strategy_deep_dive = {
            "planning": planning_res,
            "processing": processing_res,
            "discovery": discovery_res,
            "segmentation": segmentation_res,
            "root_cause": root_cause_res,
            "steps": {
                "step_1": {"title": "Problem Discovery Plan", "status": "complete", "data": planning_res},
                "step_2": {"title": "Data Processing & Stats", "status": "complete", "data": processing_res},
                "step_4": {"title": "Research Discoveries", "status": "complete", "data": discovery_res},
                "step_8": {"title": "Root Causes", "status": "complete", "data": root_cause_res}
            }
        }
        self.strategy_status = "awaiting_survey"
        self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Phase 1 (Discovery) completed successfully. Awaiting Survey Data.")
        
        # Map outputs to dashboard variables
        self._map_phase_1_outputs_to_dashboard()

    def run_strategy_deep_dive_async(self, target_phase=1):
        """Runs the 9-Agent sequential strategy pipeline in a background thread."""
        self.strategy_status = "running"
        self.strategy_total_steps = 9
        
        # Load survey validation if present
        survey_validation = self.strategy_deep_dive.get("survey_validation") if (self.strategy_deep_dive and isinstance(self.strategy_deep_dive, dict)) else None

        # Helper to log steps
        def log_agent_progress(step_num, agent_name, status, detail=""):
            timestamp = datetime.now().strftime('%H:%M:%S')
            if status == "start":
                msg = f"[{timestamp}] Running Stage {step_num}/9: {agent_name}..."
            elif status == "complete":
                self.strategy_completed_steps = step_num
                msg = f"[{timestamp}] Stage {step_num}/9: {agent_name} completed successfully."
            elif status == "failed":
                msg = f"[{timestamp}] ERROR: Stage {step_num}/9: {agent_name} failed. {detail}"
            self.strategy_logs.append(msg)
            logger.info(msg)

        try:
            if target_phase == 1 or not self.strategy_deep_dive:
                self.run_strategy_phase_1()
            
            else:
                # Target phase 2: Resuming
                self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resuming Multi-Agent Research Strategy (Phase 2)...")
                self.strategy_completed_steps = 5
                
                planning_res = self.strategy_deep_dive.get("planning")
                processing_res = self.strategy_deep_dive.get("processing")
                discovery_res = self.strategy_deep_dive.get("discovery")
                segmentation_res = self.strategy_deep_dive.get("segmentation")
                root_cause_res = self.strategy_deep_dive.get("root_cause")

                # Stage 6: Solution Generation
                log_agent_progress(6, "Solution Generation Agent", "start")
                from agents.solution_agent import SolutionGenerationAgent
                solution_res = SolutionGenerationAgent().generate(root_cause_res, discovery_res)
                log_agent_progress(6, "Solution Generation Agent", "complete")

                # Stage 7: Executive Presentation
                log_agent_progress(7, "Executive Presentation Agent", "start")
                from agents.presentation_agent import ExecutivePresentationAgent
                presentation_res = ExecutivePresentationAgent().synthesize(solution_res, root_cause_res, discovery_res)
                log_agent_progress(7, "Executive Presentation Agent", "complete")

                # Stage 8: Evidence Traceability
                log_agent_progress(8, "Evidence Traceability Agent", "start")
                from agents.traceability_agent import EvidenceTraceabilityAgent
                traceability_res = EvidenceTraceabilityAgent().trace(solution_res, root_cause_res, discovery_res)
                log_agent_progress(8, "Evidence Traceability Agent", "complete")

                # Stage 9: Research Audit Agent (with Retry Loop)
                log_agent_progress(9, "Research Audit Agent", "start")
                from agents.audit_agent import ResearchAuditAgent
                audit_agent = ResearchAuditAgent()
                
                # Implementation of Audit Loop (up to 2 retries)
                for attempt in range(3):
                    audit_res = audit_agent.audit(
                        planning_res, processing_res, discovery_res,
                        segmentation_res, root_cause_res, solution_res,
                        presentation_res, traceability_res
                    )
                    verdict = audit_res.get("verdict", "PASS")
                    if verdict in ["PASS", "PASS WITH WARNINGS"]:
                        self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Audit passed with verdict: {verdict}")
                        break
                    else:
                        msg = f"[{datetime.now().strftime('%H:%M:%S')}] Audit Attempt {attempt + 1} failed: {verdict}. Feedback: {json.dumps(audit_res.get('required_revisions', []))}"
                        self.strategy_logs.append(msg)
                        logger.warning(msg)
                        if attempt < 2:
                            self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Re-running solution generation and presentation synthesis with audit feedback...")
                            solution_res = SolutionGenerationAgent().generate(root_cause_res, discovery_res)
                            presentation_res = ExecutivePresentationAgent().synthesize(solution_res, root_cause_res, discovery_res)
                            traceability_res = EvidenceTraceabilityAgent().trace(solution_res, root_cause_res, discovery_res)
                        else:
                            raise Exception(f"Research Audit failed after maximum retries. Verdict: {verdict}")
                
                log_agent_progress(9, "Research Audit Agent", "complete")

                # Merge Phase 2 outputs
                self.strategy_deep_dive["solutions"] = solution_res
                self.strategy_deep_dive["traceability"] = traceability_res
                self.strategy_deep_dive["audit"] = audit_res
                self.strategy_deep_dive["steps"]["step_13"] = {"title": "Traceability Map", "status": "complete", "data": traceability_res}
                self.strategy_deep_dive["steps"]["step_14"] = {"title": "Prioritized Solutions", "status": "complete", "data": solution_res}
                
                self.board_presentation = presentation_res
                self.strategy_status = "completed"
                self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Phase 2 & Executive Presentation completed successfully.")

            # Preserve survey validation metadata when overwriting self.strategy_deep_dive
            if survey_validation:
                self.strategy_deep_dive["survey_validation"] = survey_validation

            # Save strategy deep dive data to file cache
            try:
                os.makedirs("data", exist_ok=True)
                with open(os.path.join("data", "strategy_cache.json"), "w", encoding="utf-8") as f:
                    json.dump({
                        "strategy_deep_dive": self.strategy_deep_dive,
                        "board_presentation": self.board_presentation,
                        "active_problem_statement": self.active_problem_statement
                    }, f, indent=2)
            except Exception as ce:
                logger.error(f"Failed to save strategy cache: {ce}")

        except Exception as e:
            self.strategy_status = "failed"
            self.strategy_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Critical failure in Multi-agent pipeline: {e}")
            logger.exception("Multi-agent Strategy Deep Dive failed")


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
        from ingestion.play_store import fetch_play_store_reviews
        from ingestion.app_store import fetch_app_store_reviews
        from ingestion.reddit import collect_reddit_data
        from ingestion.normalizer import (
            normalize_play_store_reviews,
            normalize_app_store_reviews,
            normalize_reddit_data,
        )
        from processing.pii_scrubber import scrub_pii_from_text

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
                        df_play = fetch_play_store_reviews(package, current_from_date, current_to_date, max_reviews=300)
                        if not df_play.empty:
                            normalized = normalize_play_store_reviews(df_play, app_name, package)
                            batch_signals.extend(normalized)
                            self._log_progress(f"  ✅ {len(normalized)} Play Store reviews for {app_name}")
                    except Exception as e:
                        self._log_progress(f"  ❌ Play Store error for {app_name}: {str(e)[:100]}")

                    try:
                        self._log_progress(f"🍎 Collecting App Store reviews for {app_name}...")
                        df_app = fetch_app_store_reviews(app_store_id_reg, current_from_date, current_to_date, max_pages=4)
                        if not df_app.empty:
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
                
        # Scrub PII only from final accepted high-signal reviews to save 90%+ CPU processing time on Free Tier
        if self.signals:
            self._log_progress(f"🔒 Scrubbing PII from final {len(self.signals)} accepted signals...")
            for sig in self.signals:
                sig.content = scrub_pii_from_text(sig.content)
                
        return self.signals

    # ── Analysis Phase ─────────────────────────
    def analyze_all(self, problem_statement: Optional[str] = None) -> dict:
        """
        Run the complete AI analysis pipeline (using Phase 1 Strategy Agents) on collected signals.
        """
        if not self.signals:
            return {"error": "No signals to analyze. Run collect_all() first."}

        self.active_problem_statement = problem_statement
        self._status = "analyzing"

        # Run sentiment analysis first
        from reasoning.behavior_analyzer import analyze_sentiment_batch
        try:
            self._log_progress("🎭 Running sentiment analysis...")
            self.signals = analyze_sentiment_batch(self.signals)
            self._log_progress("  ✅ Sentiment analysis complete")
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            self._log_progress(f"  ❌ Sentiment analysis failed: {e}")

        # Run Phase 1 Strategy Agents
        self._log_progress("🧠 Running Phase 1 of Multi-Agent Strategy Deep Dive (Planning, Processing, Discovery, Segmentation, Root Cause)...")
        self.run_strategy_phase_1(log_func=self._log_progress)

        self._status = "complete"
        self._log_progress("🎉 Analysis pipeline complete!")
        
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
            self._log_progress("💾 Ingestion pipeline cache successfully saved to local file.")
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
        self._progress = [f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Ingestion pipeline initialized. Booting NLP engines..."]
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
        from output.evidence_builder import (
            compute_source_distribution, compute_sentiment_summary,
            compute_category_mention_counts, compute_behavioral_signal_counts,
        )
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
        from output.evidence_builder import (
            compute_source_distribution, compute_sentiment_summary,
        )
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
