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

## 3. Presentation & Slide Design Standards

Whenever generating slide decks (e.g., Executive Insight Decks) via the API, you must adhere to Principal PM design standards:

1. **Never use blank defaults**: Do not generate slides with default white backgrounds and black text bullet points.
2. **Template Duplication**: Always require a `templatePresentationId` (a beautifully designed master template in Google Drive) and use the Drive API to duplicate it and fill its placeholders.
3. **Brand Coloring**: Keep the slide design color closely related to the product on which the analysis is being done. Try to follow the same color scheme as the original company.
4. **Visual Hierarchy**: Replace bullet points with visual structures (e.g., 3-column grids, side-by-side comparisons, bold callouts) embedded in the template layout.
5. **Action Titles**: Slide titles must be full-sentence takeaways (e.g., "High cart abandonment is driven by lack of trust, costing $2M annually" instead of "Cart Abandonment Analysis").
6. **Premium Aesthetics**: Enforce professional, high-contrast color palettes (e.g., Deep Navy, vibrant Teal/Orange accents, or Brand colors) to create a premium "McKinsey/BCG" style.

---

## 4. 10-Slide Board-Level Executive Presentation Schema

Whenever generating the board presentation output JSON, it must follow the Chief Product Officer / McKinsey narrative synthesis rules:

### A. Narrative Flow & Structure
The presentation must consist of exactly 10 slides representing a complete narrative:
1. **Slide 1: Executive Summary** (`title`, `headline`, `problem`, `why_now`, `recommendation`, `business_impact`, `speaker_notes`)
2. **Slide 2: Customer Problem** (`title`, `top_3_user_pains`, `customer_quotes`, `behavior_patterns`, `jobs_to_be_done`, `key_takeaway`, `speaker_notes`)
3. **Slide 3: Root Cause Analysis** (`title`, `root_causes`, `validated_assumptions`, `false_assumptions`, `issue_tree_summary`, `key_takeaway`, `speaker_notes`)
4. **Slide 4: Market & Competitive Landscape** (`title`, `competitor_summary`, `market_gap`, `white_space`, `opportunities`, `strategic_advantage`, `speaker_notes`)
5. **Slide 5: AI Opportunity** (`title`, `current_process`, `ai_can_improve`, `automation`, `personalization`, `predictions`, `expected_business_value`, `speaker_notes`)
6. **Slide 6: Solution Options** (`title`, `conservative`, `innovative`, `moonshot`, `recommended`, `reason`, `speaker_notes`)
7. **Slide 7: Expected Business Impact** (`title`, `north_star_metric`, `primary_metrics`, `guardrail_metrics`, `counter_metrics`, `expected_results`, `risks`, `speaker_notes`)
8. **Slide 8: Implementation Roadmap** (`title`, `phase_1`, `phase_2`, `phase_3`, `dependencies`, `timeline`, `speaker_notes`)
9. **Slide 9: Competitive Moat** (`title`, `switching_costs`, `data_advantage`, `network_effect`, `flywheel`, `long_term_strategy`, `speaker_notes`)
10. **Slide 10: Executive Recommendation** (`title`, `decision`, `top_priorities`, `investment_required`, `expected_roi`, `next_steps`, `closing_message`, `speaker_notes`)

### B. Board-Level Slide Rules
- **Formatting**: Max 5 bullet points per slide, max 12 words per bullet. No paragraphs.
- **Content density**: Use precise metrics, numbers, and facts. Avoid generic observations or buzzwords.
- **Executive Elements**: Every slide must list tradeoffs, risks, and assumptions, and must answer: *"So what?"*
- **Design Metadata**: The output JSON must also supply `presentation_theme`, `primary_color`, `secondary_color`, `recommended_icons`, `recommended_charts`, and `visual_priority` for each slide.

