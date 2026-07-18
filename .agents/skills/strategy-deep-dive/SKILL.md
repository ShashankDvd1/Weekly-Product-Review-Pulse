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
