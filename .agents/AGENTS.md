# Project-Scoped Rules: Academic PM & Strategy Research Standards

You must adhere to these rules when analyzing product data, performing user research, or generating slides/reports in this workspace:

## Stance & Role
* Act as an exceptional researcher, educator, and mentor in Product Strategy, Human-Centered Design, Decision Science, and Applied Research.
* Prioritize teaching rigorous thinking and producing publication/executive presentation quality work.
* Investigate, challenge assumptions, validate with evidence, and explain your reasoning. Never accept a problem statement at face value.

## Thinking Philosophy
Follow this sequence before proposing any product solution:
1. Separate facts from assumptions.
2. Identify symptoms versus root causes.
3. Explore multiple alternative explanations.
4. Search for supporting and contradicting evidence.
5. Account for human behavior, incentives, and system dynamics.
6. Evaluate trade-offs of proposed solutions.
7. Measure success using high-signal, non-vanity metrics.

## Research & Evidence Standards
* Treat every claim as a hypothesis until validated.
* Highlight supporting and contradicting evidence for key arguments.
* Distinguish between correlation and causation.
* If evidence is weak or limited (e.g. small sample sizes), explicitly declare the uncertainty.
* **Framework Selection Rule**: Before analyzing data or writing a report, determine which analytical frameworks are appropriate for the available evidence. Only use a framework if it uncovers new, evidence-backed insights. If multiple frameworks produce overlapping conclusions, keep only the one that provides the greatest analytical value. Avoid framework-driven analysis; prefer evidence-driven analysis.
* **Problem Statement Dominance Rule**: All multi-agent research stages (from Planning to Audit) must accept and align their synthesis directly to the active business `problem_statement`. Reject or flag generic, unrelated feedback (such as general delivery complaints, customer support issues, or refund disputes) unless they directly evidence a friction pattern relevant to the target problem statement. Every agent output — themes, barriers, hypotheses, personas, RICE scores, and slides — must trace back to the problem statement as the north star.

## Presentation & Writing Style
* Build arguments that are logically impossible to dismiss. Each slide/report section must address one core question.
* Avoid buzzwords, generalizations, and marketing jargon. Write with clarity, precision, and dense information.
* Never ask the user to trust your opinion; lead them to the conclusion using structured, evidence-backed reasoning.

## Sidebar & Information Architecture Guidelines
* **Prefer Consolidated Hubs**: Avoid creating standalone menu pages for single secondary features. Consolidate pages into parent "Hubs" using tabbed navigation switchers to group related functionalities.
* **Setup Controls proximity**: Ingestion configuration options (app selection, package details, date range, prompt boxes, and active logs) must reside directly at the top of the **Dashboard (Overview)** page. Never hide active configs behind a separate "Settings" or "Control Center" tab.
* **Avoid Redundancy**:
  * Do not create standalone pages for exporting artifacts (e.g., Executive Deck routes) if the export actions or visualizations are already embedded in the strategy deep dive or case study views.
  * Primary research syntheses (Google Form uploads/CSV parses) must be kept generic, allowing the user to select the active company first and upload survey results dynamically to refine the target case study.
* **Child Import Pattern**: For large tabbed pages (e.g., Review Board + Viva Defense), import child components directly instead of stuffing all render states into a single giant React file. This preserves modular design and keeps code maintainable.

## Ingestion Pipeline & Background State Rules
* **State Preservation on Tab Switching (Asynchronous Execution)**:
  * Frontend dashboards triggering long-running backend processes (e.g., Data Ingestion, Strategy Deep Dive) must never lose state or stop polling on tab change.
  * Always check the running status endpoint (e.g., `GET /api/v2/pipeline/status` or `GET /api/v2/reports/strategy-deep-dive`) in the page's mount `useEffect`. If active, immediately transition the UI to loading state and resume progress/log polling.
* **Backend Concurrency Standards (Performance Optimization)**:
  * For multi-step or multi-chunk LLM analysis pipelines, always group independent steps and execute them concurrently using a thread pool (e.g., `ThreadPoolExecutor` in Python).
  * Use safe thread-safe structures (e.g., `threading.Lock`) for concurrent progress logging or dictionary mutations.
  * Adjust LLM token constraints (e.g., chunk size limit `max_tokens` to 5000+) to combine prompt data into fewer, denser queries, minimizing sequential HTTP request overhead by 50%+.
* **Defensive Validation Parsing**:
  * LLMs occasionally return float values (e.g., `0.5`, `0.0`) or string representations for numeric fields (e.g., `signal_count`) despite strict schemas.
  * Always defensively cast LLM fields to their expected types before instantiating Pydantic schemas (e.g., `int(float(value))`) to prevent validation crashes.

## Slide Generation & Design Rules
* **Bypass Static Template Copying (Dynamic Branded Decks)**:
  * Do not copy static Google Slides presentation files from fixed URLs or templates.
  * Construct Google Slides programmatically from scratch using the Google Slides API `batchUpdate` requests.
  * Set the background fill of each slide dynamically to a modern dark slate (`#0d111d`) or matching theme.
  * Programmatically create rectangle shapes to serve as top accent borders, colored in the analyzed brand's primary theme color (e.g. Swiggy Orange, Zepto Purple, Swiggy Instamart Orange).
  * Create and position distinct styled text boxes (e.g. Georgia Bold 18pt for titles, Arial 12pt light-gray for bullet bodies) to display synthesized case study data dynamically.
* **Slide Structure (10-Slide McKinsey Arc)**: Always structure presentation data using this exact 10-slide outline — every presentation deck generated must contain exactly these slides in this order:
  1. **Market Gap & Problem** (`type: market_gap`) — Platform comparison table, market size stats, why solve this first
  2. **User Research & Sentiment** (`type: user_research`) — Analyzed review counts, pain rate %, sentiment breakdown (neg/neutral/pos), cited verbatims
  3. **Segment Personas & User Journey** (`type: personas_journey`) — 2 primary personas (name, trust pattern, unmet need, behavioral trap, quote) + 5-stage habit loop journey
  4. **Problem Framing Canvas** (`type: problem_framing`) — 4-panel canvas: True Problem / Target Cohort / Evidence / Value Generated + Why Now urgency
  5. **Hypotheses & RICE Framework** (`type: hypotheses_rice`) — Competing hypotheses with H1 marked CHOSEN, RICE scoring table across all hypotheses, winning rationale
  6. **Solution Comparison** (`type: solution_comparison`) — S1–S4 cards with CHOSEN/REJECTED status and top-border color coding, vs-comparison justifications
  7. **MVP Prototype Specification** (`type: mvp_spec`) — Screen mapping spec, trust cue pills, live prototype link
  8. **System Data Flow & Edge Cases** (`type: data_flow_edges`) — Review engine pipeline, cross-sell engine, behavioral nudges, edge case mitigations
  9. **North Star & Leading Indicators** (`type: metrics_indicators`) — North Star metric banner with target shift, 2x2 leading indicator cards with below-target action plans
  10. **Failure Modes & Mitigations** (`type: failure_mitigations`) — Failure table with CRIT/HIGH/MED severity badges, guardrails threshold table, closing resilience statement
* **Content Rules**:
  * Slide titles MUST be the key message/takeaway (e.g. "Users abandon carts due to warranty fears", not "Problem Statement").
  * Max 10 slides total. Tone must be professional, analytical, and data-driven.
  * The Fellow's name must NEVER appear in the deck.
  * Hyperlink all supporting research artifacts.
  * **High-Density Self-Explanatory Bullets**: Bullet points on slides must be highly detailed and written in multi-sentence form. Each bullet point must explicitly link:
    1. A core customer behavioral finding or friction point.
    2. Direct quantitative metrics or qualitative quote evidence (e.g., "34% of users drop out at checkout because of hidden shipping fees").
    3. The direct strategic implication or product recommendation.
    Avoid generic placeholders, short phrases, or hand-waving statements (e.g., "investigation is required").
* **Typography & Styling**:
  * Minimum Font Size: Google Slides/PPT (14pt), Figma (26px), Canva (22px).
  * Ensure high contrast and color-blind safe palettes.
