# Weekly Product Review Pulse — Implementation Plan (Phase-wise)

This document breaks down the execution of the architecture outlined in `architecture.md` into logical, sequential phases.

## Phase 1: Project Scaffolding & Setup
*Objective: Establish the foundation for both the Vercel frontend and Render backend.*
1. **Repository Setup**: Create the core directory structure (`frontend/` and `backend/`).
2. **Backend Foundation**: Set up the Python virtual environment and `requirements.txt` (FastAPI, uvicorn, presidio, sentence-transformers, groq, etc.). Create the base FastAPI `main.py` entry point.
3. **Frontend Foundation**: Initialize the Vite/React application in the `frontend/` directory and install standard dependencies (e.g., TailwindCSS, Axios).

## Phase 2: Backend — Data Ingestion & Filtering Pipeline
*Objective: Successfully retrieve and clean raw review data based on user input parameters.*
1. **Ingestion Modules**: 
   * Implement `play_store.py` using `google-play-scraper`.
   * Implement `app_store.py` using a standard RSS feed parser.
2. **Filtering Logic**: Create utility functions to filter out reviews below the UI's minimum word count and handle emoji inclusion/exclusion.
3. **PII Scrubbing**: Integrate Microsoft Presidio (`presidio-analyzer`, `presidio-anonymizer`) to redact personal data before passing it down the pipeline.

## Phase 3: Backend — Embeddings, Clustering & Reasoning
*Objective: Transform raw, cleaned reviews into structured insights using free LLM models.*
1. **Embeddings & Clustering**: 
   * Integrate `BAAI/bge-small-en-v1.5` via `sentence-transformers`.
   * Apply UMAP for dimensionality reduction and HDBSCAN to find dense review clusters.
   * Calculate cluster centroids to identify the most representative reviews.
2. **LLM Reasoning & Quota Management (Groq)**: 
   * Use `tiktoken` to count tokens before making API calls to ensure we stay strictly under the Tokens Per Minute (TPM) limit.
   * Implement chunking and explicit `time.sleep()` delays between requests to respect Requests Per Minute (RPM) limits.
   * Construct prompts to pass only the centroid reviews to the Groq API.
   * Extract key themes, verbatim user quotes (enforcing strict substring matches), and action ideas.
   * Ensure the LLM tags each extracted theme with a specific **Team Category** (Product, Engineering, Art, CEO).
   * Implement a fallback that gracefully surfaces quota limits (RPD/TPD) to the UI instead of crashing.

## Phase 4: Backend — APIs & MCP Stubs
*Objective: Expose the pipeline to the UI and prepare the final delivery mechanism.*
1. **API Endpoints**: Finalize the FastAPI routes that the Vite frontend will call (e.g., `/api/generate-report`). Ensure CORS is configured for Vercel.
2. **MCP Client Stubs**: Create the placeholder functions that will eventually call the Google Docs and Gmail MCP servers when triggered by the UI's Push buttons.

## Phase 5: Frontend — UI Implementation & Integration
*Objective: Build the user interface and wire it to the backend.*
1. **Input Interface**: Build the main form allowing users to select the Date Range, input App Store/Play Store IDs, set the minimum word count slider, and toggle emojis.
2. **Data Integration**: Connect the form to the FastAPI backend using API calls (handling loading states while the pipeline runs).
3. **Report Dashboard**: Design the output view to render the generated JSON report. Group the themes beautifully under their respective **Team Categories**.
4. **Action Buttons**: Implement the Global "Push" button and Team-specific dispatch buttons that call the backend's MCP trigger endpoints.

## Phase 6: Testing & Deployment Validation
*Objective: Ensure everything runs smoothly in a production-like environment.*
1. Test end-to-end flow with a real App Package (e.g., Groww) on local development servers.
2. Verify strict quote validation and PII redaction.
3. Prepare deployment configurations for Render (backend) and Vercel (frontend).
