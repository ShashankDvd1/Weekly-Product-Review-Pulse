# Weekly Product Review Pulse — Edge Cases & Handling Strategies

This document outlines potential edge cases the system may encounter during operation and the planned handling strategies for each.

## 1. Data Ingestion
*   **Invalid App Package / ID**: A user inputs a package name that doesn't exist on the Play Store or App Store.
    *   *Handling*: The FastAPI backend will catch the 404/scraper exception and return a clean HTTP 400 error. The Vite UI will display: *"App not found. Please check the package name or ID."*
*   **No Reviews in Date Range**: The app is valid, but no customers left reviews within the selected "From / To" dates.
    *   *Handling*: The pipeline halts early and returns a 204 No Content or success with an empty state. The UI displays: *"No reviews were posted during this period."*
*   **Massive Volume of Reviews**: A highly popular app (e.g., WhatsApp) returns tens of thousands of reviews, risking memory exhaustion or timeouts.
    *   *Handling*: We will cap the maximum number of reviews fetched per run (e.g., max 5,000) to keep memory usage low and processing fast.
*   **Non-English Reviews**: Reviews are written in languages not optimally supported by the `BGE-small-en` embedding model.
    *   *Handling*: The scraper will be configured to fetch only the `en` (English) region/language by default. 

## 2. Filtering & Processing
*   **Aggressive Filtering Results in 0 Reviews**: A user sets the minimum word count slider to 100, and zero reviews meet the criteria.
    *   *Handling*: The pipeline detects an empty dataset post-filtering and immediately returns to the UI: *"No reviews met your filtering criteria. Try lowering the word count."*
*   **Extremely Long Reviews (Spam)**: A user pastes a massive crash log or spam text into a review (e.g., 2,000 words).
    *   *Handling*: Before processing, reviews longer than a reasonable threshold (e.g., 200 words) will be truncated to prevent them from skewing the clustering or consuming excessive LLM tokens.

## 3. LLM Reasoning & AI
*   **LLM Hallucination on Quotes**: The Groq LLM slightly modifies a user quote (e.g., fixing grammar), which causes the strict substring validation to fail.
    *   *Handling*: The validation script drops the invalid quote. The theme is still reported, but without that specific quote. We will rely heavily on strict prompt engineering ("DO NOT MODIFY A SINGLE CHARACTER") to minimize this.
*   **Free Tier Rate Limits (RPM, RPD, TPM, TPD)**: Groq's free tier has strict limits on Requests Per Minute/Day and Tokens Per Minute/Day.
    *   *Handling (Top Priority)*: 
        1. **Token Tracking**: We will use a tokenizer/character count before making API calls to ensure we *never* send a payload exceeding the TPM limit. If the payload is too large, we will chunk the centroid reviews and process them in smaller batches.
        2. **Request Queueing (RPM)**: We will implement explicit `time.sleep()` delays between chunked requests to stay safely under the Requests Per Minute limit.
        3. **Daily Quotas (RPD/TPD)**: We will catch quota-exceeded errors. If the daily limit is hit, the UI will gracefully inform the user that the free quota has reset, preventing unhandled crashes.
        4. **Exponential Backoff**: If an HTTP 429 (Too Many Requests) is hit despite tracking, the system will use an exponential backoff retry loop. The UI loading state will safely persist while the backend retries.
*   **Uncategorizable Themes**: The LLM struggles to map a theme to one of the strict Team Categories (Product, Engineer, Art, CEO).
    *   *Handling*: The prompt will include an "Uncategorized" or "General" fallback team, so the parser doesn't crash if it encounters an unexpected team name.

## 4. Frontend (Vercel) & Backend (Render) Constraints
*   **Request Timeout (Vercel/Render limits)**: The embedding, clustering, and LLM processing might take longer than the standard 10-15 second serverless timeout on Vercel or Render.
    *   *Handling*: The UI will display a clear "Processing... This may take up to 2 minutes" message. We must ensure the FastAPI endpoint on Render is not subject to a short timeout, and Vercel's fetch request does not abort prematurely.
*   **Cold Starts**: The Render free tier spins down after 15 minutes of inactivity. The first request might take 30-50 seconds just to wake the server up.
    *   *Handling*: The Vite frontend can ping a lightweight `/health` endpoint upon loading the page to wake the backend up in the background before the user even hits submit.

## 5. Output Delivery (MCP)
*   **MCP Server Unreachable / Fails**: The user hits the manual "Push to CEO Team" button, but the MCP client stub fails to connect to the Google Workspace MCP.
    *   *Handling*: Catch the network error on the backend and return a failure state. The UI will show a toast notification: *"Failed to push. Ensure the MCP server is running and accessible."* The report remains on the screen so no data is lost.
