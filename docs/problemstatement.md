# Weekly Product Review Pulse — Problem Statement

## Problem Statement
We are building an automated weekly “pulse” that turns public App Store and Google Play reviews for any given app into a one-page insight report. It features a User Interface where users can input any package name or App Store ID. The report is delivered to stakeholders through Google Workspace, using MCP (Model Context Protocol) so that writes to Google Docs and Gmail go through dedicated MCP servers—not ad hoc API calls inside the agent.

Supported products: Any app (dynamic input via UI for App Store and Google Play Store package names).

## Objective
Give product, support, and leadership teams a repeatable, weekly snapshot of what customers are saying in store reviews: themes, representative quotes, and actionable ideas—without manual copy-paste or one-off spreadsheets.

## What the system does
*   **Ingest public reviews** using a custom date range (From Date to To Date, selectable via the UI) from both Apple App Store (e.g. iTunes customer-reviews RSS) and Google Play (scraper-based), per app.
*   **Filter & Clean Data**: The UI allows users to configure a minimum word count (0 to 100 words) to ensure meaningful feedback is processed, and provides an option to either include or exclude reviews containing emojis.
*   **Cluster and rank feedback** using free embeddings (e.g. BGE) and density-based clustering (UMAP + HDBSCAN).
*   **Prevent Hallucination & Minimize Tokens**: Instead of sending all reviews to the LLM, we identify the top representative reviews for each cluster (centroid proximity). We pass only these to a free LLM (e.g. Groq) to name themes, pull verbatim quotes, and propose action ideas. Strict substring-matching validation ensures that the returned quotes exist exactly in the original reviews.
*   **Render a concise one-page narrative**: The UI displays the full generated report, listing all themes, real quotes, and action ideas. Each theme is tagged with a relevant **Team Category** (e.g., Product Team, Engineer Team, Art Team, CEO Team).
*   **Deliver outputs through Google Workspace MCP servers (via UI Approval)**:
    *   **Manual Dispatch**: A final "Push" button is available in the UI so the report can be reviewed before the MCP sends the email.
    *   **Team-Specific Sends**: The UI provides separate buttons for each Team Category. This allows users to send targeted emails containing only the themes and docs relevant to that specific team (e.g., sending only bug-related themes to the Engineer Team).
    *   **Google Docs MCP** — append each week’s report as a new dated section to a single running document per app. The Doc is the system of record and preserves history.
    *   **Gmail MCP** — send stakeholder emails that include a deep link to the new section in the Doc.

### Internal Code Modularity
| Concern | Where it lives |
| :--- | :--- |
| **Data retrieval** | Ingestion modules (App Store + Play Store) |
| **Reasoning** | Clustering + LLM summarization (themes, quotes, actions) |
| **Output generation** | Report + email rendering (structured for Docs and HTML/text for Gmail) |
| **Human-visible delivery** | MCP tools only → Google Docs MCP + Gmail MCP |

The agent is an MCP host/client; it does not embed Google credentials or call the Docs/Gmail REST APIs directly for delivery.

## Key Requirements
*   **MCP-based delivery**: Append to the shared Google Doc and send Gmail only via the respective MCP servers’ tools (e.g. document batch update, draft/create/send flows as defined in architecture).
*   **Weekly cadence**: Designed to run once per product per week (e.g. scheduled job Monday morning IST), with a CLI for backfill of any ISO week.
*   **Idempotent runs**: Re-running the same product + ISO week must not create duplicate Doc sections or duplicate sends. This is enforced with a stable section anchor in the Doc and a run-scoped idempotency check on email (see architecture).
*   **Auditable**: Each run records delivery identifiers (e.g. doc heading / message ids) and enough metadata to answer “what was sent when, for which week?”
*   **Safety and quality**: PII scrubbing on review text before LLM and before publishing; reviews treated as data, not instructions; cost/token limits per run.

## Non-goals (explicit)
*   A generic Google Workspace product beyond what the pulse needs (Docs append + Gmail send/draft).
*   Real-time streaming analytics or a BI dashboard (the running Google Doc is the living artifact).
*   Social sources (Twitter, Reddit, etc.) in the initial scope.
*   Storing Google OAuth secrets in the agent codebase—they belong in the MCP servers’ configuration, per architecture.

## Who this helps
| Audience | Value |
| :--- | :--- |
| **Product** | Prioritize roadmap from recurring themes |
| **Support** | Spot repeating complaints and quality issues |
| **Leadership** | Fast health snapshot tied to customer voice |

## Sample output (illustrative)
**[App Name] — Weekly Review Pulse**
**Period**: [Selected From Date] to [Selected To Date]

**Top themes**
*   **App performance & bugs** — Lag, crashes during trading hours; login/session timeouts.
*   **Customer support friction** — Slow responses; unresolved tickets.
*   **UX & feature gaps** — Confusing navigation for portfolio insights; missing advanced analytics.

**Real user quotes**
*   “The app freezes exactly when the market opens, very frustrating.”
*   “Support takes days to reply and doesn’t solve the issue.”
*   “Good for beginners but lacks detailed analysis tools.”

**Action ideas**
*   **Stabilize peak-time performance** — Scale infra during market hours; improve crash visibility.
*   **Improve support SLA visibility** — Expected response time in-app; ticket status tracking.
*   **Enhance power-user features** — Advanced portfolio analytics; clearer investments navigation.

**What this solves**
Same intent as today: roadmap alignment for product, issue clustering for support, and a leadership-friendly snapshot—now automated, archived in Google Docs, and announced by email with a link back to the canonical section.

## Delivery expectations (stakeholder-facing)
*   Each run adds one clearly labeled section to the product’s pulse Google Doc (dated / week-labeled).
*   The email is a brief teaser (e.g. top themes as bullets) plus a “Read full report” link to that section.
*   Development/staging may default to draft-only email until explicit confirmation to send, per implementation plan.
