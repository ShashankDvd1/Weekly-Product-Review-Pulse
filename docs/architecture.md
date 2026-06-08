# Weekly Product Review Pulse — Architecture Document

## High-Level Architecture
The system is divided into a **Frontend (UI)** and a **Backend (Data Pipeline & Orchestration)**, separated by a REST API.

```mermaid
flowchart TD
    subgraph Frontend [Vercel Deployment]
        UI[Vite/React UI]
        Inputs[Inputs: App Package, Dates, Filters]
        Display[Display Report & Teams]
        Actions[Push Buttons: All Teams / Specific Teams]
        
        UI --> Inputs
        Inputs -->|API Call| BackendAPI
    end
    
    subgraph Backend [Render Deployment - FastAPI]
        BackendAPI[FastAPI Endpoint]
        Ingestion[Data Ingestion: Play Store & App Store]
        Filtering[Filtering: Word Count & Emoji]
        PII[PII Scrubbing: Presidio]
        Embedding[Embeddings: BGE]
        Clustering[Clustering: UMAP + HDBSCAN]
        Reasoning[LLM Reasoning: Groq with Quota Manager]
        
        BackendAPI --> Ingestion
        Ingestion --> Filtering
        Filtering --> PII
        PII --> Embedding
        Embedding --> Clustering
        Clustering --> Reasoning
        Reasoning -->|Return JSON Report| UI
    end
    
    subgraph MCP Integration [Local / Separate Service]
        MCP_Docs[Google Docs MCP]
        MCP_Gmail[Gmail MCP]
        
        Actions -->|API Call Trigger| MCP_Trigger[MCP Stub/Client]
        MCP_Trigger --> MCP_Docs
        MCP_Trigger --> MCP_Gmail
    end
```

## Components Breakdown

### 1. Frontend (Vite)
* **Hosting**: Vercel
* **Purpose**: User interaction, input gathering, and report visualization.
* **Features**:
  * Date range selector.
  * Inputs for App Store ID and Play Store Package Name.
  * Sliders/Toggles for minimum word count and emoji inclusion.
  * Report Dashboard to view the final generated pulse grouped by **Team Category** (Product, Engineering, Art, CEO).
  * Manual Push buttons (Global and Team-Specific) to trigger the MCP workflow.

### 2. Backend (FastAPI + Python Data Pipeline)
* **Hosting**: Render
* **Purpose**: Data retrieval and LLM reasoning.
* **Modules**:
  * **`ingestion/`**: Scrapes reviews from Apple App Store (RSS) and Google Play (`google-play-scraper`).
  * **`processing/`**: 
    * Filters reviews based on UI parameters.
    * Scrubs PII using Microsoft Presidio.
    * Generates embeddings using `BAAI/bge-small-en-v1.5`.
    * Clusters reviews using UMAP and HDBSCAN to find centroids.
  * **`reasoning/`**: Uses Groq LLM API to analyze centroid reviews, extract themes, select verbatim quotes (with strict substring validation), and categorize themes by Team. **Includes a Quota Manager** that strictly tracks Tokens Per Minute (TPM) and Requests Per Minute (RPM) using chunking and programmatic delays to prevent rate limit violations.
  * **`output/`**: Formats the reasoning into structured JSON sent back to the Frontend.

### 3. MCP Clients (Output Delivery)
* **Purpose**: Writes to Google Workspace without embedding OAuth tokens directly in the agent.
* **Flow**: 
  * Triggered manually from the Frontend.
  * Takes the structured JSON report and uses the `mcp_client_stub` to mock sending updates to Google Docs and Gmail.
