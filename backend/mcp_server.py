"""
Pulse Intelligence — MCP Server

Exposes all platform capabilities as reusable MCP tools that can be
called by Claude Desktop, Cursor, VS Code, or any MCP-compatible client.

Run as:  python mcp_server.py
"""

import json
import logging
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import run_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("pulse-intelligence")


# ═══════════════════════════════════════════════
#  TOOL DEFINITIONS
# ═══════════════════════════════════════════════

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        # ── Collection Tools ──
        Tool(
            name="collect_playstore_reviews",
            description="Collect Google Play Store reviews for a quick commerce app",
            inputSchema={
                "type": "object",
                "properties": {
                    "package_name": {"type": "string", "description": "Play Store package name (e.g., com.kiranacheckout.customer)"},
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                },
                "required": ["package_name", "from_date", "to_date"],
            },
        ),
        Tool(
            name="collect_appstore_reviews",
            description="Collect Apple App Store reviews for a quick commerce app",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_id": {"type": "string", "description": "App Store ID (e.g., 1575323757 for Zepto)"},
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                },
                "required": ["app_id", "from_date", "to_date"],
            },
        ),
        Tool(
            name="collect_reddit_posts",
            description="Collect Reddit posts and comments about quick commerce apps",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddits": {"type": "array", "items": {"type": "string"}, "description": "List of subreddits to search"},
                    "search_terms": {"type": "array", "items": {"type": "string"}, "description": "Search queries"},
                    "time_filter": {"type": "string", "enum": ["day", "week", "month", "year", "all"], "default": "year"},
                },
            },
        ),

        # ── Analysis Tools ──
        Tool(
            name="run_full_pipeline",
            description="Run the complete intelligence pipeline: collect data from all sources, analyze behavioral patterns, generate insights. This is the primary tool.",
            inputSchema={
                "type": "object",
                "properties": {
                    "apps": {"type": "array", "items": {"type": "string"}, "description": "App keys: zepto, blinkit, swiggy_instamart", "default": ["zepto", "blinkit", "swiggy_instamart"]},
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)", "default": ""},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)", "default": ""},
                    "include_reddit": {"type": "boolean", "default": True},
                },
            },
        ),
        Tool(
            name="detect_themes",
            description="Detect themes and patterns from collected consumer signals",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="detect_category_barriers",
            description="Identify barriers preventing users from exploring new product categories in quick commerce",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_personas",
            description="Generate AI-powered user personas from behavioral signals",
            inputSchema={
                "type": "object",
                "properties": {
                    "num_personas": {"type": "integer", "default": 4, "description": "Number of personas to generate"},
                },
            },
        ),
        Tool(
            name="analyze_jtbd",
            description="Extract Jobs-To-Be-Done from consumer signals",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="identify_opportunities",
            description="Identify growth and product opportunities from analysis results",
            inputSchema={"type": "object", "properties": {}},
        ),

        # ── Research Tools ──
        Tool(
            name="generate_hypotheses",
            description="Generate testable product hypotheses from analysis results",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_interview_questions",
            description="Generate user interview questions for primary research (follows 'The Mom Test' methodology)",
            inputSchema={
                "type": "object",
                "properties": {
                    "num_questions": {"type": "integer", "default": 15},
                },
            },
        ),

        # ── Report Tools ──
        Tool(
            name="generate_executive_summary",
            description="Generate an executive summary of all analysis findings",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_category_discovery_report",
            description="Generate the Category Discovery Report — why users don't explore new categories",
            inputSchema={"type": "object", "properties": {}},
        ),

        # ── Search Tools ──
        Tool(
            name="semantic_search",
            description="Search across all consumer signals using semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
        ),

        # ── Dashboard Tools ──
        Tool(
            name="get_dashboard_overview",
            description="Get aggregated statistics for the intelligence dashboard",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_full_results",
            description="Get all analysis results (themes, barriers, personas, JTBD, opportunities, hypotheses)",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


# ═══════════════════════════════════════════════
#  TOOL IMPLEMENTATIONS
# ═══════════════════════════════════════════════

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle MCP tool calls."""
    try:
        result = _execute_tool(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]
    except Exception as e:
        logger.exception(f"Tool {name} failed")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


def _execute_tool(name: str, arguments: dict) -> dict:
    """Route tool calls to their implementations."""
    from agents.orchestrator import get_orchestrator, reset_orchestrator
    from core.schemas import FullPipelineRequest

    orchestrator = get_orchestrator()

    # ── Collection ──
    if name == "collect_playstore_reviews":
        from ingestion.play_store import fetch_play_store_reviews
        df = fetch_play_store_reviews(
            arguments["package_name"],
            arguments["from_date"],
            arguments["to_date"],
        )
        return {"reviews_count": len(df), "sample": df.head(5).to_dict("records") if not df.empty else []}

    elif name == "collect_appstore_reviews":
        from ingestion.app_store import fetch_app_store_reviews
        df = fetch_app_store_reviews(
            arguments["app_id"],
            arguments["from_date"],
            arguments["to_date"],
        )
        return {"reviews_count": len(df), "sample": df.head(5).to_dict("records") if not df.empty else []}

    elif name == "collect_reddit_posts":
        from ingestion.reddit import collect_reddit_data
        signals = collect_reddit_data(
            subreddits=arguments.get("subreddits"),
            search_terms=arguments.get("search_terms"),
            time_filter=arguments.get("time_filter", "year"),
        )
        return {"signals_count": len(signals), "sample": signals[:3] if signals else []}

    # ── Full Pipeline ──
    elif name == "run_full_pipeline":
        reset_orchestrator()
        orchestrator = get_orchestrator()
        request = FullPipelineRequest(
            apps=arguments.get("apps", ["zepto", "blinkit", "swiggy_instamart"]),
            from_date=arguments.get("from_date", ""),
            to_date=arguments.get("to_date", ""),
            include_reddit=arguments.get("include_reddit", True),
        )
        return orchestrator.run_full_pipeline(request)

    # ── Analysis (require collected data) ──
    elif name == "detect_themes":
        if not orchestrator.signals:
            return {"error": "No data collected. Run 'run_full_pipeline' first."}
        from reasoning.behavior_analyzer import detect_themes
        orchestrator.themes = detect_themes(orchestrator.signals)
        return {"themes": [t.model_dump() for t in orchestrator.themes]}

    elif name == "detect_category_barriers":
        if not orchestrator.signals:
            return {"error": "No data collected. Run 'run_full_pipeline' first."}
        from reasoning.behavior_analyzer import detect_category_barriers
        orchestrator.barriers = detect_category_barriers(orchestrator.signals)
        return {"barriers": [b.model_dump() for b in orchestrator.barriers]}

    elif name == "generate_personas":
        if not orchestrator.signals:
            return {"error": "No data collected. Run 'run_full_pipeline' first."}
        from reasoning.persona_generator import generate_personas
        orchestrator.personas = generate_personas(
            orchestrator.signals,
            num_personas=arguments.get("num_personas", 4),
        )
        return {"personas": [p.model_dump() for p in orchestrator.personas]}

    elif name == "analyze_jtbd":
        if not orchestrator.signals:
            return {"error": "No data collected. Run 'run_full_pipeline' first."}
        from reasoning.jtbd_analyzer import analyze_jtbd
        orchestrator.jobs = analyze_jtbd(orchestrator.signals)
        return {"jobs": [j.model_dump() for j in orchestrator.jobs]}

    elif name == "identify_opportunities":
        if not orchestrator.themes:
            return {"error": "No themes detected. Run analysis first."}
        from reasoning.opportunity_miner import identify_opportunities
        orchestrator.opportunities = identify_opportunities(
            orchestrator.themes, orchestrator.barriers,
            orchestrator.personas, orchestrator.jobs, orchestrator.signals,
        )
        return {"opportunities": [o.model_dump() for o in orchestrator.opportunities]}

    # ── Research ──
    elif name == "generate_hypotheses":
        if not orchestrator.barriers:
            return {"error": "No barriers detected. Run analysis first."}
        from reasoning.research_copilot import generate_hypotheses
        orchestrator.hypotheses = generate_hypotheses(
            orchestrator.barriers, orchestrator.opportunities, orchestrator.themes,
        )
        return {"hypotheses": [h.model_dump() for h in orchestrator.hypotheses]}

    elif name == "generate_interview_questions":
        if not orchestrator.personas:
            return {"error": "No personas generated. Run analysis first."}
        from reasoning.research_copilot import generate_interview_questions
        orchestrator.interview_questions = generate_interview_questions(
            orchestrator.personas, orchestrator.barriers, orchestrator.hypotheses,
            num_questions=arguments.get("num_questions", 15),
        )
        return {"questions": [q.model_dump() for q in orchestrator.interview_questions]}

    # ── Reports ──
    elif name == "generate_executive_summary":
        if not orchestrator.signals:
            return {"error": "No data available. Run the full pipeline first."}
        from output.report_generator import generate_executive_summary
        orchestrator.executive_summary = generate_executive_summary(
            orchestrator.signals, orchestrator.themes, orchestrator.barriers,
            orchestrator.personas, orchestrator.jobs, orchestrator.opportunities,
        )
        return orchestrator.executive_summary.model_dump()

    elif name == "generate_category_discovery_report":
        if not orchestrator.signals:
            return {"error": "No data available. Run the full pipeline first."}
        from output.report_generator import generate_category_discovery_report
        return generate_category_discovery_report(
            orchestrator.signals, orchestrator.barriers,
            orchestrator.personas, orchestrator.opportunities,
            orchestrator.hypotheses,
        )

    # ── Search ──
    elif name == "semantic_search":
        from core.vector_store import semantic_search
        results = semantic_search(arguments["query"], top_k=arguments.get("top_k", 10))
        return results

    # ── Dashboard ──
    elif name == "get_dashboard_overview":
        return orchestrator.get_dashboard_overview()

    elif name == "get_full_results":
        return orchestrator.get_full_results()

    else:
        return {"error": f"Unknown tool: {name}"}


# ═══════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio
    logger.info("Starting Pulse Intelligence MCP Server...")
    asyncio.run(run_server(server))
