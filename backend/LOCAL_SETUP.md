# Local Setup & Render Optimization Guide

This project is configured with a **Dual-Mode Backend** allowing it to run in two environments:

1. **Lightweight Production Mode (Render)**:
   * Uses no heavy neural network libraries (`torch`, `sentence-transformers`, `chromadb`, `presidio`).
   * Automatically uses scikit-learn's `TfidfVectorizer` for review deduplication, in-memory indexing for searches, and regular expressions for PII scrubbing.
   * Keeps RAM usage under **100MB** (well within Render's Free tier limits) and is extremely fast.

2. **Heavyweight Local Mode**:
   * Uses Sentence Transformers (`all-MiniLM-L6-v2` locally), a persistent `ChromaDB` vector database, and SpaCy/Presidio NLP engines for full semantic matching and entity scrubbing.

---

## 💻 Local Setup Instructions

To run the project locally with full features:

### 1. Install Dependencies
Instead of the lightweight production `requirements.txt`, install from `requirements_local.txt`:
```bash
cd backend
pip install -r requirements_local.txt
```

### 2. Configure Environment Variables
Create or edit your `.env` file in the `backend` directory:
```env
GROQ_API_KEY=your_groq_api_key
# Add other credentials as needed
```

### 3. Run the Server
```bash
uvicorn main:app --reload
```

---

## 🚀 Pushing to Git & GitHub

When pushing these changes to Git / GitHub:

1. Stage all modified and new files:
   ```bash
   git add backend/requirements.txt backend/requirements_local.txt backend/core/vector_store.py backend/processing/deduplication.py backend/processing/pii_scrubber.py backend/LOCAL_SETUP.md
   ```
2. Commit your changes:
   ```bash
   git commit -m "feat: implement dual-mode lightweight backend for Render deployment"
   ```
3. Push to GitHub:
   ```bash
   git push origin main
   ```

Upon pushing, Render will build using the lightweight `requirements.txt` file automatically, preventing any PyTorch memory allocation errors and dramatically speeding up the build and ingestion pipelines!
