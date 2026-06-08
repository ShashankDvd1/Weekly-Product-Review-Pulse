from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
import pandas as pd

# Configure engine to use the small 12MB spacy model instead of 400MB
provider = NlpEngineProvider(nlp_configuration={
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
})
nlp_engine = provider.create_engine()

# Initialize engines
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
anonymizer = AnonymizerEngine()

def scrub_pii_from_text(text: str) -> str:
    """
    Scrubs PII (names, emails, phones, etc.) from a single text string.
    """
    if not isinstance(text, str) or not text.strip():
        return text
        
    # Analyze text for PII entities
    results = analyzer.analyze(text=text, entities=[], language='en')
    
    # Anonymize findings
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    
    return anonymized_result.text

def scrub_pii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scrubs PII from the 'content' column of a DataFrame.
    """
    if df.empty or 'content' not in df.columns:
        return df
        
    df['content'] = df['content'].apply(scrub_pii_from_text)
    return df
