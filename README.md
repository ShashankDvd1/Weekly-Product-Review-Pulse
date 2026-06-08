# Weekly Product Review Pulse

An automated weekly “pulse” that turns public App Store and Google Play reviews for selected fintech products into a one-page insight report and delivers it to stakeholders through Google Workspace, using MCP (Model Context Protocol) to push writes to Google Docs and Gmail.

---

## Detailed Local Setup Guide

### 1. Backend Setup (FastAPI)

#### Prerequisites
- **Python**: Ensure you have Python 3.10 or higher installed. You can check by running `python --version` in your terminal.
- **Git**: Ensure Git is installed to manage the repository.

#### Step-by-Step Setup
1. **Open your Terminal/Command Prompt** and navigate to the project root directory:
   ```bash
   cd e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse
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
   Install all the packages listed in `requirements.txt` (FastAPI, Uvicorn, Pandas, google-play-scraper, etc.):
   ```bash
   pip install -r requirements.txt
   ```
6. **Download Language Models**:
   The application uses `spaCy` and `Presidio` for identifying and scrubbing PII (Personally Identifiable Information). Download the required English model:
   ```bash
   python -m spacy download en_core_web_lg
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
   cd e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/frontend
   ```
2. **Install Node Packages**:
   Install all required frontend libraries (React, Vite, ESLint, etc.):
   ```bash
   npm install
   ```
3. **Start the Development Server**:
   ```bash
   npm run dev
   ```
   Or if script policies prevent running `.ps1` files on Windows:
   ```powershell
   npm.cmd run dev
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
     pip install -r requirements.txt && python -m spacy download en_core_web_lg
     ```
   - **Start Command**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 10000
     ```
   - **Plan**: Select **Free** (or **Starter** to prevent Out Of Memory crashes due to model size).
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
     and
     ```javascript
     const response = await fetch('https://review-pulse-backend.onrender.com/api/mcp-push', ...
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

The project currently uses **stubs** to simulate MCP interactions (creating/updating Google Docs and drafting emails via Gmail).

### Customizing Google Doc Links & Gmail Details
If you want to configure specific links or modify the simulation behavior:
1. Open the [mcp_client_stub.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/output/mcp_client_stub.py) file.
2. **Google Docs**: Update the returned URL string in the `push_to_google_docs` function:
   ```python
   def push_to_google_docs(app_name: str, report_data: list):
       # Replace the mock link with your team's actual Google Doc URL:
       return {"status": "success", "doc_url": "https://docs.google.com/document/d/your-actual-doc-id-here"}
   ```
3. **Gmail**: Modify the `push_to_gmail` function to update the recipient lists or structure.

### Connecting to Real MCP Servers
To transition from the stubs to production MCP servers (e.g., the official `@modelcontextprotocol/server-google-drive` or custom mail tools):
1. Configure the respective Google Drive/Docs/Gmail MCP servers in your host configuration file (e.g., `claude_desktop_config.json` or equivalent).
2. Update `mcp_client_stub.py` to use an MCP Python client SDK (like `mcp`) to dynamically execute tool calls on those registered servers.

