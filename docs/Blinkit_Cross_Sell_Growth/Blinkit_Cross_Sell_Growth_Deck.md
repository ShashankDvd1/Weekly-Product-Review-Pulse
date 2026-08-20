---
marp: true
theme: uncover
paginate: true
size: 16:9
style: |
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

  :root {
    --bg-primary: #0d111d;
    --bg-card: #161b2e;
    --accent-orange: #f7971e;
    --accent-green: #27ae60;
    --accent-red: #e74c3c;
    --accent-blue: #3498db;
    --text-primary: #f0f0f5;
    --text-secondary: #a0a4b8;
    --text-muted: #6b7094;
    --border-subtle: #252b40;
  }

  section {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 22px;
    line-height: 1.55;
    padding: 50px 60px 40px 60px;
    border-top: 4px solid var(--accent-orange);
  }

  h1 {
    font-size: 30px;
    font-weight: 800;
    color: var(--accent-orange);
    margin-bottom: 6px;
    letter-spacing: -0.3px;
  }

  h2 {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    margin-top: 18px;
    margin-bottom: 6px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 4px;
  }

  h3 {
    font-size: 19px;
    font-weight: 600;
    color: var(--accent-blue);
    margin-top: 10px;
    margin-bottom: 4px;
  }

  p, li {
    color: var(--text-secondary);
    font-size: 18px;
  }

  strong {
    color: var(--text-primary);
    font-weight: 700;
  }

  em {
    color: var(--text-muted);
    font-style: italic;
  }

  ul, ol {
    margin-top: 4px;
    margin-bottom: 4px;
    padding-left: 22px;
  }

  li {
    margin-bottom: 3px;
  }

  blockquote {
    border-left: 3px solid var(--accent-orange);
    background: var(--bg-card);
    padding: 10px 16px;
    margin: 8px 0;
    font-size: 16px;
    border-radius: 4px;
  }

  blockquote p {
    color: var(--text-secondary);
    font-style: italic;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 16px;
    margin-top: 8px;
  }

  th {
    background: var(--bg-card);
    color: var(--accent-orange);
    font-weight: 700;
    text-align: left;
    padding: 8px 12px;
    border-bottom: 2px solid var(--accent-orange);
  }

  td {
    padding: 7px 12px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-secondary);
  }

  tr:nth-child(even) td {
    background: rgba(22, 27, 46, 0.5);
  }

  /* Severity badges */
  td strong {
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 13px;
  }

  /* Slide number styling */
  section::after {
    color: var(--text-muted);
    font-size: 13px;
  }

  /* Subtitle line under h1 */
  section > p:first-of-type {
    color: var(--text-secondary);
    font-size: 17px;
    margin-top: 0;
    margin-bottom: 14px;
  }
---

<!-- _class: lead -->

# Slide 1 — Market Gap & Problem

Users often purchase the same set of products repeatedly and rarely explore new categories available on the platform.

- Users appreciate quick delivery and convenience
- Users are willing to pay for premium services and products
- Users rarely explore new categories available on the platform

## Current Platform Metrics

- **1 million** — Monthly Active Customers
- **$50** — Average Order Value
- **20%** — Customer Retention Rate

## Competitor Analysis

| Platform | What they offer | What's missing |
| :--- | :--- | :--- |
| Blinkit | Quick delivery and convenience | Limited product offerings and categories |
| Zepto | Quick delivery and convenience | Limited product offerings and categories |
| Swiggy Instamart | Quick delivery and convenience | Limited product offerings and categories |
| BigBasket | Wide product offerings and categories | Slow delivery and limited convenience |
| Amazon Fresh | Wide product offerings and categories | Slow delivery and limited convenience |

## Why Solve This First

- **Reason 1:** Users are willing to pay for premium services and products
- **Reason 2:** Users appreciate quick delivery and convenience
- **Reason 3:** Users rarely explore new categories available on the platform

---

# Slide 2 — User Research & Sentiment

Users appreciate quick delivery and convenience, but struggle to discover new products and categories.
Total feedback analyzed/labeled: **150 / 150**.

## Discovery Pain Rate

- **40%** — Variety
- **30%** — Less Repetition
- **20%** — Real navigation
- **10%** — Better suggestions

## Sentiment Analysis

- **60** Negative
- **30** Neutral
- **60** Positive

## Cited User Verbatims

> "A very good alternative when you are unable to reach local marketplace or you have to purchase something urgently and you have less time." *(play_store)*

> "good, This service useful in emergency situations." *(play_store)*

---

# Slide 3 — Segment Personas & User Journey

Understanding the needs and pain points of our users.

## User Personas

### 1. Busy Professional

- **"Archetype":** Age 25-45, City: Urban, Frequency: Daily
- **Trust pattern:** High
- **Unmet need:** Convenience and premium services
- **Behavioral trap:** Limited product offerings and categories
- **Quote:** *"I need to be able to order quickly and easily, without having to spend too much time searching for products."*

### 2. Stay-at-Home Parent

- **"Archetype":** Age 25-45, City: Suburban, Frequency: Weekly
- **Trust pattern:** Medium
- **Unmet need:** Convenience and premium services
- **Behavioral trap:** Limited product offerings and categories
- **Quote:** *"I need to be able to order quickly and easily, without having to spend too much time searching for products."*

## User Journey Habit Loop

1. **Open:** Browse products and categories. *(Friction: Limited product offerings and categories)*
2. **Served:** Order products and categories. *(Friction: Limited product offerings and categories)*
3. **Browse:** Explore new products and categories. *(Friction: Limited product offerings and categories)*
4. **Checkout:** Complete order. *(Friction: Limited product offerings and categories)*
5. **Exit:** Leave the platform. *(Friction: Limited product offerings and categories)*

---

# Slide 4 — Problem Framing Canvas

Understanding the root cause of the problem.

1. **What is the True Problem?**
   Limited product offerings and categories
2. **Who faces this problem?**
   Busy Professionals and Stay-at-Home Parents
3. **How do we know it's a problem?**
   - Users rarely explore new categories available on the platform
   - Users are willing to pay for premium services and products
4. **Value Generated by Solving This**
   - *For Users:* Convenience and premium services
   - *For Platform:* Increased customer retention and revenue
5. **Why Should We Solve This Now?**
   Saturation: High | AI Unlock: High | First-mover window: High

---

# Slide 5 — Hypotheses & RICE Framework

Evaluating the potential impact of different solutions.

- **H1: Personalized Recommendations and Offers (CHOSEN)**
  Users are more likely to explore new categories if the app provides personalized recommendations and offers.
- **H2: Improved Customer Experience**
  Users are more likely to report issues with damaged products and poor customer service if they are not satisfied with the app's overall experience.

## RICE Framework Scoring

| ID | Reach | Impact | Confidence | Effort | Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H1** | 9/10 | 9/10 | 80/100 | 4/10 | **162** |
| **H2** | 5/10 | 6/10 | 60/100 | 5/10 | **36** |

**Winning Rationale:** The personalized recommendations and offers hypothesis has the highest RICE score, indicating that it has the highest potential impact and should be prioritized.

---

# Slide 6 — Solution Comparison

Key Insight: Multiple Solutions Can Address the Problem.

- **S1: Full Homepage Redesign (REJECTED)**
  Redesign the homepage to showcase a wide range of products and categories.
  *Concern:* "Users may not engage with the new design."
- **S2: Push Notification Campaign (REJECTED)**
  Send push notifications to users with personalized product recommendations.
  *Concern:* "Users may not respond to push notifications."
- **S3: Category Badges without Authenticity Seals (REJECTED)**
  Display category badges on product pages without authenticity seals.
  *Concern:* "Users may not trust the badges."
- **S4: Contextual In-Cart Cross-Sell Hub with Brand Badging (CHOSEN)**
  Display a cross-sell hub in the cart with brand badges and contextual recommendations.
  *Rationale:* "Users may engage with the hub and increase sales."

## Why the Selected Solution Wins Against Each Alternative

- **vs S1:** Full homepage redesign may not address the root cause of limited product offerings and categories.
- **vs S2:** Push notification campaign may not be effective in increasing engagement and sales.
- **vs S3:** Category badges without authenticity seals may not be trusted by users.

---

# Slide 7 — MVP Prototype Specifications

Key Insight: MVP Should Focus on Core Features and User Experience.

## Core Features

- **Feature 1:** Contextual In-Cart Cross-Sell Hub
- **Feature 2:** Brand Badging and Authenticity Seals
- **Feature 3:** Personalized Product Recommendations

## Dynamic Trust Cues Configured

- Clear and concise product descriptions
- High-quality product images
- Secure payment processing

## MVP Screen Mapping Spec

1. **Login Screen:** User enters username and password to log in.
2. **Product Page:** User views product details and recommendations.
3. **Cart Screen:** User views cart contents and makes a purchase.

---

# Slide 8 — System Data Flow & Edge Cases

Key Insight: Data Flow Should Be Efficient and Secure.

## Data Flow Pipeline

1. **Review Insights Pipeline:** Reviews and ratings from users
2. **Contextual Cross-Sell Engine:** Product information and metadata

## Behavioral Nudges Built In

- **Nudge 1:** Display recommended products on product pages
- **Nudge 2:** Send personalized product recommendations via email
- **Nudge 3:** Display contextual recommendations in the cart

## Edge Cases & Mitigations Handled

- **E1: User Input Error** → Validate user input and display error messages.
- **E2: Product Engine Failure** → Implement failover mechanisms and display alternative recommendations.
- **E3: Recommendation Engine Failure** → Implement failover mechanisms and display alternative recommendations.
- **E4: User Output Error** → Validate user output and display error messages.

---

# Slide 9 — Success Metrics & Leading Indicators

Key Insight: Metrics Should Be Relevant and Actionable.

**★ NORTH STAR METRIC:** Average Order Value (AOV) — Average value of orders placed by users (Target Shift: X% to Y%)

## Leading Indicators & Action Plans

| Metric | Target | Impact | Below Target Action |
| :--- | :--- | :--- | :--- |
| Conversion Rate (CR) | >18% | Increase in sales and revenue | Optimize product pages and recommendations |
| Customer Satisfaction (CSAT) | >8% | Increase in customer loyalty and retention | Improve product quality and customer service |
| Average Order Value (AOV) | >15% | Increase in revenue and profitability | Optimize product offerings and pricing |
| Return Rate | +30% | Increase in customer satisfaction and loyalty | Improve product quality and customer service |

---

# Slide 10 — Failure Modes & Mitigations

Key Insight: Failure Mitigations Should Be Proactive and Effective.
*"By implementing these failure mitigations, we can ensure a successful launch and achieve our business objectives."*

- Failure 1: Technical Issues
- Failure 2: User Adoption
- Failure 3: Revenue Shortfall

## Failure Mitigation Matrix

| What could go wrong | Mitigation | Severity |
| :--- | :--- | :--- |
| Technical Issues | Implement failover mechanisms and display alternative recommendations. | **CRIT** |
| User Adoption | Monitor user behavior and adjust product offerings and recommendations. | **HIGH** |
| Revenue Shortfall | Monitor revenue and adjust product offerings and pricing. | **MED** |

## Guardrails to Enforce

- **Average Order Value (AOV) < 4%:** Monitor revenue and adjust product offerings and pricing.
- **Conversion Rate (CR) < 200ms:** Monitor user behavior and adjust product offerings and recommendations.
- **Customer Satisfaction (CSAT) < 1%:** Monitor customer satisfaction and loyalty.
