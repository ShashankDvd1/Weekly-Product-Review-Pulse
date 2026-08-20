import sys
import os
import webbrowser

sys.path.insert(0, 'backend')
from google_auth_oauthlib.flow import InstalledAppFlow
from core.config import GOOGLE_API_SCOPES

secret_file = os.path.join('backend', 'credentials', 'client_secret.json')
if not os.path.exists(secret_file):
    secret_file = os.path.join('credentials', 'client_secret.json')

if not os.path.exists(secret_file):
    print(f"Error: Could not find client_secret.json in backend/credentials/client_secret.json")
    sys.exit(1)

print("Starting Google OAuth login server...")
flow = InstalledAppFlow.from_client_secrets_file(secret_file, GOOGLE_API_SCOPES)
creds = flow.run_local_server(port=0, open_browser=True)

token_path = os.path.join('backend', 'credentials', 'token.json')
os.makedirs(os.path.dirname(token_path), exist_ok=True)
with open(token_path, 'w', encoding='utf-8') as f:
    f.write(creds.to_json())

print("\n" + "="*50)
print("SUCCESS! token.json saved to backend/credentials/token.json")
print("="*50)
