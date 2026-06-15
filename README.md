# Weekly Product Review Pulse

An automated weekly "pulse" that turns public App Store and Google Play reviews for selected products into a one-page insight report and delivers it to stakeholders through Google Workspace, using MCP (Model Context Protocol) to push writes to Google Docs and Gmail.

---

## Architecture & Pipeline

The report generation pipeline processes reviews through 5 optimized stages:

| Stage | Technology | Description |
|-------|-----------|-------------|
| **1. Ingestion** | `google-play-scraper`, iTunes RSS | Fetches up to 500 most recent reviews in parallel (Play Store + App Store concurrently via `ThreadPoolExecutor`) |
| **2. Filtering** | Pandas | Filters by minimum word count and emoji presence |
| **3. Clustering** | `scikit-learn` (TF-IDF + MiniBatchKMeans) | Groups reviews into 5–15 topic clusters and selects the most representative review (centroid) from each |
| **4. PII Scrubbing** | `Presidio` + `spaCy` | Anonymizes names, emails, and phone numbers in centroid reviews only |
| **5. LLM Reasoning** | `Groq` (Llama 3.1 8B) | Extracts themes, quotes, action items, and team assignments from centroids |

**Performance:** Full report generation completes in **~10 seconds** for most apps.

---

## Tech Stack

### Backend
- **Framework:** FastAPI + Uvicorn
- **ML/NLP:** scikit-learn (TF-IDF vectorization + MiniBatchKMeans clustering)
- **PII Detection:** Microsoft Presidio + spaCy (`en_core_web_sm`)
- **LLM:** Groq API (Llama 3.1 8B Instant)
- **Data:** Pandas, NumPy

### Frontend
- **Framework:** React 18 + Vite
- **Language:** JavaScript/JSX

### MCP Integration
- **Protocol:** Model Context Protocol (MCP) via `mcp` Python SDK
- **Server:** Custom Node.js MCP server for Google Docs & Gmail

---

## Detailed Local Setup Guide

### 1. Backend Setup (FastAPI)

#### Prerequisites
- **Python**: Ensure you have Python 3.10 or higher installed. You can check by running `python --version` in your terminal.
- **Git**: Ensure Git is installed to manage the repository.

#### Step-by-Step Setup
1. **Open your Terminal/Command Prompt** and navigate to the project root directory:
   ```bash
   cd Weekly-Product-Review-Pulse
   ```
2. **Navigate to the Backend Folder**:
   ```bash
   cd backend
   ```
3. **Create a Virtual Environment**:
   This keeps the project dependencies isolated from your global Python installation.
   ```bash
   python -m venv venv
   ```
4. **Activate the Virtual Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   *(You should see `(venv)` prepended to your command line prompt).*
5. **Install Dependencies**:
   Install all the packages listed in `requirements.txt` (FastAPI, Uvicorn, Pandas, scikit-learn, etc.):
   ```bash
   pip install -r requirements.txt
   ```
6. **Download Language Models**:
   The application uses `spaCy` and `Presidio` for identifying and scrubbing PII (Personally Identifiable Information). Download the required English model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
7. **Configure Environment Variables**:
   - Create a file named `.env` in the `backend/` directory.
   - Add your Groq API key to the file:
     ```env
     GROQ_API_KEY="your-groq-api-key-here"
     ```
8. **Start the Development Server**:
   ```bash
   python main.py
   ```
   The backend server will launch at `http://localhost:8000`. You can verify it is running by opening `http://localhost:8000/health` in your browser.

---

### 2. Frontend Setup (React + Vite)

#### Prerequisites
- **Node.js**: Ensure you have Node.js (version 18+) installed. Verify with `node -v`.

#### Step-by-Step Setup
1. **Open a new terminal window** and navigate to the frontend directory:
   ```bash
   cd Weekly-Product-Review-Pulse/frontend
   ```
2. **Install Node Packages**:
   Install all required frontend libraries (React, Vite, etc.):
   ```bash
   npm install
   ```
3. **Start the Development Server**:
   ```bash
   npm run dev
   ```
4. **Access the App**:
   Once started, open `http://localhost:5173/` in your web browser to view the application interface.

---

## Detailed Deployment Guide

### 1. Backend Deployment (Render)

Render hosts Python FastAPI applications as Web Services. Follow these steps to deploy:

1. **Push Code to GitHub**: Put your codebase in a GitHub repository.
2. **Log in to Render**: Sign in at [Render.com](https://render.com/).
3. **Create Web Service**:
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository containing the project.
4. **Configure Settings**:
   - **Name**: `review-pulse-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Region**: Select a region close to your target audience.
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 10000
     ```
   - **Plan**: Select **Free** or **Starter**.
5. **Add Environment Variables**:
   - Under the **Environment** tab, click **Add Environment Variable**.
   - Key: `GROQ_API_KEY`
   - Value: `your-groq-api-key`
6. **Deploy**: Click **Create Web Service**. Render will build the environment and provide you with a live URL (e.g., `https://review-pulse-backend.onrender.com`).

---

### 2. Frontend Deployment (Vercel)

Vercel is optimized for building and serving Vite-based React frontends.

1. **Update API Endpoint**:
   - Before deploying the frontend, open `frontend/src/App.jsx`.
   - Update the fetch requests to point to your live Render backend URL instead of `http://localhost:8000`. For example:
     ```javascript
     const response = await fetch('https://review-pulse-backend.onrender.com/api/generate-report', ...
     ```
2. **Push Changes**: Commit and push the updated `App.jsx` to GitHub.
3. **Log in to Vercel**: Sign in at [Vercel.com](https://vercel.com/) with GitHub.
4. **Import Project**:
   - Click **Add New** -> **Project**.
   - Select your repository.
5. **Configure Build**:
   - **Root Directory**: Click "Edit" and choose the `frontend` folder.
   - **Framework Preset**: Verify it defaults to `Vite`.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. **Deploy**: Click **Deploy**. Vercel will build your static files and host them globally on a `*.vercel.app` URL.

---

## MCP (Model Context Protocol) Integration

The project uses a **custom MCP server** (`MCP-Server-For-Reviews-Analyzer`) to push reports to Google Docs and draft notification emails via Gmail. The MCP server stores team members and their email addresses in a local SQLite database.

### How It Works
1. The backend's `mcp_client.py` connects to the Node.js MCP server via `stdio_client`.
2. It calls the `send_report` tool, passing the formatted report content and a `team_name`.
3. The MCP server looks up the team's member emails from its SQLite database (`data/mcp_distribution.db`).
4. It creates a Google Doc with the report and drafts a Gmail notification to all team members.

---

### Configuring Recipient Email Addresses

The LLM assigns each theme to one of 4 teams. You **must** add real email addresses for each team so reports get delivered to the right people.

#### Team Categories

| Team Category | Who Should Receive | Example |
|---|---|---|
| `Product Team` | Product Managers, Product Owners | `pm@yourcompany.com` |
| `Engineer Team` | Engineering Leads, Backend/Frontend Devs | `eng-lead@yourcompany.com` |
| `Art Team` | UI/UX Designers, Visual Designers | `designer@yourcompany.com` |
| `CEO Team` | C-Suite, Leadership, Strategy | `ceo@yourcompany.com` |

#### Where to Add Emails

Navigate to the **MCP Server directory** and use the `manage_team.ts` CLI script:

```bash
cd e:/PM_Portfolio_Projects/MCP-Server-For-Reviews-Analyzer
```

#### Add Members to Teams

```bash
# Product Team
npx ts-node manage_team.ts add "Product Team" pm@yourcompany.com
npx ts-node manage_team.ts add "Product Team" product-owner@yourcompany.com

# Engineer Team
npx ts-node manage_team.ts add "Engineer Team" eng-lead@yourcompany.com
npx ts-node manage_team.ts add "Engineer Team" backend-dev@yourcompany.com

# Art Team
npx ts-node manage_team.ts add "Art Team" ux-designer@yourcompany.com
npx ts-node manage_team.ts add "Art Team" ui-lead@yourcompany.com

# CEO Team
npx ts-node manage_team.ts add "CEO Team" ceo@yourcompany.com
npx ts-node manage_team.ts add "CEO Team" vp-product@yourcompany.com
```

#### View All Teams & Members

```bash
npx ts-node manage_team.ts list
```

#### Remove a Member

```bash
npx ts-node manage_team.ts remove "Engineer Team" old-dev@yourcompany.com
```

> **Note:** The team names used here (`Product Team`, `Engineer Team`, `Art Team`, `CEO Team`) must match exactly what the LLM outputs in the `team_category` field of each theme. The MCP server uses a fuzzy `LIKE` match, so partial matches will also work (e.g., `product` matches `Product Team`).

### Connecting Your Own MCP Server
1. Update the `MCP_SERVER_PATH` in `backend/output/mcp_client.py` to point to your MCP server's entry point.
2. Configure the required environment variables for Google API credentials in your MCP server's `.env` file.
3. Ensure the MCP server exposes a `send_report` tool that accepts `title`, `content`, and optional `team_category` arguments.

---

## Performance Optimizations

The pipeline has been heavily optimized for speed:

- **Parallel Ingestion**: Play Store and App Store reviews are fetched concurrently using `ThreadPoolExecutor`
- **Lightweight Clustering**: Uses TF-IDF + MiniBatchKMeans instead of heavy neural embeddings, completing in <1 second
- **Smart PII Scrubbing**: Only scrubs centroid reviews (10-15) instead of all reviews (500+), and targets only critical PII types (names, emails, phones)
- **Volume Capping**: Limits to 500 most recent reviews — statistically sufficient for theme extraction without the computational overhead of processing thousands

