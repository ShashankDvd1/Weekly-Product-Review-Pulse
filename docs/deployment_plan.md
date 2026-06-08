# Deployment Plan: Weekly Product Review Pulse

This guide covers how to take your application from localhost to the public internet using **Vercel** (Frontend) and **Render** (Backend).

## 1. Frontend Deployment (Vercel)
Vercel is perfectly optimized for Vite/React applications.

### Steps to Deploy
1. **Push to GitHub**: Push the entire `Weekly-Product-Review-Pulse` repository to a public or private GitHub repository.
2. **Connect to Vercel**:
   * Go to [Vercel.com](https://vercel.com/) and sign in with GitHub.
   * Click **Add New Project** and select your repository.
3. **Configure Build Settings**:
   * **Framework Preset**: Vercel should auto-detect `Vite`.
   * **Root Directory**: Set this to `frontend`.
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
4. **Environment Variables**:
   * *Wait to deploy the backend first*. Once the backend is deployed, you will need to update the `App.jsx` fetch URLs from `http://localhost:8000` to your new Render URL (e.g., `https://review-pulse-api.onrender.com`).
5. **Deploy**: Click "Deploy" and Vercel will host the UI for free.

---

## 2. Backend Deployment (Render)
Render makes deploying Python FastAPI apps very straightforward.

> [!WARNING] 
> **Memory Warning (Free Tier)**
> The application uses heavy Machine Learning models (`BAAI/bge-small-en-v1.5` for embeddings and `en_core_web_lg` for Presidio PII scrubbing). Loading PyTorch and these models into RAM will likely exceed Render's 512MB Free Tier limit, causing an "Out of Memory" (OOM) crash. 
> 
> **Solution**: You will likely need to deploy the backend on Render's **Starter Tier** ($7/mo) which provides more RAM, or explore **Google Cloud Run** which offers up to 2GB RAM on its free tier.

### Steps to Deploy
1. **Prepare for Production**:
   * In `backend/main.py`, ensure your CORS middleware allows your Vercel URL:
     ```python
     allow_origins=["https://your-vercel-app-url.vercel.app"]
     ```
2. **Connect to Render**:
   * Go to [Render.com](https://render.com/) and create a **New Web Service**.
   * Connect your GitHub repository.
3. **Configure the Service**:
   * **Root Directory**: `backend`
   * **Environment**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_lg` *(Note: Since Spacy models aren't standard pip packages, adding the explicit download command ensures Presidio works in the cloud).*
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. **Environment Variables**:
   * Add your `GROQ_API_KEY` in the Render Environment Variables dashboard so it is securely injected into the cloud environment.
5. **Deploy**: Click "Create Web Service". Render will provision the server, install the 400MB models, and give you a public URL (e.g., `https://pulse-api.onrender.com`).

---

## 3. Final Integration
Once Render provides your API URL:
1. Go back to your frontend code in `App.jsx`.
2. Replace `http://localhost:8000` with your new Render URL.
3. Push the changes to GitHub. Vercel will automatically rebuild and deploy the updated frontend!
