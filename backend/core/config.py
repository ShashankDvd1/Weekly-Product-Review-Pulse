"""
Pulse Intelligence — Configuration Management

Centralizes all configuration, API keys, constants, and app-specific settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# API Keys
# ─────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ─────────────────────────────────────────────
# LLM Configuration
# ─────────────────────────────────────────────
LLM_MODEL_FAST = "llama-3.1-8b-instant"                 # Fast, cheap: sentiment, classification
LLM_MODEL_REASONING = "llama-3.3-70b-versatile"     # Deep reasoning: behavior, personas, JTBD
LLM_TEMPERATURE_ANALYTICAL = 0.2                # Low creativity for analysis
LLM_TEMPERATURE_CREATIVE = 0.4                  # Moderate creativity for personas/JTBD

# Groq free tier rate limits
GROQ_MAX_TPM = 40000   # Tokens per minute
GROQ_MAX_RPM = 30     # Requests per minute
GROQ_RPM_DELAY = 60.0 / GROQ_MAX_RPM

# ─────────────────────────────────────────────
# Embedding Configuration
# ─────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ─────────────────────────────────────────────
# ChromaDB Configuration
# ─────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
CHROMA_COLLECTION_SIGNALS = "consumer_signals"
CHROMA_COLLECTION_INSIGHTS = "insights"

# ─────────────────────────────────────────────
# Reddit Configuration
# ─────────────────────────────────────────────
REDDIT_BASE_URL = "https://www.reddit.com"
REDDIT_USER_AGENT = "PulseIntelligence/1.0 (Consumer Intelligence Platform)"
REDDIT_DEFAULT_SUBREDDITS = [
    "india",
    "bangalore",
    "mumbai",
    "delhi",
    "IndianGaming",
    "indiasocial",
]
REDDIT_SEARCH_TERMS_QUICK_COMMERCE = [
    "zepto",
    "blinkit",
    "swiggy instamart",
    "quick commerce",
    "10 minute delivery",
    "instant delivery",
    "grocery delivery app",
    "blinkit makeup",
    "blinkit electronics",
    "blinkit categories",
    "blinkit toys",
    "blinkit skincare"
]
REDDIT_MIN_SCORE = 2          # Minimum upvote score to include
REDDIT_MIN_WORD_COUNT = 10    # Minimum words for a useful comment
REDDIT_MAX_POSTS_PER_QUERY = 25
REDDIT_MAX_COMMENTS_PER_POST = 50
REDDIT_REQUEST_DELAY = 2.0   # Seconds between requests (respect rate limits)

# ─────────────────────────────────────────────
# Quick Commerce App Registry
# ─────────────────────────────────────────────
QUICK_COMMERCE_APPS = {
    "zepto": {
        "name": "Zepto",
        "play_store_package": "com.zeptoconsumerapp",
        "app_store_id": "1575323645",
        "categories": [
            "Grocery", "Fruits & Vegetables", "Dairy & Bread",
            "Snacks & Munchies", "Beauty & Cosmetics", "Home & Kitchen",
            "Electronics", "Baby Care", "Pet Care", "Cleaning Essentials",
            "Health & Wellness", "Stationery", "Toys & Games",
        ],
    },
    "blinkit": {
        "name": "Blinkit",
        "play_store_package": "com.grofers.customerapp",
        "app_store_id": "960335206",
        "categories": [
            "Grocery", "Fruits & Vegetables", "Dairy & Bread",
            "Snacks & Branded Foods", "Beauty & Personal Care", "Home & Kitchen",
            "Electronics & Accessories", "Baby Care", "Pet Supplies",
            "Cleaning & Household", "Health & Hygiene", "Stationery & Books",
            "Toys & Sports",
        ],
    },
    "swiggy_instamart": {
        "name": "Swiggy Instamart",
        "play_store_package": "in.swiggy.android",
        "app_store_id": "989540920",
        "categories": [
            "Grocery", "Fruits & Vegetables", "Dairy & Bread",
            "Snacks & Packaged Food", "Beauty & Personal Care",
            "Home & Kitchen", "Electronics", "Baby Care",
            "Cleaning & Essentials", "Health & Wellness",
        ],
    },
}

# ─────────────────────────────────────────────
# Category Exploration Analysis
# ─────────────────────────────────────────────
CATEGORY_BARRIER_TYPES = [
    "awareness",        # User doesn't know the category exists
    "trust",            # User doesn't trust the platform for this category
    "habit",            # User has a fixed routine / trigger
    "price_perception", # User assumes it's overpriced
    "quality_concern",  # User fears poor quality
    "selection",        # User thinks selection is limited
    "convenience",      # Easier to buy elsewhere
    "discovery",        # Hard to find/browse the category in app
]

# ─────────────────────────────────────────────
# Data Pipeline
# ─────────────────────────────────────────────
MAX_REVIEWS_PER_APP = 200
DEDUP_SIMILARITY_THRESHOLD = 0.85
MIN_CLUSTER_SIZE = 5

# ─────────────────────────────────────────────
# Confidence Scoring
# ─────────────────────────────────────────────
CONFIDENCE_LEVELS = {
    "very_high": {"min_mentions": 50, "min_sources": 3, "score_range": (0.9, 1.0)},
    "high":      {"min_mentions": 20, "min_sources": 2, "score_range": (0.7, 0.89)},
    "medium":    {"min_mentions": 10, "min_sources": 2, "score_range": (0.5, 0.69)},
    "low":       {"min_mentions": 5,  "min_sources": 1, "score_range": (0.3, 0.49)},
    "very_low":  {"min_mentions": 1,  "min_sources": 1, "score_range": (0.0, 0.29)},
}

# ─────────────────────────────────────────────
# Google API Configuration
# ─────────────────────────────────────────────
GOOGLE_API_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/presentations"
]
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials", "service_account.json"),
)
GOOGLE_CLIENT_SECRET_FILE = os.getenv(
    "GOOGLE_CLIENT_SECRET_FILE",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials", "client_secret.json"),
)
GOOGLE_TOKEN_FILE = os.getenv(
    "GOOGLE_TOKEN_FILE",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials", "token.json"),
)
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "1-KqYGsX7eUVmo9ShlXx0i2c0tg8EnbsB")
GOOGLE_SLIDES_TEMPLATE_ID = os.getenv("GOOGLE_SLIDES_TEMPLATE_ID", "1C5pqUxKQ9gsPy_Fs6DA2CW5mCrgNFVluBi4axOWb9E4")

# Sheet names within the workbook
SHEET_NAMES = {
    "play_store": "Play Store Reviews",
    "app_store": "App Store Reviews",
    "reddit": "Reddit",
    "unified": "Unified Dataset",
    "themes": "AI Themes",
    "personas": "Personas",
    "barriers": "Category Barriers",
    "jtbd": "JTBD",
    "opportunities": "Opportunities",
    "weekly_reports": "Weekly Reports",
    "metrics": "Metrics",
    "logs": "Logs",
}
