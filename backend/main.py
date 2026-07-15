"""
Pulse Intelligence — FastAPI Application

Evolves the original Weekly Product Review Pulse into an AI Consumer
Intelligence Platform with v2 endpoints for multi-source analysis.

Preserves all original /api/* endpoints for backward compatibility.
"""

import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

from ingestion.play_store import fetch_play_store_reviews
from ingestion.app_store import fetch_app_store_reviews

# v2 imports
from core.schemas import (
    FullPipelineRequest, CollectRequest, AnalyzeRequest,
)
from agents.orchestrator import get_orchestrator, reset_orchestrator
from reasoning.prompt_parser import parse_ingestion_prompt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pulse Intelligence API",
    description="AI Consumer Intelligence Platform — Evolved from Weekly Product Review Pulse",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════
#  ORIGINAL v1 ENDPOINTS (preserved)
# ═══════════════════════════════════════════════

class ParsePromptRequest(BaseModel):
    prompt: str

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Pulse Intelligence is running",
        "version": "2.0.0",
        "features": ["category_discovery", "behavioral_analysis"],
    }


# ═══════════════════════════════════════════════
#  v2 ENDPOINTS — Pulse Intelligence Platform
# ═══════════════════════════════════════════════

# ── Full Pipeline ────────────────────────────

@app.post("/api/v2/pipeline/parse-prompt")
def parse_prompt(request: ParsePromptRequest):
    """Parse a natural language pipeline configuration prompt."""
    try:
        config = parse_ingestion_prompt(request.prompt)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/pipeline/run")
def run_full_pipeline(request: FullPipelineRequest):
    """
    Run the complete intelligence pipeline:
    collect from all sources → analyze → generate insights.

    This is the primary endpoint for the platform.
    """
    try:
        reset_orchestrator()
        orchestrator = get_orchestrator()
        results = orchestrator.run_full_pipeline(request)
        return {"status": "success", **results}
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/pipeline/status")
def get_pipeline_status():
    """Get the current status of the pipeline."""
    orchestrator = get_orchestrator()
    return {
        "status": orchestrator.status,
        "progress": orchestrator.progress,
    }


# ── Collection Endpoints ─────────────────────

@app.post("/api/v2/collect/all")
def collect_all_sources(request: CollectRequest):
    """Collect data from all specified sources."""
    try:
        orchestrator = get_orchestrator()
        signals = orchestrator.collect_all(
            apps=request.apps,
            from_date=request.from_date,
            to_date=request.to_date,
        )
        return {
            "status": "success",
            "signals_collected": len(signals),
            "progress": orchestrator.progress,
            "collection_results": [c.model_dump() for c in orchestrator.collection_results],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Analysis Endpoints ────────────────────────

@app.post("/api/v2/analyze/full")
def analyze_all():
    """Run the complete analysis pipeline on collected data."""
    try:
        orchestrator = get_orchestrator()
        if not orchestrator.signals:
            raise HTTPException(status_code=400, detail="No data collected yet. Call /api/v2/collect/all first.")
        results = orchestrator.analyze_all()
        return {"status": "success", **results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/analyze/themes")
def get_themes():
    """Get detected themes."""
    orchestrator = get_orchestrator()
    return {
        "themes": [t.model_dump() for t in orchestrator.themes],
        "count": len(orchestrator.themes),
    }


@app.get("/api/v2/analyze/barriers")
def get_barriers():
    """Get detected category exploration barriers."""
    orchestrator = get_orchestrator()
    return {
        "barriers": [b.model_dump() for b in orchestrator.barriers],
        "count": len(orchestrator.barriers),
    }


@app.get("/api/v2/analyze/personas")
def get_personas():
    """Get generated personas."""
    orchestrator = get_orchestrator()
    return {
        "personas": [p.model_dump() for p in orchestrator.personas],
        "count": len(orchestrator.personas),
    }


@app.get("/api/v2/analyze/jtbd")
def get_jtbd():
    """Get Jobs-To-Be-Done analysis."""
    orchestrator = get_orchestrator()
    return {
        "jobs": [j.model_dump() for j in orchestrator.jobs],
        "count": len(orchestrator.jobs),
    }


@app.get("/api/v2/analyze/opportunities")
def get_opportunities():
    """Get growth opportunities."""
    orchestrator = get_orchestrator()
    return {
        "opportunities": [o.model_dump() for o in orchestrator.opportunities],
        "count": len(orchestrator.opportunities),
    }


# ── Research Copilot ─────────────────────────

@app.get("/api/v2/research/hypotheses")
def get_hypotheses():
    """Get research hypotheses."""
    orchestrator = get_orchestrator()
    return {
        "hypotheses": [h.model_dump() for h in orchestrator.hypotheses],
        "count": len(orchestrator.hypotheses),
    }


@app.get("/api/v2/research/questions")
def get_interview_questions():
    """Get generated interview questions."""
    orchestrator = get_orchestrator()
    return {
        "questions": [q.model_dump() for q in orchestrator.interview_questions],
        "count": len(orchestrator.interview_questions),
    }


# ── Reports ──────────────────────────────────

@app.get("/api/v2/reports/executive")
def get_executive_summary():
    """Get the executive summary."""
    orchestrator = get_orchestrator()
    if orchestrator.executive_summary:
        return orchestrator.executive_summary.model_dump()
    return {"error": "No executive summary generated yet. Run the full pipeline first."}


@app.get("/api/v2/reports/category-discovery")
def get_category_discovery_report():
    """
    Get the Category Discovery Report —
    the primary deliverable for the graduation assignment.
    """
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        return {"error": "No data available. Run the full pipeline first."}

    from output.report_generator import generate_category_discovery_report
    report = generate_category_discovery_report(
        orchestrator.signals,
        orchestrator.barriers,
        orchestrator.personas,
        orchestrator.opportunities,
        orchestrator.hypotheses,
    )
    return report


# ── Dashboard ─────────────────────────────────

@app.get("/api/v2/dashboard/overview")
def get_dashboard_overview():
    """Get aggregated data for the dashboard overview page."""
    orchestrator = get_orchestrator()
    return orchestrator.get_dashboard_overview()


@app.get("/api/v2/dashboard/results")
def get_full_results():
    """Get all analysis results."""
    orchestrator = get_orchestrator()
    return orchestrator.get_full_results()


# ── Search ────────────────────────────────────

@app.post("/api/v2/search/semantic")
def semantic_search_endpoint(query: str, top_k: int = 10):
    """Semantic search across all collected signals."""
    try:
        from core.vector_store import semantic_search
        results = semantic_search(query, top_k=top_k)
        return {"results": results, "query": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
