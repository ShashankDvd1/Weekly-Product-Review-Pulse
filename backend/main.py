"""
Pulse Intelligence — FastAPI Application

Evolves the original Weekly Product Review Pulse into an AI Consumer
Intelligence Platform with v2 endpoints for multi-source analysis.

Preserves all original /api/* endpoints for backward compatibility.
"""

import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import csv
import io

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
def run_full_pipeline(request: FullPipelineRequest, background_tasks: BackgroundTasks):
    """
    Run the complete intelligence pipeline asynchronously:
    collect from all sources → analyze → generate insights.

    This is the primary endpoint for the platform.
    """
    try:
        import os
        pipeline_cache_path = os.path.join("data", "pipeline_cache.json")
        if os.path.exists(pipeline_cache_path):
            try:
                os.remove(pipeline_cache_path)
            except Exception:
                pass
        reset_orchestrator()
        orchestrator = get_orchestrator()
        orchestrator._status = "collecting"
        import datetime
        orchestrator._progress = [f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🚀 Ingestion pipeline initialized. Booting NLP engines..."]
        background_tasks.add_task(orchestrator.run_full_pipeline, request)
        return {
            "status": "started",
            "message": "Intelligence pipeline started in background",
            "progress": ["Pipeline execution initialized..."]
        }
    except Exception as e:
        logger.exception("Pipeline failed to start")
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
    if orchestrator.interview_script:
        return orchestrator.interview_script.model_dump()
    return {
        "optimized_script": [],
        "removed_questions": [],
        "missing_questions": [],
        "estimated_duration": "15-20 minutes",
        "quality_score": 0,
        "recommendations": []
    }

class GenerateFormRequest(BaseModel):
    product_name: str
    problem_statement: str
    product_description: str
    target_segment: str
    key_features: str
    assumptions: str

@app.post("/api/v2/research/generate-form")
def generate_survey_form(req: GenerateFormRequest):
    """Automatically generate an AI Survey and optionally a Google Form."""
    from reasoning.form_generator import generate_survey_and_form
    
    try:
        result = generate_survey_and_form(req.model_dump())
        return result
    except Exception as e:
        logger.exception("Failed to generate survey form")
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/api/v2/signals")
def get_all_signals():
    """Get all collected unified signals (reviews, comments)."""
    orchestrator = get_orchestrator()
    return {
        "signals": [s.model_dump() for s in orchestrator.signals],
        "count": len(orchestrator.signals),
    }


@app.get("/api/v2/reports/executive-deck")
def get_executive_deck_report():
    """Generate the AI Executive Insight presentation deck data."""
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        return {"error": "No data available. Run the full pipeline first."}

    from output.report_generator import generate_executive_deck
    try:
        deck = generate_executive_deck(
            orchestrator.signals,
            orchestrator.themes,
            orchestrator.barriers,
            orchestrator.personas,
            orchestrator.jobs,
            orchestrator.opportunities,
        )
        return deck
    except Exception as e:
        logger.exception("Failed to generate executive deck")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/reports/executive-deck/export-slides")
def export_executive_deck_slides_endpoint():
    """Export the AI Executive Insight presentation deck into Google Slides."""
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        raise HTTPException(status_code=400, detail="Executive deck data not generated yet. Run the full pipeline first.")

    from output.report_generator import generate_executive_deck
    try:
        deck_data = generate_executive_deck(
            orchestrator.signals,
            orchestrator.themes,
            orchestrator.barriers,
            orchestrator.personas,
            orchestrator.jobs,
            orchestrator.opportunities,
        )
        from reasoning.mcp_doc_exporter import export_executive_deck_slides
        presentation_url = export_executive_deck_slides(deck_data)
        return {
            "status": "success",
            "presentation_url": presentation_url
        }
    except Exception as e:
        logger.exception("Failed to export executive deck to Google Slides")
        raise HTTPException(status_code=500, detail=str(e))



# ── Review Board ──────────────────────────────

class VivaStartRequest(BaseModel):
    length: int = 10  # 5, 10, or 15 questions


class VivaAnswerRequest(BaseModel):
    answer: str


@app.get("/api/v2/review-board/evaluation")
def get_review_board_evaluation():
    """Get or compile scorecards, dynamic metrics, and visual assets."""
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        return {"error": "No data available. Run the full pipeline first."}

    if orchestrator.board_evaluation is None:
        from reasoning.review_board import generate_board_evaluation
        orchestrator.board_evaluation = generate_board_evaluation(
            orchestrator.signals,
            orchestrator.themes,
            orchestrator.barriers,
            orchestrator.personas,
            orchestrator.jobs,
            orchestrator.opportunities,
            orchestrator.hypotheses,
        )

    return orchestrator.board_evaluation


@app.get("/api/v2/reports/mvp-case")
def get_mvp_case_study_endpoint():
    """Get the PM business case study explaining what MVP was chosen, why, and metric analysis."""
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        return {"error": "No data available. Run the full pipeline first."}

    if orchestrator.mvp_case_study is None:
        from reasoning.review_board import generate_mvp_case_study
        orchestrator.mvp_case_study = generate_mvp_case_study(
            orchestrator.signals,
            orchestrator.themes,
            orchestrator.barriers,
            orchestrator.personas,
            orchestrator.opportunities,
        )

    return orchestrator.mvp_case_study


@app.get("/api/v2/reports/strategy-deep-dive")
def get_strategy_deep_dive(background_tasks: BackgroundTasks):
    """Run or return the 16-step Strategy Deep Dive analysis asynchronously."""
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        return {"error": "No data available. Run the full pipeline first."}

    if orchestrator.strategy_status in ["idle", "failed"]:
        background_tasks.add_task(orchestrator.run_strategy_deep_dive_async)
        
    return {
        "status": orchestrator.strategy_status,
        "logs": orchestrator.strategy_logs,
        "completed_steps": orchestrator.strategy_completed_steps,
        "total_steps": orchestrator.strategy_total_steps,
        "board_presentation": orchestrator.board_presentation if orchestrator.strategy_status == "completed" else None,
        "result": orchestrator.strategy_deep_dive if orchestrator.strategy_deep_dive else None
    }


@app.get("/api/v2/reports/mvp-workspace")
def get_mvp_workspace():
    """Generates or returns the MVP Workspace PRD document based on Deep Dive results."""
    orchestrator = get_orchestrator()
    if orchestrator.strategy_status != "completed" or not orchestrator.strategy_deep_dive:
        return {"error": "Strategy Deep Dive must be completed first."}
        
    # Check if we already generated it
    if hasattr(orchestrator, "mvp_workspace_prd") and orchestrator.mvp_workspace_prd:
        return orchestrator.mvp_workspace_prd
        
    from reasoning.mvp_workspace_generator import generate_mvp_workspace
    prd = generate_mvp_workspace(orchestrator.strategy_deep_dive)
    orchestrator.mvp_workspace_prd = prd
    
    # Save cache
    import json, os
    try:
        cache_path = os.path.join("data", "strategy_cache.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["mvp_workspace_prd"] = prd
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save MVP Workspace to cache: {e}")
        
    return prd


@app.post("/api/v2/reports/strategy-deep-dive/run")
def run_strategy_deep_dive_endpoint(background_tasks: BackgroundTasks):
    """Forces a fresh run of the Strategy Deep Dive by bypassing/deleting cache."""
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        raise HTTPException(status_code=400, detail="No signals available. Run the ingestion pipeline first.")
    
    # Reset status and delete cache file if exists
    import os
    cache_path = os.path.join("data", "strategy_cache.json")
    if os.path.exists(cache_path):
        try:
            os.remove(cache_path)
            logger.info("Deleted strategy cache file to force fresh run.")
        except Exception as e:
            logger.error(f"Failed to delete strategy cache file: {e}")
            
    orchestrator.strategy_status = "idle"
    orchestrator.strategy_deep_dive = None
    orchestrator.board_presentation = None
    orchestrator.strategy_completed_steps = 0
    orchestrator.strategy_logs = []
    
    background_tasks.add_task(orchestrator.run_strategy_deep_dive_async)
    return {"status": "running"}



@app.post("/api/v2/surveys/upload")
async def upload_survey_data(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Uploads survey CSV, analyzes it against Phase 1 insights, and resumes Phase 2."""
    orchestrator = get_orchestrator()
    if orchestrator.strategy_status not in ["awaiting_survey", "completed"] or not orchestrator.strategy_deep_dive:
        raise HTTPException(status_code=400, detail="Phase 1 must be completed before uploading a survey.")

    import pandas as pd
    import io
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    survey_data = df.to_dict('records')

    from reasoning.survey_analyzer import analyze_survey_data
    validation_results = analyze_survey_data(survey_data, orchestrator.strategy_deep_dive.get("steps", {}))
    
    # Store validation results in deep dive
    orchestrator.strategy_deep_dive["survey_validation"] = validation_results
    orchestrator.strategy_status = "running"
    
    # Start Phase 2
    background_tasks.add_task(orchestrator.run_strategy_deep_dive_async, 2)
    return {"status": "success", "message": "Survey analyzed. Phase 2 started."}


@app.post("/api/v2/reports/strategy-deep-dive/export-doc")
def export_strategy_deep_dive_doc_endpoint():
    """Export the 16-step Strategy Deep Dive into a Google Doc saved in the target Drive folder."""
    orchestrator = get_orchestrator()
    if not orchestrator.strategy_deep_dive:
        raise HTTPException(status_code=400, detail="Strategy Deep Dive data not generated yet. Run Deep Strategy Analysis first.")

    try:
        from reasoning.mcp_doc_exporter import export_strategy_deep_dive_doc
        doc_url = export_strategy_deep_dive_doc(orchestrator.strategy_deep_dive)
        return {
            "status": "success",
            "doc_url": doc_url
        }
    except Exception as e:
        logger.exception("Failed to export Strategy Deep Dive to Google Doc")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/reports/strategy-deep-dive/export-slides")
def export_strategy_deep_dive_slides_endpoint():
    """Export the Strategy Deep Dive into a Google Slides presentation saved in the target Drive folder."""
    orchestrator = get_orchestrator()
    if not orchestrator.strategy_deep_dive:
        raise HTTPException(status_code=400, detail="Strategy Deep Dive data not generated yet. Run Deep Strategy Analysis first.")

    try:
        from reasoning.mcp_doc_exporter import export_strategy_deep_dive_slides
        board_deck = orchestrator.board_presentation
        if not board_deck:
            from reasoning.board_presenter import synthesize_board_presentation
            board_deck = synthesize_board_presentation(orchestrator.strategy_deep_dive)
            orchestrator.board_presentation = board_deck
            
        presentation_url = export_strategy_deep_dive_slides(board_deck)
        return {
            "status": "success",
            "presentation_url": presentation_url
        }
    except Exception as e:
        logger.exception("Failed to export Strategy Deep Dive to Google Slides")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/reports/strategy-deep-dive/export-source")
def export_strategy_deep_dive_source():
    """Returns the board presentation raw JSON for design engines."""
    orchestrator = get_orchestrator()
    if not orchestrator.strategy_deep_dive:
        raise HTTPException(status_code=400, detail="Strategy Deep Dive data not generated yet. Run Deep Strategy Analysis first.")
        
    try:
        board_deck = orchestrator.board_presentation
        if not board_deck:
            from reasoning.board_presenter import synthesize_board_presentation
            board_deck = synthesize_board_presentation(orchestrator.strategy_deep_dive)
            orchestrator.board_presentation = board_deck
            
        return {
            "status": "success",
            "source_json": board_deck
        }
    except Exception as e:
        logger.exception("Failed to export Strategy Deep Dive source")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/reports/strategy-deep-dive/export-markdown")
def export_strategy_deep_dive_markdown():
    """Returns the full 16-step Strategy Deep Dive as a Markdown document."""
    orchestrator = get_orchestrator()
    if not orchestrator.strategy_deep_dive:
        raise HTTPException(status_code=400, detail="Strategy Deep Dive data not generated yet. Run Deep Strategy Analysis first.")
        
    try:
        def dict_to_markdown(data, depth=0) -> str:
            if isinstance(data, dict):
                lines = []
                for k, v in data.items():
                    title = k.replace("_", " ").title()
                    if isinstance(v, (dict, list)):
                        lines.append(f"{'  ' * depth}- **{title}**:")
                        lines.append(dict_to_markdown(v, depth + 1))
                    else:
                        lines.append(f"{'  ' * depth}- **{title}**: {v}")
                return "\n".join(lines)
            elif isinstance(data, list):
                lines = []
                for item in data:
                    if isinstance(item, (dict, list)):
                        lines.append(dict_to_markdown(item, depth))
                    else:
                        lines.append(f"{'  ' * depth}- {item}")
                return "\n".join(lines)
            else:
                return f"{'  ' * depth}{data}"

        md_content = f"# Strategy Deep Dive Report\\n\\n"
        steps_dict = orchestrator.strategy_deep_dive.get("steps", {})
        
        # Sort keys numerically (step_1, step_2, ..., step_16)
        sorted_keys = sorted(
            steps_dict.keys(), 
            key=lambda x: int(x.split("_")[1]) if "_" in x and x.split("_")[1].isdigit() else 99
        )
        
        for step_id in sorted_keys:
            step_data = steps_dict[step_id]
            md_content += f"## {step_data.get('title', 'Untitled Step')}\\n\\n"
            
            raw_data = step_data.get("data", {})
            if isinstance(raw_data, dict) and "error" in raw_data:
                md_content += f"⚠️ *Step failed to execute: {raw_data['error']}*\\n\\n"
            else:
                md_content += dict_to_markdown(raw_data) + "\\n\\n"
                
            md_content += "---\\n\\n"
            
        return {
            "status": "success",
            "markdown_content": md_content
        }
    except Exception as e:
        logger.exception("Failed to export Strategy Deep Dive to Markdown")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/review-board/viva/start")
def start_viva_defense(req: VivaStartRequest):
    """Start an interactive Viva Defense session."""
    orchestrator = get_orchestrator()
    
    # Pre-generate questions if empty
    from reasoning.review_board import generate_viva_questions
    if not orchestrator.viva_questions:
        orchestrator.viva_questions = generate_viva_questions(orchestrator.opportunities)

    # Slice questions based on length
    length = min(max(req.length, 5), len(orchestrator.viva_questions))
    selected_questions = orchestrator.viva_questions[:length]

    # Initialize session
    orchestrator.viva_session = {
        "active": True,
        "current_question_index": 0,
        "questions": selected_questions,
        "answers": [],
        "evaluations": []
    }

    first_q = selected_questions[0]
    return {
        "question": first_q,
        "current_index": 0,
        "total_questions": length,
        "active": True
    }


@app.post("/api/v2/review-board/viva/answer")
def submit_viva_answer(req: VivaAnswerRequest):
    """Submit user's Viva response, evaluate, and return progress status."""
    orchestrator = get_orchestrator()
    session = orchestrator.viva_session

    if not session or not session.get("active"):
        raise HTTPException(status_code=400, detail="No active Viva session. Call /viva/start first.")

    current_idx = session["current_question_index"]
    questions = session["questions"]
    current_q = questions[current_idx]

    # Evaluate answer
    from reasoning.review_board import evaluate_viva_answer
    eval_result = evaluate_viva_answer(
        current_q["question"],
        current_q["expected_direction"],
        req.answer
    )

    # Store user response and evaluation
    session["answers"].append(req.answer)
    session["evaluations"].append(eval_result)

    # Check if this was the last question
    completed = current_idx >= len(questions) - 1
    next_q = None

    if not completed:
        session["current_question_index"] += 1
        next_q = questions[session["current_question_index"]]
    else:
        # End session
        session["active"] = False
        # Calculate final viva aggregate score
        scores = [e["score"] for e in session["evaluations"]]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Build portfolio readiness indicator
        eval_result["viva_summary"] = {
            "average_score": avg_score,
            "total_questions": len(questions),
            "evaluations": session["evaluations"]
        }

    return {
        "evaluation": eval_result,
        "next_question": next_q,
        "current_index": session["current_question_index"],
        "completed": completed
    }


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


# ── Blinkit Case Study ──────────────────────────────
from fastapi import UploadFile, File

@app.post("/api/v2/blinkit/analyze")
def run_blinkit_analysis():
    """Run the specialized Blinkit cross-sell analysis on collected signals."""
    orchestrator = get_orchestrator()
    if not orchestrator.signals:
        raise HTTPException(status_code=400, detail="No signals available. Please run the collection pipeline first.")

    if len(orchestrator.signals) < 100:
        raise HTTPException(
            status_code=400, 
            detail=f"Blinkit Case Study requires a minimum of 100 consumer signals to ensure statistical validity (Currently: {len(orchestrator.signals)} signals). Please select a broader date range on the Overview tab and re-run the pipeline."
        )

    from ingestion.normalizer import filter_cross_category_signals
    filtered_signals = filter_cross_category_signals(orchestrator.signals)
    
    if not filtered_signals:
        raise HTTPException(status_code=400, detail="No signals remained after cross-category filtering.")
        
    from reasoning.blinkit_case_study import analyze_blinkit_cross_sell
    problem_stmt = getattr(orchestrator, "active_problem_statement", None)
    result = analyze_blinkit_cross_sell(filtered_signals, problem_statement=problem_stmt)
    
    # Cache the result in orchestrator for synthesis
    orchestrator.blinkit_scraped_insights = result
    
    return {
        "status": "success",
        "filtered_count": len(filtered_signals),
        "insights": result
    }

@app.post("/api/v2/blinkit/upload-survey")
async def upload_blinkit_survey(file: UploadFile = File(...)):
    """Upload Google Form CSV and synthesize with scraped data."""
    import pandas as pd
    from reasoning.blinkit_case_study import synthesize_primary_research
    
    df = pd.read_csv(file.file)
    survey_data = df.to_dict('records')
    
    orchestrator = get_orchestrator()
    scraped_insights = getattr(orchestrator, "blinkit_scraped_insights", {})
    
    result = synthesize_primary_research(scraped_insights, survey_data)
    
    # Write to problem statement doc
    try:
        # Resolve path correctly from backend dir to docs dir
        import os
        docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "Blinkit_Cross_Sell_Growth", "problem_statement.md")
        with open(docs_path, "w", encoding="utf-8") as f:
            f.write(result.get("problem_statement_markdown", "No content generated."))
    except Exception as e:
        logger.error(f"Failed to write problem statement: {e}")
        
    return result

# ═══════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
