import sys
import os

# add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.reasoning.form_generator import generate_survey_structure

payload = {
    "product_name": "Blinkit",
    "problem_statement": "Users stick to repetitive buying habits.",
    "product_description": "Quick commerce.",
    "target_segment": "Existing MAU.",
    "key_features": "Discovery feed.",
    "assumptions": "Lack of trust."
}

try:
    print("Testing generate_survey_structure...")
    res = generate_survey_structure(payload)
    print(res.model_dump())
except Exception as e:
    import traceback
    traceback.print_exc()
