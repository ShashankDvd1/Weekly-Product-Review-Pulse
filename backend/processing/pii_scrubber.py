import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_anonymizer import AnonymizerEngine
    HAS_PRESIDIO = True
except ImportError:
    AnalyzerEngine = None
    NlpEngineProvider = None
    AnonymizerEngine = None
    HAS_PRESIDIO = False

# Fallback Regex Patterns
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

def regex_scrub_pii(text: str) -> str:
    """
    Lightweight regex-based PII scrubber to mask email addresses and phone numbers.
    """
    if not isinstance(text, str) or not text.strip():
        return text
    text = EMAIL_REGEX.sub("<EMAIL_ADDRESS>", text)
    text = PHONE_REGEX.sub("<PHONE_NUMBER>", text)
    return text

# Initialize Presidio if available
if HAS_PRESIDIO:
    try:
        # Configure engine to use the small 12MB spacy model instead of 400MB
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
        })
        nlp_engine = provider.create_engine()

        # Initialize engines
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
        anonymizer = AnonymizerEngine()
        logger.info("Presidio NLP Scrubber initialized successfully.")
    except Exception as e:
        logger.warning(f"Presidio initialization failed ({e}). Falling back to Regex PII Scrubber.")
        HAS_PRESIDIO = False
else:
    logger.info("Presidio not installed. Using high-speed Regex PII Scrubber.")


def scrub_pii_from_text(text: str) -> str:
    """
    Scrubs PII (names, emails, phones) from a single text string.
    """
    if not isinstance(text, str) or not text.strip():
        return text
        
    if not HAS_PRESIDIO:
        return regex_scrub_pii(text)
        
    try:
        # Only scan for the most important PII types (much faster than scanning all)
        results = analyzer.analyze(
            text=text,
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
            language='en'
        )
        
        # Anonymize findings
        anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized_result.text
    except Exception as e:
        logger.warning(f"Presidio scrubbing failed: {e}. Falling back to Regex scrubber.")
        return regex_scrub_pii(text)


def scrub_pii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scrubs PII from the 'content' column of a DataFrame.
    """
    if df.empty or 'content' not in df.columns:
        return df
        
    df['content'] = df['content'].apply(scrub_pii_from_text)
    return df
