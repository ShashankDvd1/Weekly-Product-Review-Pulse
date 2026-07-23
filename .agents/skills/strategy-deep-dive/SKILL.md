---
name: strategy-deep-dive
description: Guide on the 16-step Principal PM / Strategy Consultant analysis framework, its prompts, and its API in this workspace.
---

# IDE Skill: Strategy Deep Dive Analysis

This skill instructs agents on how the 16-step strategy deep dive framework is structured, configured, and run.

## 1. Core Architecture

The analysis is coordinated by a Python engine located in:
* **[strategy_deep_dive.py](file:///e:/PM_Portfolio_Projects/Weekly-Product-Review-Pulse/backend/reasoning/strategy_deep_dive.py)**

It contains 16 individual LLM step prompts:
1. **Problem Restatement**: Restates problem from User, Business, Tech, and Market perspectives.
2. **Challenge Assumptions**: Validates/contradicts hidden assumptions.
3. **5 Whys Analysis**: Traces problem to its root cause.
4. **Issue Tree**: Decomposes problem into categories (User, Business, Psychology, Operations, etc.).
5. **Behavioral Analysis**: Evaluates emotional blocks (Fear, Loss Aversion, Habit, Cognitive Load).
6. **Jobs To Be Done**: Defines Functional, Emotional, Social, Hidden, and Future jobs.
7. **User Journey**: Maps pain/emotion across Before, During, and After phases.
8. **Root Cause Matrix**: Maps problem, evidence, root cause, impact, and intervention.
9. **Competitive Research**: Analyzes successes, failures, and gaps of direct/indirect competitors.
10. **White Space**: Spots optimize vs non-optimized gaps and shared assumptions.
11. **Second-Order Thinking**: Projects 1-month and 1-year effects, risks, and gaming potential.
12. **Metrics Framework**: Defines North Star, inputs, outputs, guardrails, and counter metrics.
13. **AI Opportunity**: Identifies decisions, personalization, and predictions AI can optimize.
14. **Solutions**: Generates Conservative, Innovative, Moonshot, and AI-First solutions.
15. **Competitive Moat**: Ranks switching costs, data advantages, and network effects.
16. **Executive Presentation**: Drafts 5-minute executive slide takeaway bullet points.

---

## 2. API Endpoint

* **Endpoint**: `GET /api/v2/reports/strategy-deep-dive`
* **Triggering**: Runs all 16 steps sequentially using the collected data, caching results in `orchestrator.strategy_deep_dive`.
* **Rate Limits**: Takes ~5-8 minutes to complete in full due to API rate-limit delays between steps.

---

## 3. Executive Presentation Generation Standards (v2.0)

Whenever generating slide decks (e.g., Executive Insight Decks) via the API, you must adhere to Principal PM / McKinsey design standards:

### A. Storytelling & Narrative Flow
Build a clear executive narrative where every slide naturally answers the previous slide:
**Problem → Evidence → Root Cause → Market Validation → Opportunity → Solution → Why This Solution → Business Impact → Execution Plan → Risks → Executive Decision**
The audience should never need to ask: Why? How do we know? Why now? Why this solution? What's the impact?

### B. Slide Contract (Mandatory)
Every slide MUST contain:
1. **Executive Question:** What business question is this slide answering?
2. **Executive Answer:** One clear takeaway in a single sentence. Headlines must be **conclusions**, not topics (e.g., "Trust Deficit is Limiting Cross-Category Growth").
3. **Supporting Evidence:** Support every claim (e.g., analytics, quotes, benchmarks).
4. **Business Impact:** Revenue, margin, retention impact, or cost of inaction. Translate all percentages into business outcomes (e.g., "+18% AOV = $X incremental annual revenue").
5. **Executive Recommendation:** Clearly state the required decision.
6. **Transition:** End every slide by leading into the next.

### C. Content & Design Constraints
1. **Word Limits:** Max 40-60 words per slide. Max 4 concise bullets. Max 12 words per bullet.
2. **Visual Hierarchy:** Recommend visual structures instead of text: KPI Cards, Opportunity Matrix, 2x2 Matrix, Fishbone Diagram, Revenue Waterfall, etc. Set a 60% whitespace / 20% visuals / 20% text ratio.
3. **Brand Coloring:** Output slide schemas mapped to product brand colors (e.g. Zepto Purple, Blinkit Yellow) to be instantly importable into Adobe Express or Gamma.
4. **Professional Lexicon:** Remove all AI-generated filler words. Use executive business language only.

---

## 4. 10-Slide Board-Level Executive Presentation Schema

Whenever generating the board presentation output JSON, it must follow this structural flow:

1. **Slide 1: Executive Summary** (`headline`, `executive_answer`, `problem`, `why_now`, `recommendation`, `business_impact_metrics`, `speaker_notes`, `suggested_visual`)
2. **Slide 2: Customer Problem** (`headline`, `executive_answer`, `top_user_pains`, `evidence_quotes`, `jobs_to_be_done`, `speaker_notes`, `suggested_visual`)
3. **Slide 3: Root Cause Analysis** (`headline`, `executive_answer`, `root_causes`, `false_assumptions`, `speaker_notes`, `suggested_visual: Fishbone/5-Whys`)
4. **Slide 4: Market Validation** (`headline`, `executive_answer`, `competitor_matrix`, `white_space_gap`, `speaker_notes`, `suggested_visual: 2x2 Matrix`)
5. **Slide 5: Strategic Opportunity** (`headline`, `executive_answer`, `opportunity_size`, `strategic_advantage`, `speaker_notes`, `suggested_visual`)
6. **Slide 6: Proposed Solution** (`headline`, `executive_answer`, `alternatives_rejected`, `solution_details`, `confidence_level`, `speaker_notes`, `suggested_visual: Wireframe/Mockup`)
7. **Slide 7: Business Impact** (`headline`, `executive_answer`, `north_star_metric`, `revenue_impact`, `margin_impact`, `speaker_notes`, `suggested_visual: KPI Cards`)
8. **Slide 8: Execution Roadmap** (`headline`, `executive_answer`, `phases`, `dependencies`, `speaker_notes`, `suggested_visual: Timeline`)
9. **Slide 9: Risks & Mitigations** (`headline`, `executive_answer`, `primary_risks`, `mitigations`, `speaker_notes`, `suggested_visual: Risk Matrix`)
10. **Slide 10: Executive Decision** (`headline`, `executive_answer`, `investment_ask`, `expected_roi`, `next_steps`, `speaker_notes`, `suggested_visual`)

