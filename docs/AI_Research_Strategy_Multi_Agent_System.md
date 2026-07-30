
# AI Research & Strategy Multi-Agent System v2

## Vision
Build an evidence-first, consulting-grade research system that adapts to any dataset. The system must never force PM frameworks or predefined strategies. Every insight, recommendation, and presentation slide must be traceable to the original data.

---

# Governing Principles

- Dataset is the only source of truth.
- Never hallucinate or fill gaps.
- Clearly distinguish Facts, Hypotheses, and Recommendations.
- State **"Insufficient evidence"** when data cannot support a claim.
- Every recommendation must trace back to evidence.
- Frameworks are optional—not mandatory.
- Presentation output is **exactly 10 slides**.
- No roadmap, appendix, or filler content.

---

# Agent Pipeline

## 1. Research Planning Agent
Purpose:
- Identify dataset type(s)
- Assess data quality and bias
- Decide which analyses/frameworks are appropriate
- Skip analyses unsupported by the data

Output:
- Research plan
- Selected frameworks (if any)
- Confidence assessment

---

## 2. Data Processing Agent
Responsibilities:
- Clean and normalize data
- Remove duplicates
- Extract metadata
- Prepare structured dataset
- Report missing values

Output:
- Structured dataset
- Data quality report
- Initial statistics

---

## 3. Research Discovery Agent
Responsibilities:
- Discover patterns
- Detect anomalies
- Extract quotes
- Identify contradictions
- Generate evidence-backed hypotheses

Rules:
- No solutions
- No predefined PM templates

---

## 4. Pattern & Segmentation Agent
Responsibilities:
- Cluster users naturally
- Prioritize themes
- Estimate confidence
- Build evidence clusters

---

## 5. Root Cause & Strategy Agent
Responsibilities:
- Validate hypotheses
- Rank root causes
- Explain alternative explanations
- Estimate customer/business impact

Rules:
- Never infer causation without evidence.

---

## 6. Solution Generation Agent
Every solution must include:
- Problem addressed
- Supporting evidence
- Confidence
- Expected KPI impact
- Risks
- Trade-offs
- Dependencies
- RICE

---

## 7. Executive Presentation Agent

Generate exactly 10 slides.

1. Executive Summary
2. Problem Landscape
3. Evidence & Insights
4. Behavioral Analysis (only if supported)
5. Root Cause Prioritization
6. Competitive / White Space (only if justified)
7. Metrics Framework (only if measurable)
8. Prioritized Solutions
9. Strategic Recommendation
10. Executive Conclusion

Rules:
- One key insight per slide
- Prefer visuals over text
- Merge low-priority insights
- Never exceed 10 slides

---

## 8. Evidence Traceability Agent

Create traceability:

Recommendation
↓
Root Cause
↓
Pattern
↓
Evidence Cluster
↓
Raw Dataset

Flag anything untraceable.

---

## 9. Research Audit Agent

Independently verify:

- Evidence validity
- Unsupported claims
- Contradictions
- Correlation vs causation
- Logical consistency
- Duplication
- Confidence levels
- Slide quality

Labels:
- Verified
- Partially Verified
- Weak Evidence
- Unsupported
- Contradicted

Verdict:
- PASS
- PASS WITH WARNINGS
- REQUIRES REVISION
- FAIL

---

# Framework Selection Rule

Never automatically generate:
- Personas
- JTBD
- Journey Maps
- 5 Whys
- SWOT
- Issue Trees
- Metrics
- Competitor Analysis
- Behavioral Models

Only use a framework if it reveals new evidence-backed insights.

---

# Orchestrator Prompt

The orchestrator coordinates all agents.

Execution Rules:
1. Run agents sequentially.
2. Each agent consumes the previous agent's output.
3. Validate output before continuing.
4. Stop and request revision if validation fails.
5. Do not present final results until the Research Audit Agent returns PASS or PASS WITH WARNINGS.

UI should display:
- Current step
- Status
- Processing time
- Confidence
- Inputs
- Outputs
- Expandable evidence

---

# Research Standards

Every insight should include:
- Evidence
- Supporting data
- Representative quotes
- Contradicting evidence
- Confidence
- Business impact
- Customer impact

---

# Final Deliverables

- Consulting-grade research report
- Evidence traceability map
- Audit report
- Exactly 10-slide executive presentation

The final output must be:
- Evidence-backed
- Traceable
- Quantified where possible
- Free from assumptions
- Free from generic PM templates
- Defensible from the original dataset
