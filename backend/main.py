import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ingestion.play_store import fetch_play_store_reviews
from ingestion.app_store import fetch_app_store_reviews
from processing.filtering import filter_reviews
from processing.pii_scrubber import scrub_pii
from processing.clustering import cluster_reviews
from reasoning.summarizer import extract_insights
from output.mcp_client import push_via_mcp

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
        # 1. Ingestion
        df_play = pd.DataFrame()
        if request.play_store_package:
            df_play = fetch_play_store_reviews(
                request.play_store_package, request.from_date, request.to_date, 
                request.lang
            )
            if not df_play.empty:
                df_play['source'] = 'Play Store'
                
        df_app = pd.DataFrame()
        if request.app_store_id:
            df_app = fetch_app_store_reviews(
                request.app_store_id, request.from_date, request.to_date
            )
            if not df_app.empty:
                df_app['source'] = 'App Store'
                
        df = pd.concat([df_play, df_app], ignore_index=True) if not df_play.empty or not df_app.empty else pd.DataFrame()
        
        if df.empty:
            return {"status": "empty", "message": "No reviews found for this period."}
            
        raw_count = len(df)
        
        warning_msg = None
        if raw_count >= 4900:
            oldest_date = df['at'].min()
            to_dt = pd.to_datetime(request.to_date)
            if oldest_date > to_dt:
                warning_msg = "Max Volume Limit Reached! The app has extreme volume, so we capped at the 5,000 most recent reviews and bypassed your requested Date Range. Please try a more recent Date Range."

        # 2. Filtering
        df = filter_reviews(df, request.min_word_count, request.include_emojis)
        if df.empty:
            return {"status": "empty", "message": f"Found {raw_count} raw reviews, but none met the filtering criteria (min {request.min_word_count} words)."}
            
        filtered_count = len(df)

        # 3. PII Scrubbing
        df = scrub_pii(df)

        # 4. Clustering (Find Centroids)
        df = cluster_reviews(df)
        centroids = df[df['is_centroid'] == True]
        llm_count = len(centroids)

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
        result = await push_via_mcp(request.app_name, request.report_data, request.team_category)
        return {
            "status": "success", 
            "message": "Pushed to MCP servers successfully",
            "mcp_response": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
