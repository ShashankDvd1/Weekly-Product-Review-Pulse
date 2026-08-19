import os
import time
import json
import pandas as pd
from groq import Groq
import tiktoken
from core.config import LLM_MODEL_FAST

# Initialize tokenizer (cl100k_base provides a rough but safe upper bound for Llama3)
encoding = tiktoken.get_encoding("cl100k_base")

# Quota Limits (Adjust based on exact Groq Free Tier limits)
MAX_TPM = 6000  
MAX_RPM = 30    
RPM_DELAY = 60.0 / MAX_RPM

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def initialize_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables")
    return Groq(api_key=api_key)

def extract_insights(centroid_reviews: pd.DataFrame):
    """
    Analyzes centroid reviews using Groq LLM and strict quota management.
    """
    if centroid_reviews.empty:
        return []
        
    client = initialize_groq()
    
    # Smart Batching: Group reviews into chunks that respect the TPM limit
    chunks = []
    current_chunk_text = ""
    current_tokens = 0
    
    for idx, row in centroid_reviews.iterrows():
        review_text = f"Review {idx}:\n{row['content']}\n\n"
        tokens = count_tokens(review_text)
        
        if current_tokens + tokens > (MAX_TPM - 1500):
            if current_chunk_text:
                chunks.append(current_chunk_text)
            current_chunk_text = review_text
            current_tokens = tokens
        else:
            current_chunk_text += review_text
            current_tokens += tokens
            
    if current_chunk_text:
        chunks.append(current_chunk_text)
        
    all_valid_themes = []
    
    # Process each chunk iteratively
    for i, chunk_text in enumerate(chunks):
        if i > 0:
            print(f"Chunk {i+1}: Applying RPM delay of {RPM_DELAY}s...")
            time.sleep(RPM_DELAY)
            
        prompt = f"""
        You are an expert product manager. Analyze the following app reviews and extract the top themes.
        For each theme, provide:
        1. "title": A short title.
        2. "summary": A brief summary.
        3. "quote": Exactly ONE verbatim quote from the text that supports the theme. DO NOT MODIFY THE QUOTE AT ALL. IT MUST BE AN EXACT SUBSTRING.
        4. "action_ideas": A list of actionable ideas to address the feedback.
        5. "team_category": Map the theme to exactly one of the following teams: "Product Team", "Engineer Team", "Art Team", "CEO Team".

        Return the output strictly as a JSON object with a single key "themes" containing a list of these objects.

        Reviews:
        {chunk_text}
        """

        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=LLM_MODEL_FAST,
                temperature=0.1, 
                response_format={"type": "json_object"}
            )
            
            output = response.choices[0].message.content
            parsed_output = json.loads(output)
            themes = parsed_output.get('themes', [])
            
            original_text_lower = chunk_text.lower()
            for theme in themes:
                quote = theme.get("quote", "")
                if quote and quote.lower() in original_text_lower:
                    all_valid_themes.append(theme)
                else:
                    theme["quote"] = "Quote unavailable (failed strict validation)."
                    all_valid_themes.append(theme)
                    
        except Exception as e:
            print(f"LLM Reasoning Failed for chunk {i+1}: {str(e)}")
            if "429" in str(e):
                 raise Exception("Groq Rate Limit Exceeded (RPD/TPD or RPM/TPM). Please wait until quota resets.")
            
    return all_valid_themes
