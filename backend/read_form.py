import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reasoning.form_generator import get_google_credentials
from googleapiclient.discovery import build

def main():
    form_id = "1EqlPLfY_9dbv0PA7Zc3d2iHw386T17PceWMFCYz_N1E"
    try:
        creds = get_google_credentials()
        form_service = build('forms', 'v1', credentials=creds)
        form = form_service.forms().get(formId=form_id).execute()
        print(json.dumps(form, indent=2))
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    main()
