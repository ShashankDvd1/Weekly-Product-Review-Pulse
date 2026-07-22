"""
Pulse Intelligence — Pydantic Schemas

Defines all data models used across the platform for type safety,
validation, and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────
class DataSource(str, Enum):
    PLAY_STORE = "play_store"
    APP_STORE = "app_store"
    REDDIT = "reddit"


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class BarrierType(str, Enum):
    AWARENESS = "awareness"
    TRUST = "trust"
    HABIT = "habit"
    PRICE_PERCEPTION = "price_perception"
    QUALITY_CONCERN = "quality_concern"
    SELECTION = "selection"
    CONVENIENCE = "convenience"
    DISCOVERY = "discovery"


class ConfidenceLevel(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class JTBDCategory(str, Enum):
    FUNCTIONAL = "functional"
    EMOTIONAL = "emotional"
    SOCIAL = "social"


class ThemeStatus(str, Enum):
    EMERGING = "emerging"
    STEADY = "steady"
    DECLINING = "declining"


class QualityCategory(str, Enum):
    DISCARD = "Discard"
    LOW_SIGNAL = "Low Signal"
    MEDIUM_SIGNAL = "Medium Signal"
    HIGH_SIGNAL = "High Signal"
    GOLD_INSIGHT = "Gold Insight"


# ─────────────────────────────────────────────
# Data Collection Models
# ─────────────────────────────────────────────
class UnifiedSignal(BaseModel):
    """A single consumer signal normalized across all sources."""
    unified_id: str = Field(description="Platform-wide unique ID")
    source: DataSource
    source_id: str = Field(description="Original ID from the source platform")
    app_name: str = Field(description="App mentioned or reviewed")
    content: str = Field(description="Normalized text content")
    title: Optional[str] = Field(default=None, description="Post title (Reddit only)")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Star rating (reviews only)")
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    date: datetime
    author_anon: Optional[str] = Field(default=None, description="Anonymized author")
    categories_mentioned: list[str] = Field(default_factory=list)
    behavioral_signals: list[str] = Field(default_factory=list)
    word_count: int = 0
    url: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

    # Quality Filter fields populated after ingestion
    quality_score: Optional[int] = None
    quality_category: Optional[QualityCategory] = None
    extracted_insights: Optional[dict] = None


class RedditPost(BaseModel):
    """A Reddit post or comment."""
    post_id: str
    subreddit: str
    post_type: str = Field(description="'post' or 'comment'")
    author: str
    title: Optional[str] = None
    content: str
    score: int = 0
    date: datetime
    url: str
    parent_post_id: Optional[str] = None
    num_comments: int = 0


class CollectionResult(BaseModel):
    """Result of a data collection run."""
    source: DataSource
    app_name: str
    signals_collected: int
    signals_after_filtering: int
    collection_timestamp: datetime = Field(default_factory=datetime.utcnow)
    errors: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


# ─────────────────────────────────────────────
# Analysis Output Models
# ─────────────────────────────────────────────
class EvidenceItem(BaseModel):
    """A single piece of evidence supporting an insight."""
    source: DataSource
    text: str
    date: Optional[datetime] = None
    rating: Optional[int] = None
    url: Optional[str] = None
    app_name: Optional[str] = None


class Theme(BaseModel):
    """An AI-detected theme from consumer signals."""
    theme_id: str
    title: str
    summary: str
    category: str = Field(description="Theme category (e.g., UX, Performance, Delivery)")
    sentiment: SentimentLabel
    mention_count: int = 0
    source_distribution: dict = Field(default_factory=dict, description='{"play_store": 15, "reddit": 8}')
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    supporting_quotes: list[str] = Field(default_factory=list)
    supporting_evidence: list[EvidenceItem] = Field(default_factory=list)
    contradicting_evidence: list[EvidenceItem] = Field(default_factory=list)
    apps_affected: list[str] = Field(default_factory=list)
    first_seen: Optional[datetime] = None
    trend: str = "stable"  # rising / stable / declining


class Persona(BaseModel):
    """An AI-generated user persona based on behavioral signals."""
    persona_id: str
    name: str = Field(description="e.g., 'The Routine Buyer'")
    description: str
    shopping_habits: str
    motivations: list[str] = Field(default_factory=list)
    barriers: list[str] = Field(default_factory=list)
    preferred_categories: list[str] = Field(default_factory=list)
    avoided_categories: list[str] = Field(default_factory=list)
    apps_used: list[str] = Field(default_factory=list)
    signal_count: int = 0
    representative_quotes: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class CategoryBarrier(BaseModel):
    """A detected barrier to category exploration."""
    barrier_id: str
    category: str = Field(description="The product category users avoid")
    barrier_type: BarrierType
    description: str
    signal_count: int = 0
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    supporting_evidence: list[EvidenceItem] = Field(default_factory=list)
    recommended_intervention: str = ""
    apps_affected: list[str] = Field(default_factory=list)


class JTBD(BaseModel):
    """A Jobs-To-Be-Done analysis result."""
    jtbd_id: str
    job_statement: str = Field(description="When [situation], I want to [motivation], so I can [outcome]")
    category: JTBDCategory
    current_solution: str = ""
    gaps: list[str] = Field(default_factory=list)
    opportunity_score: float = Field(ge=0.0, le=10.0, default=0.0)
    signal_count: int = 0
    related_persona: Optional[str] = None
    supporting_quotes: list[str] = Field(default_factory=list)


class GrowthOpportunity(BaseModel):
    """An identified growth/product opportunity."""
    opportunity_id: str
    title: str
    description: str
    category: str = Field(description="Feature / UX / Content / Ops / Marketing")
    impact: str = "medium"  # high / medium / low
    effort: str = "medium"  # high / medium / low
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_themes: list[str] = Field(default_factory=list, description="Theme IDs")
    supporting_jtbd: list[str] = Field(default_factory=list, description="JTBD IDs")
    target_persona: Optional[str] = None
    recommended_experiment: str = ""
    apps_affected: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────
# Research Copilot Models
# ─────────────────────────────────────────────
class Hypothesis(BaseModel):
    """A product hypothesis to validate."""
    hypothesis_id: str
    statement: str
    rationale: str
    evidence_count: int = 0
    confidence: float = Field(ge=0.0, le=1.0)
    validation_method: str = ""
    related_barrier: Optional[str] = None
    related_opportunity: Optional[str] = None


class OptimizedInterviewQuestion(BaseModel):
    """A heavily optimized question following The Mom Test."""
    original_question: str
    issues: list[str] = Field(default_factory=list)
    optimized_question: str
    validated_hypothesis: str
    decision_supported: str


class InterviewScriptOutput(BaseModel):
    """The final strict Mom Test validated output."""
    optimized_script: list[OptimizedInterviewQuestion] = Field(default_factory=list)
    removed_questions: list[dict] = Field(default_factory=list)
    missing_questions: list[str] = Field(default_factory=list)
    estimated_duration: str = "15-20 minutes"
    quality_score: int = 0
    recommendations: list[str] = Field(default_factory=list)


class ReviewQualityAssessment(BaseModel):
    """The output of Phase 2 Quality Filter."""
    information_density: int
    specificity: int
    actionability: int
    root_cause_potential: int
    evidence_strength: int
    credibility: int
    final_score: int
    category: QualityCategory
    user_goal: Optional[str] = None
    pain_point: Optional[str] = None
    trigger: Optional[str] = None
    context: Optional[str] = None
    root_cause: Optional[str] = None
    emotional_impact: Optional[str] = None
    current_workaround: Optional[str] = None
    desired_outcome: Optional[str] = None
    feature_mentioned: Optional[str] = None


# ─────────────────────────────────────────────
# Report Models
# ─────────────────────────────────────────────
class ExecutiveSummary(BaseModel):
    """An AI-generated executive summary."""
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    data_coverage: dict = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────
# API Request/Response Models
# ─────────────────────────────────────────────
class CollectRequest(BaseModel):
    """Request to collect data from sources."""
    apps: list[str] = Field(default=["zepto", "blinkit", "swiggy_instamart"])
    sources: list[DataSource] = Field(default=[DataSource.PLAY_STORE, DataSource.APP_STORE, DataSource.REDDIT])
    from_date: str = ""
    to_date: str = ""
    reddit_subreddits: list[str] = Field(default_factory=list)
    reddit_search_terms: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    """Request to run analysis on collected data."""
    apps: list[str] = Field(default=["zepto", "blinkit", "swiggy_instamart"])
    analysis_types: list[str] = Field(
        default=["themes", "sentiment", "behavior", "barriers", "personas", "jtbd", "opportunities"]
    )
    force_recollect: bool = False


class FullPipelineRequest(BaseModel):
    """Request to run the complete collection + analysis pipeline."""
    apps: list[str] = Field(default=["zepto", "blinkit", "swiggy_instamart"])
    from_date: str = ""
    to_date: str = ""
    include_reddit: bool = True
    export_to_sheets: bool = False
    play_store_package: Optional[str] = None
    app_store_id: Optional[str] = None
    reddit_subreddits: list[str] = Field(default_factory=list)
    reddit_search_terms: list[str] = Field(default_factory=list)
    problem_statement: Optional[str] = None


class DashboardOverview(BaseModel):
    """Data for the dashboard overview page."""
    total_signals: int = 0
    signals_by_source: dict = Field(default_factory=dict)
    signals_by_app: dict = Field(default_factory=dict)
    sentiment_summary: dict = Field(default_factory=dict)
    top_themes: list[dict] = Field(default_factory=list)
    top_barriers: list[dict] = Field(default_factory=list)
    top_personas: list[dict] = Field(default_factory=list)
    collection_status: dict = Field(default_factory=dict)
    last_updated: Optional[datetime] = None


# ── Review Board Models ─────────────────────────────────

class ScorecardItem(BaseModel):
    """A scored sub-category in a reviewer scorecard."""
    category: str
    score: float
    reason: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ReviewerScorecard(BaseModel):
    """An evaluator scorecard representing one reviewer profile."""
    reviewer_name: str
    focus: str
    scores: list[ScorecardItem] = Field(default_factory=list)
    overall_reviewer_feedback: str


class BoardEvaluation(BaseModel):
    """Full product board evaluation package."""
    professor_scorecard: ReviewerScorecard
    pm_scorecard: ReviewerScorecard
    founder_scorecard: ReviewerScorecard
    improvement_report: list[str] = Field(default_factory=list)
    visual_assets: dict = Field(default_factory=dict)


class VivaQuestion(BaseModel):
    """A question presented in the interactive viva session."""
    question_id: str
    question: str
    purpose: str
    expected_direction: str
    difficulty: str  # easy, medium, hard


class VivaAnswerEvaluation(BaseModel):
    """Evaluation output for a single user Viva response."""
    score: float
    confidence: str
    communication_score: float
    logic_score: float
    product_thinking_score: float
    business_thinking_score: float
    clarity: str
    suggestions: list[str] = Field(default_factory=list)
    follow_up_question: Optional[str] = None

