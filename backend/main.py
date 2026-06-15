import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Load environment variables from .env file
load_dotenv()

from ingestion.play_store import fetch_play_store_reviews
from ingestion.app_store import fetch_app_store_reviews
from processing.filtering import filter_reviews
from processing.pii_scrubber import scrub_pii
from processing.clustering import cluster_reviews
from reasoning.summarizer import extract_insights
from output.mcp_client import push_via_mcp

logger = logging.getLogger(__name__)

app = FastAPI(title="Weekly Product Review Pulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    app_store_id: str | None = None
    play_store_package: str | None = None
    from_date: str
    to_date: str
    lang: str = "en"
    min_word_count: int = 0
    include_emojis: bool = True

class McpPushRequest(BaseModel):
    app_name: str
    report_data: list
    team_category: str | None = None

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running and awake"}

@app.post("/api/generate-report")
def generate_report(request: ReportRequest):
    try:
        # 1. Ingestion (parallel fetch for Play Store + App Store)
        df_play = pd.DataFrame()
        df_app = pd.DataFrame()
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            if request.play_store_package:
                futures['play'] = executor.submit(
                    fetch_play_store_reviews,
                    request.play_store_package, request.from_date, request.to_date, request.lang
                )
            if request.app_store_id:
                futures['app'] = executor.submit(
                    fetch_app_store_reviews,
                    request.app_store_id, request.from_date, request.to_date
                )
            for key, future in futures.items():
                result_df = future.result()
                if not result_df.empty:
                    result_df['source'] = 'Play Store' if key == 'play' else 'App Store'
                    if key == 'play':
                        df_play = result_df
                    else:
                        df_app = result_df
                
        df = pd.concat([df_play, df_app], ignore_index=True) if not df_play.empty or not df_app.empty else pd.DataFrame()
        
        if df.empty:
            return {"status": "empty", "message": "No reviews found for this period."}
        
        raw_count = len(df)
        
        warning_msg = None
        if raw_count >= 450:
            oldest_date = df['at'].min()
            to_dt = pd.to_datetime(request.to_date)
            if oldest_date > to_dt:
                warning_msg = "Max Volume Limit Reached! The app has extreme volume, so we capped at the 500 most recent reviews. Please try a more recent Date Range."

        # 2. Filtering
        df = filter_reviews(df, request.min_word_count, request.include_emojis)
        
        if df.empty:
            return {"status": "empty", "message": f"Found {raw_count} raw reviews, but none met the filtering criteria (min {request.min_word_count} words)."}
            
        filtered_count = len(df)

        # 3. Clustering (TF-IDF + KMeans to find representative centroids)
        df, fallback_used = cluster_reviews(df)
        centroids = df[df['is_centroid'] == True].copy()
        llm_count = len(centroids)

        # 4. PII Scrubbing (only on centroids for speed)
        centroids = scrub_pii(centroids)
        
        if fallback_used:
            fallback_msg = "Low review volume. Clustering couldn't find dense topics, so we randomly sampled a few reviews instead. Try expanding your Date Range or lowering the Minimum Word Count."
            warning_msg = f"{warning_msg} | {fallback_msg}" if warning_msg else fallback_msg
        
        # Save centroids to be fed to LLM
        os.makedirs("output", exist_ok=True)
        centroids.to_json("output/llm_input.json", orient="records", indent=2)

        # 5. LLM Reasoning
        themes = extract_insights(centroids)

        return {
            "status": "success", 
            "data": themes, 
            "raw_count": raw_count,
            "filtered_count": filtered_count,
            "llm_count": llm_count,
            "warning": warning_msg
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp-push")
async def mcp_push(request: McpPushRequest):
    try:
        from output.mcp_client import push_via_mcp
        result = await push_via_mcp(request.app_name, request.report_data, request.team_category)
        if result and isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("detail"))
        return {"status": "success", "docs_response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
