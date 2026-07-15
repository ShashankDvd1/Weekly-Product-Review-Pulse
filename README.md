# Pulse Intelligence

An AI-powered Consumer Intelligence Platform that analyzes public signals (App Store, Google Play, Reddit) to extract behavioral patterns, detect category exploration barriers, generate user personas, and mine product growth opportunities.

Evolved from the original **Weekly Product Review Pulse**.

---

## What It Does

Pulse Intelligence goes beyond simple sentiment analysis. By using large language models (Groq Llama 3.3 70B) for deep reasoning, it answers **WHY** users behave the way they do:

1. **Behavioral Pattern Detection**: Identifies habit loops, trust issues, price sensitivity, and discovery gaps.
2. **Category Exploration Barriers**: Why do users stick to familiar categories (like Grocery) and avoid exploring new ones (like Beauty or Electronics)?
3. **User Personas**: AI-generated behavioral archetypes (e.g., "The Routine Buyer", "The Curious Explorer").
4. **Jobs-To-Be-Done (JTBD)**: Extracts functional, emotional, and social jobs users are hiring your product for.
5. **Growth Opportunities**: Synthesizes analysis into prioritized product opportunities.
6. **Research Copilot**: Automatically generates testable hypotheses and "Mom Test" interview questions.

---

## Architecture & Pipeline

The pipeline processes consumer signals through 4 stages:

| Stage | Technology | Description |
|-------|-----------|-------------|
| **1. Collection** | `google-play-scraper`, iTunes RSS, Reddit JSON API | Fetches data from multiple sources in parallel. |
| **2. Normalization** | Pandas, Pydantic, ChromaDB | Standardizes data, detects category/behavioral signals, and performs semantic deduplication using vector embeddings. |
| **3. AI Analysis** | Groq (Llama 3.3 70B), Sentence-Transformers | Deep reasoning to extract themes, barriers, personas, JTBD, and opportunities. |
| **4. Reporting** | Python MCP SDK, Google Sheets (Mocked) | Formats insights into actionable reports, exposes them via MCP tools, and provides a REST API for dashboards. |

---

## Tech Stack

### Backend
- **Framework:** FastAPI + Uvicorn
- **AI/LLM:** Groq API (Llama 3.1 8B for fast tasks, Llama 3.3 70B for deep reasoning)
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Store:** ChromaDB
- **Data Models:** Pydantic
- **PII Detection:** Microsoft Presidio + spaCy (`en_core_web_sm`)

### MCP Integration
- **Protocol:** Model Context Protocol (MCP) via `mcp` Python SDK
- **Server:** Embedded Python MCP server exposing 15+ tools for collection, analysis, and reporting.

### Frontend
- **Framework:** React 18 + Vite (React Router for multi-page dashboard)

---

## Detailed Local Setup Guide

### 1. Backend Setup

#### Prerequisites
- **Python**: 3.10+
- **Git**

#### Steps
1. Navigate to the Backend Folder:
   ```bash
   cd backend
   ```
2. Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   # Windows: .\venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   ```
3. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download spaCy model (for PII scrubbing):
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. Configure Environment Variables:
   Create a `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY="your-groq-api-key-here"
   ```
6. Start the API Server:
   ```bash
   python main.py
   ```
   *Available at `http://localhost:8000`*

### 2. MCP Server Setup

The backend also acts as an MCP server, allowing you to use Pulse Intelligence tools directly in Claude Desktop or Cursor.

1. Ensure the backend environment is set up and activated.
2. Run the MCP server:
   ```bash
   python mcp_server.py
   ```
3. To configure Claude Desktop to use it, add the following to your `claude_desktop_config.json`:
   ```json
   "mcpServers": {
     "pulse-intelligence": {
       "command": "python",
       "args": ["/absolute/path/to/Weekly-Product-Review-Pulse/backend/mcp_server.py"]
     }
   }
   ```

### 3. Frontend Setup (Dashboard)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node Packages:
   ```bash
   npm install
   ```
3. Start the Development Server:
   ```bash
   npm run dev
   ```
   *Available at `http://localhost:5173`*

---

## Backward Compatibility (v1)

The original Weekly Product Review Pulse functionality (fetching Play/App Store reviews, clustering, LLM summarization, and Node.js MCP push to Google Docs/Gmail) remains fully intact via the `/api/generate-report` and `/api/mcp-push` endpoints. The React UI in `frontend/src/App.jsx` still supports this flow.
