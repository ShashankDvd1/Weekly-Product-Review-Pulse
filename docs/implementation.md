# Pulse Intelligence — Implementation Plan (Phase-wise)

> Evolved from Weekly Product Review Pulse into an AI Consumer Intelligence Platform.
> First use case: Quick Commerce Category Discovery Engine (Zepto, Blinkit, Swiggy Instamart).

This document breaks down the execution of the architecture into logical, sequential phases.

---

## Phase 0: Foundation (Completed — Weekly Pulse v1)
*Objective: The original Weekly Product Review Pulse — fully functional.*

1. **Backend**: FastAPI + Python with Play Store + App Store ingestion, TF-IDF clustering, PII scrubbing, Groq LLM reasoning.
2. **Frontend**: React 18 + Vite with report generation UI.
3. **MCP Integration**: Node.js MCP server for Google Docs & Gmail delivery.
4. **Deployed**: Render (backend) + Vercel (frontend).

> ✅ **Status**: Complete. All v1 endpoints preserved at `/api/*`.

---

## Phase 1: Core Infrastructure
*Objective: Build the shared infrastructure that all new features depend on.*

### 1.1 Configuration Management — `core/config.py`
- Centralized configuration for API keys, LLM models, rate limits
- Quick Commerce App Registry (Zepto, Blinkit, Swiggy Instamart with package names, App Store IDs, and category lists)
- Category barrier type definitions
- Confidence scoring thresholds
- Google Sheets configuration

### 1.2 Pydantic Schemas — `core/schemas.py`
- **UnifiedSignal**: Normalized data model across all sources (reviews + Reddit)
- **Theme**: AI-detected theme with evidence chain and confidence scoring
- **CategoryBarrier**: Barrier to category exploration (awareness, trust, habit, price, quality, selection, convenience, discovery)
- **Persona**: Behavioral user archetype
- **JTBD**: Jobs-To-Be-Done with opportunity scoring
- **GrowthOpportunity**: Prioritized product opportunity
- **Hypothesis**: Testable research hypothesis
- **InterviewQuestion**: Generated interview question (Mom Test methodology)
- **ExecutiveSummary**: Report output model
- API request/response models for all v2 endpoints

### 1.3 LLM Client — `core/llm_client.py`
- Unified Groq client wrapper with:
  - Model selection: Llama 3.1 8B (fast/classification) vs Llama 3.3 70B (deep reasoning)
  - Automatic RPM rate limiting with configurable delays
  - Retry with exponential backoff (15s, 30s, 45s)
  - JSON-mode response enforcement
  - Token counting via tiktoken
  - Singleton pattern for connection reuse

### 1.4 Vector Store — `core/vector_store.py`
- ChromaDB persistent client with two collections:
  - `consumer_signals`: All reviews and Reddit signals with embeddings
  - `insights`: AI-generated themes, personas, barriers
- Sentence-transformers embedding model (`all-MiniLM-L6-v2`, 384-dim)
- Operations: store, semantic search, similarity matching
- Lazy model loading to avoid startup delays

---

## Phase 2: Multi-Source Data Collection
*Objective: Extend data collection from 2 sources to 3, with cross-source normalization.*

### 2.1 Reddit Collector — `ingestion/reddit.py`
- Uses Reddit's **public JSON API** (append `.json` to any Reddit URL)
- Zero API key required — rate limited by 2-second delay between requests
- Search across multiple subreddits: `r/india`, `r/bangalore`, `r/mumbai`, `r/indiasocial`
- Search terms: "zepto", "blinkit", "swiggy instamart", "quick commerce", "10 minute delivery"
- Recursive comment extraction (up to depth 5)
- Filtering: minimum upvote score (2+), minimum word count (10+)
- Handles rate limits, removed posts, deleted comments, bot filtering

### 2.2 Data Normalizer — `ingestion/normalizer.py`
- Converts Play Store, App Store, and Reddit data into **UnifiedSignal** schema
- **Category mention detection**: Regex-based detection of 12 product categories (grocery, beauty, electronics, etc.)
- **Behavioral signal detection**: Detects 7 signal types:
  - `habit_loop`: Routine/repeat purchase patterns
  - `trust_issue`: Trust and quality concerns
  - `discovery_gap`: Awareness gaps about available categories
  - `price_sensitivity`: Price comparison and value concerns
  - `convenience_driver`: Convenience and speed motivations
  - `comparison_behavior`: Cross-app comparison signals
  - `emergency_trigger`: Urgency and last-minute purchase triggers
- **App detection**: Identifies which app is mentioned in Reddit posts
- Deterministic ID generation for deduplication

### 2.3 Enhanced Existing Collectors
- Play Store and App Store collectors remain unchanged
- PII scrubbing applied during normalization
- Added to orchestrator for parallel collection

---

## Phase 3: AI Analysis Engine
*Objective: Build the behavioral intelligence layer that answers WHY users behave the way they do.*

### 3.1 Behavioral Pattern Analyzer — `reasoning/behavior_analyzer.py`
- **Theme Detection**: Extracts recurring patterns across all signals using Groq 70B
  - Evidence-grounded themes with confidence scoring
  - Cross-source validation (themes appearing in both reviews AND Reddit get higher confidence)
  - Verbatim quote extraction with validation
- **Category Barrier Detection**: The CORE analysis for the graduation assignment
  - Identifies 8 types of barriers: awareness, trust, habit, price_perception, quality_concern, selection, convenience, discovery
  - Each barrier includes: description, evidence, confidence score, recommended intervention
  - Per-category and per-app breakdown
- **Batch Sentiment Analysis**: Uses the fast 8B model for sentiment classification (-1.0 to 1.0)

### 3.2 Persona Generator — `reasoning/persona_generator.py`
- Generates 4 distinct behavioral archetypes from consumer signals
- Each persona includes:
  - Behavioral profile (not demographics)
  - Specific shopping habits and routines
  - Category preferences and avoidances
  - Motivations and barriers
  - Representative verbatim quotes
- At least one persona represents a "category explorer" (for comparison)

### 3.3 JTBD Analyzer — `reasoning/jtbd_analyzer.py`
- Extracts Jobs-To-Be-Done in the format: "When [situation], I want to [motivation], so I can [outcome]"
- Three job categories: Functional, Emotional, Social
- **Opportunity scoring**: Importance × (1 - Satisfaction) on a 0-10 scale
- Identifies current solutions and unmet gaps
- At least 2 jobs related to category exploration barriers

### 3.4 Opportunity Miner — `reasoning/opportunity_miner.py`
- Synthesizes themes + barriers + personas + JTBD into actionable product opportunities
- Each opportunity includes:
  - Impact/effort assessment (high/medium/low)
  - Target persona
  - Recommended A/B test or pilot experiment
  - Confidence score based on evidence strength
- Prioritized by impact (high first) then effort (low first)

### 3.5 Research Copilot — `reasoning/research_copilot.py`
- **Hypothesis Generation**: Creates falsifiable hypotheses in the format "We believe that [intervention] will [outcome] because [reason]"
  - Each hypothesis includes validation method (A/B test, interview, survey, prototype)
  - At least 4 hypotheses about category exploration barriers
- **Interview Question Generation**: 15 questions following "The Mom Test" methodology
  - Structured flow: warm-up → category behavior → barrier probing → discovery → closing
  - Behavioral questions about past actions (not hypothetical futures)
  - Tied to specific personas and hypotheses

---

## Phase 4: Output & Evidence Layer
*Objective: Build trust in AI outputs through evidence chains and professional reports.*

### 4.1 Evidence Builder — `output/evidence_builder.py`
- **Evidence chain construction**: Links every insight to supporting source data
- **Confidence scoring**: Based on mention count, source diversity, contradiction ratio
  - Very High: 50+ mentions, 3+ sources
  - High: 20+ mentions, 2+ sources
  - Medium: 10+ mentions, 2+ sources
  - Low: 5+ mentions
  - Very Low: <5 mentions
- Aggregate statistics: source distribution, app distribution, sentiment summary, behavioral signal counts, category mention counts

### 4.2 Report Generator — `output/report_generator.py`
- **Executive Summary**: LLM-generated narrative with hard data (counts, distributions, scores)
  - Key findings (5 items)
  - Top opportunities (3 items)
  - Recommended actions (3 items)
- **Category Discovery Report**: The primary assignment deliverable
  - Data coverage statistics
  - Category mention frequency
  - Barriers grouped by type and by category
  - Persona profiles
  - Prioritized opportunities
  - Research hypotheses

---

## Phase 5: Pipeline Orchestration
*Objective: Coordinate all phases into a single runnable pipeline.*

### 5.1 Orchestrator Agent — `agents/orchestrator.py`
- Manages the full pipeline: Collect → Normalize → Analyze → Report
- **Progress tracking**: Real-time status updates with emoji indicators
- **Error isolation**: Individual source failures don't crash the pipeline
- Singleton pattern for state persistence across API calls
- Pipeline steps:
  1. Collect Play Store reviews (per app)
  2. Collect App Store reviews (per app)
  3. Collect Reddit discussions (cross-app)
  4. Normalize and deduplicate all signals
  5. Run sentiment analysis
  6. Detect themes
  7. Detect category barriers
  8. Generate personas
  9. Extract JTBD
  10. Identify opportunities
  11. Generate hypotheses
  12. Generate interview questions
  13. Generate executive summary

---

## Phase 6: MCP Server
*Objective: Expose all platform capabilities as reusable MCP tools.*

### 6.1 Python MCP Server — `mcp_server.py`
- **16 tools** organized into categories:
  - **Collection** (3): `collect_playstore_reviews`, `collect_appstore_reviews`, `collect_reddit_posts`
  - **Analysis** (6): `run_full_pipeline`, `detect_themes`, `detect_category_barriers`, `generate_personas`, `analyze_jtbd`, `identify_opportunities`
  - **Research** (2): `generate_hypotheses`, `generate_interview_questions`
  - **Reports** (2): `generate_executive_summary`, `generate_category_discovery_report`
  - **Search** (1): `semantic_search`
  - **Dashboard** (2): `get_dashboard_overview`, `get_full_results`
- Compatible with: Claude Desktop, Cursor, Windsurf, VS Code, any MCP client
- Transport: stdio (local) and SSE (remote)

---

## Phase 7: API Layer
*Objective: Expose all functionality through REST endpoints.*

### 7.1 FastAPI v2 Endpoints — `main.py`
All original v1 endpoints are **preserved** for backward compatibility:
- `GET /health` — Health check (updated with v2 info)
- `POST /api/generate-report` — Original Weekly Pulse report
- `POST /api/mcp-push` — Push report via MCP

**New v2 endpoints:**
- `POST /api/v2/pipeline/run` — Run the complete intelligence pipeline
- `GET  /api/v2/pipeline/status` — Pipeline progress
- `POST /api/v2/collect/all` — Collect from all sources
- `POST /api/v2/analyze/full` — Run all analysis steps
- `GET  /api/v2/analyze/themes` — Get detected themes
- `GET  /api/v2/analyze/barriers` — Get category barriers
- `GET  /api/v2/analyze/personas` — Get personas
- `GET  /api/v2/analyze/jtbd` — Get JTBD analysis
- `GET  /api/v2/analyze/opportunities` — Get opportunities
- `GET  /api/v2/research/hypotheses` — Get hypotheses
- `GET  /api/v2/research/questions` — Get interview questions
- `GET  /api/v2/reports/executive` — Executive summary
- `GET  /api/v2/reports/category-discovery` — Category Discovery Report
- `GET  /api/v2/dashboard/overview` — Dashboard data
- `GET  /api/v2/dashboard/results` — Full results
- `POST /api/v2/search/semantic` — Semantic search

---

## Phase 8: Frontend Dashboard
*Objective: Evolve the React + Vite frontend into a multi-page intelligence dashboard.*

### 8.1 Pages
- **Dashboard**: Overview with key metrics, source status, sentiment summary
- **Category Discovery**: Barrier visualization, category analysis (assignment deliverable)
- **Personas**: Interactive persona cards with behavioral profiles
- **Evidence Explorer**: Drill into any insight to see supporting evidence
- **Research Copilot**: Hypotheses and interview questions
- **Weekly Pulse**: Original report generation (preserved)

### 8.2 Components
- `SentimentChart` — Sentiment distribution visualization
- `ThemeCard` — Theme display with confidence badge
- `PersonaCard` — Rich persona card with habits, motivations, barriers
- `BarrierMap` — Category barrier visualization
- `EvidenceChain` — Evidence drill-down with source attribution
- `ConfidenceBadge` — Visual confidence level indicator

---

## Phase 9: Testing & Deployment
*Objective: Validate the platform end-to-end and deploy updates.*

1. Test full pipeline with real data (Zepto + Blinkit + Swiggy Instamart).
2. Verify cross-source normalization and deduplication.
3. Validate LLM outputs (themes, barriers, personas) for quality.
4. Check confidence scoring accuracy.
5. Test MCP server with Claude Desktop.
6. Deploy updated backend to Render.
7. Deploy updated frontend to Vercel.
8. Update README with new features and setup instructions.

---

## Architecture Summary

```
DATA SOURCES               PIPELINE                    OUTPUTS
─────────────             ────────                    ───────
Google Play    ─┐
App Store      ─┤─→ Normalize → Deduplicate → PII Scrub
Reddit JSON    ─┘
                    │
                    ▼
              Embed (sentence-transformers)
                    │
                    ▼
              Store (ChromaDB)
                    │
                    ▼
              AI Analysis (Groq 70B)
              ├── Theme Detection
              ├── Category Barriers      ─→  Dashboard
              ├── Persona Generation     ─→  Reports
              ├── JTBD Extraction        ─→  Google Sheets
              ├── Opportunity Mining     ─→  MCP Tools
              ├── Research Copilot       ─→  Claude Desktop
              └── Executive Summary      ─→  REST API
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + Vite | Dashboard UI |
| Backend | FastAPI + Python | API + Orchestration |
| LLM (Fast) | Groq — Llama 3.1 8B | Sentiment, classification |
| LLM (Reasoning) | Groq — Llama 3.3 70B | Behavioral analysis, personas |
| Embeddings | sentence-transformers (MiniLM-L6-v2) | Semantic search, clustering |
| Vector DB | ChromaDB | Embedding storage, similarity search |
| PII Scrubbing | Presidio + spaCy | Privacy protection |
| Clustering | TF-IDF + MiniBatchKMeans | Topic grouping |
| MCP Server | Python `mcp` SDK | Reusable tool exposure |
| Data Storage | Google Sheets | Human-readable data store |
| Backend Hosting | Render (free tier) | API hosting |
| Frontend Hosting | Vercel (free tier) | Dashboard hosting |
| **Total Cost** | **$0/month** | All free tiers |
